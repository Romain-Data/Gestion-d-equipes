import pandas as pd
from typing import List, Dict, Any


def generer_planning_algo(noms_ateliers: List[str], noms_equipes: List[str]) -> pd.DataFrame:
    """
    Génère un planning de tournoi sous forme de DataFrame.

    Chaque équipe rencontrera toutes les autres (comporte une logique Round-Robin).
    Les matchs sont répartis sur les ateliers disponibles.

    Args:
        noms_ateliers (List[str]): La liste des noms des ateliers.
        noms_equipes (List[str]): La liste des noms des équipes.

    Returns:
        pd.DataFrame: Un DataFrame contenant le planning complet (Tours, Ateliers, etc.).
    """
    # 1. Préparation des équipes (Nombre pair nécessaire)
    equipes = noms_equipes.copy()
    if len(equipes) % 2 != 0:
        equipes.append("FANTOME")

    nb_equipes = len(equipes)
    nb_matchs_par_tour = nb_equipes // 2
    nb_ateliers = len(noms_ateliers)

    # Le cycle des opposants dure N-1 tours (Round Robin classique)
    cycle_opposants = nb_equipes - 1

    # La grille de rotation doit être assez grande pour contenir :
    # - Tous les matchs possibles simultanés (nb_matchs_par_tour)
    # - Tous les ateliers (nb_ateliers)
    # Ceci définit la "largeur" de notre fenêtre glissante
    taille_grille = max(nb_matchs_par_tour, nb_ateliers)

    # Nombre de tours à générer
    # On prend le max entre le cycle des opposants (pour voir tout le monde)
    # et la taille de la grille (pour passer par tous les ateliers/slots)
    nb_tours = max(cycle_opposants, taille_grille)

    planning_global = []

    # Indices fixes pour la méthode du cercle
    # L'équipe à l'index 0 est fixe, les autres tournent
    # indices = [0, 1, 2, ..., N-1]
    fixed_index = 0
    rotating_indices = list(range(1, nb_equipes))

    for tour in range(nb_tours):
        tour_data: Dict[str, Any] = {"Tour": tour + 1}

        # 2. Génération des matchs (Logique Opposants - Circle Method)
        # On utilise le modulo cycle_opposants pour répéter les rencontres si besoin
        step = tour % cycle_opposants

        # Rotation de la liste d'indices
        current_rotating = rotating_indices[step:] + rotating_indices[:step]
        current_indices = [fixed_index] + current_rotating

        # Formation des paires "logiques"
        paires_du_tour = []
        for i in range(nb_matchs_par_tour):
            idx_a = current_indices[i]
            idx_b = current_indices[nb_equipes - 1 - i]
            paires_du_tour.append((equipes[idx_a], equipes[idx_b]))

        # 2.5 Séparation des matchs réels et des pauses fantômes
        matchs_reels = []
        equipes_en_pause = []

        for eq_a, eq_b in paires_du_tour:
            est_fantome_a = (eq_a == "FANTOME")
            est_fantome_b = (eq_b == "FANTOME")

            if est_fantome_a and est_fantome_b:
                continue  # Ignore (double fantome possible si impair + vide?)
            elif est_fantome_a:
                equipes_en_pause.append(eq_b)
            elif est_fantome_b:
                equipes_en_pause.append(eq_a)
            else:
                matchs_reels.append((eq_a, eq_b))

        # 3. Assignation aux Ateliers par Batchs
        # On calcule combien de lots de matchs on peut faire entrer dans les ateliers
        # ex: 10 ateliers, 5 matchs => 2 lots (A1-A5, A6-A10)

        # Nombre de matchs réels joués simultanément (capacité d'un batch)
        # Note: 'matchs_reels' varie en taille si des équipes sont FANTOME,
        # mais la capacité théorique max est (nb_equipes // 2)
        matchs_simultanes_max = nb_matchs_par_tour  # Capacité théorique (ex: 5 pour 10 équipes)

        # Nombre de batches possibles
        if matchs_simultanes_max > 0:
            nb_batches = len(noms_ateliers) // matchs_simultanes_max
        else:
            nb_batches = 1  # Cas dégénéré

        indices_matchs_assignes = set()

        # Vérifie si nous avons un nombre impair d'équipes (impliquant l'existence d'un 'FANTOME').
        # Dans ce cas, chaque tour a 1 match de moins que le max théorique.
        # Si nous avons aussi plusieurs batches, le batching strict laissera des trous.
        # Bascule sur le SLIDING WINDOW dans ce cas pour tourner l'usage de tous les ateliers.
        # Note : si on a ajouté FANTOME, len(equipes) est pair.
        force_sliding = False
        if nb_batches > 1 and "FANTOME" in equipes:
            force_sliding = True

        # Si on n'a assez d'ateliers que pour 1 seul batch (ou moins), on reste sur le mode classique/glissant OU forcé
        if nb_batches <= 1 or force_sliding:
            # Mode SLIDING WINDOW (Restauré pour garantir l'usage de tous les ateliers si surplus)
            # ex: 12 équipes (6 matchs) / 10 ateliers.
            # On veut que les matchs se décalent sur les ateliers 1-10.

            nb_slots_utiles = len(matchs_reels)
            current_grid_size = max(nb_slots_utiles, len(noms_ateliers))

            for k, atelier_nom in enumerate(noms_ateliers):
                # Formule de rotation de la grille
                slot_source = (k - tour) % current_grid_size

                if slot_source < nb_slots_utiles:
                    # Il y a un match réel pour ce slot virtuel
                    eq_a, eq_b = matchs_reels[slot_source]
                    tour_data[atelier_nom] = f"{eq_a} vs {eq_b}"
                    indices_matchs_assignes.add(slot_source)
                else:
                    # Slot vide
                    tour_data[atelier_nom] = "-"

            # Pause calc pour Sliding: quels index de matchs_reels n'ont pas été servis
            for i in range(nb_slots_utiles):
                if i not in indices_matchs_assignes:
                    m_a, m_b = matchs_reels[i]
                    equipes_en_pause.append(m_a)
                    equipes_en_pause.append(m_b)

        else:
            # Mode BATCH (Strict)
            import math
            rounds_per_batch = math.ceil(nb_tours / nb_batches)

            # Quel batch pour ce tour ? (0-indexed)
            current_batch_index = tour // rounds_per_batch
            if current_batch_index >= nb_batches:
                current_batch_index = nb_batches - 1

            # Offset d'atelier
            atelier_start_index = current_batch_index * matchs_simultanes_max

            # Rotation locale des matchs
            shift = tour % len(matchs_reels)
            matchs_ordonnes = matchs_reels[shift:] + matchs_reels[:shift]

            for k, atelier_nom in enumerate(noms_ateliers):
                match_index_relatif = k - atelier_start_index

                if 0 <= match_index_relatif < len(matchs_ordonnes):
                    eq_a, eq_b = matchs_ordonnes[match_index_relatif]
                    tour_data[atelier_nom] = f"{eq_a} vs {eq_b}"
                    indices_matchs_assignes.add(match_index_relatif)
                else:
                    tour_data[atelier_nom] = "-"

            # Pause calc pour Batch: quels index de matchs_ordonnes n'ont pas été servis
            for i in range(len(matchs_ordonnes)):
                if i not in indices_matchs_assignes:
                    m_a, m_b = matchs_ordonnes[i]
                    equipes_en_pause.append(m_a)
                    equipes_en_pause.append(m_b)

        tour_data["Equipes en pause"] = ", ".join(sorted(equipes_en_pause))

        planning_global.append(tour_data)

    return pd.DataFrame(planning_global)


def conversions_par_equipe(df_global: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Transforme le DataFrame global (Tours x Ateliers) en un dictionnaire de plannings par équipe.

    Args:
        df_global (pd.DataFrame): Le planning global généré.

    Returns:
        Dict[str, pd.DataFrame]: Un dictionnaire { "NomEquipe": DataFrame(Tour, Atelier, Adversaire) }.
    """
    plannings_equipes = {}

    # On récupère toutes les équipes présentes dans le DataFrame
    # (en parsant les cellules "Equipe A vs Equipe B")
    # Une façon simple est de parcourir tout le tableau.

    # Structure temporaire : { "NomEquipe": [ {"Tour": 1, "Atelier": "A1", "Adversaire": "B"} ... ] }
    records_equipes: Dict[str, List[Dict[str, Any]]] = {}

    for index, row in df_global.iterrows():
        tour_num = row['Tour']

        # Pour chaque colonne (sauf 'Tour' et 'Equipes en pause')
        for col in df_global.columns:
            if col in ["Tour", "Equipes en pause"]:
                continue

            cell_value = row[col]
            if not isinstance(cell_value, str):
                continue

            if " vs " in cell_value:
                # C'est un match : "Equipe A vs Equipe B"
                parts = cell_value.split(" vs ")
                if len(parts) == 2:
                    eq_a = parts[0].strip()
                    eq_b = parts[1].strip()

                    # Enregistrement pour A
                    if eq_a not in records_equipes:
                        records_equipes[eq_a] = []
                    records_equipes[eq_a].append({
                        "Tour": tour_num,
                        "Atelier": col,
                        "Adversaire": eq_b
                    })

                    # Enregistrement pour B
                    if eq_b not in records_equipes:
                        records_equipes[eq_b] = []
                    records_equipes[eq_b].append({
                        "Tour": tour_num,
                        "Atelier": col,
                        "Adversaire": eq_a
                    })
            elif cell_value != "-" and cell_value.strip() != "":
                # Cas rare ou format différent ? Pour l'instant on ignore les pauses ou autre format
                pass

    # Conversion en DataFrames
    for eq, records in records_equipes.items():
        if eq != "FANTOME":  # On ignore le fantôme
            df_eq = pd.DataFrame(records)
            # Tri par tour pour être propre
            if not df_eq.empty:
                df_eq = df_eq.sort_values(by="Tour")
            plannings_equipes[eq] = df_eq

    return plannings_equipes
