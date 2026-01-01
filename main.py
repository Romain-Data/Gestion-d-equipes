import pandas as pd


def generer_planning(noms_ateliers, noms_equipes):
    nb_ateliers = len(noms_ateliers)
    nb_equipes = len(noms_equipes)

    # Vérification de base
    if nb_equipes > 2 * nb_ateliers:
        print("Attention : Trop d'équipes pour le nombre d'ateliers (files d'attente nécessaires).")
        # Pour simplifier, on garde la logique mais certaines équipes devront attendre

    # Séparation des équipes en deux groupes (Intérieur / Extérieur)
    # On complète avec des équipes "Fantômes" si nombre impair
    if nb_equipes % 2 != 0:
        noms_equipes.append("---")
        nb_equipes += 1

    # On coupe la liste en deux
    mid = len(noms_equipes) // 2
    # Si on a plus d'équipes que 2xAteliers, on prend juste les 2xAteliers premiers pour la logique de base
    # (Ici on suppose le cas idéal : nb_equipes = 2 * nb_ateliers ou proche)

    groupe_A = noms_equipes[:mid]  # Tourne dans un sens
    groupe_B = noms_equipes[mid:]  # Tourne dans l'autre

    planning_global = []

    # On prépare les positions initiales
    # Pour que ça marche, il faut aligner les listes sur la taille des ateliers
    # Si on a moins d'équipes que de places, on ajoute des places vides
    while len(groupe_A) < nb_ateliers:
        groupe_A.append("Vide")
        groupe_B.append("Vide")

    # Initialisation des rotations
    # Groupe A : Position 0 à N
    # Groupe B : Position 0 à N

    # decalage_supplementaire = 0
    est_pair = (nb_ateliers % 2 == 0)

    print(f"--- GÉNÉRATION POUR {nb_ateliers} ATELIERS ET {nb_equipes} ÉQUIPES ---\n")

    for tour in range(1, nb_ateliers + 1):
        tour_data = {"Tour": tour}

        # GESTION DU "SAUT" À LA MI-TEMPS (Pour nombre pair d'ateliers)
        # Si on est à la moitié + 1, on décale le groupe B d'un cran supplémentaire
        if est_pair and tour == (nb_ateliers // 2) + 1:
            groupe_B = [groupe_B[-1]] + groupe_B[:-1]  # Rotation extra

        for i in range(nb_ateliers):
            atelier_nom = noms_ateliers[i]

            # L'équipe A sur l'atelier i
            eq_a = groupe_A[i]
            # L'équipe B sur l'atelier i
            eq_b = groupe_B[i]

            matchup = f"{eq_a} vs {eq_b}"

            # Nettoyage si "Vide" ou "---"
            if eq_a in ["Vide", "---"] and eq_b in ["Vide", "---"]:
                matchup = "Libre"
            elif eq_a in ["Vide", "---"]:
                matchup = f"{eq_b} (Seul)"
            elif eq_b in ["Vide", "---"]:
                matchup = f"{eq_a} (Seul)"

            tour_data[atelier_nom] = matchup

        planning_global.append(tour_data)

        # ROTATION POUR LE TOUR SUIVANT
        # Groupe A : Le dernier passe devant (Sens Horaire fictif)
        groupe_A = [groupe_A[-1]] + groupe_A[:-1]

        # Groupe B : Le premier passe derrière (Sens Anti-horaire fictif)
        groupe_B = groupe_B[1:] + [groupe_B[0]]

    return pd.DataFrame(planning_global)


# --- CONFIGURATION ---
# Remplacez les noms ici
mes_ateliers = [f"Atelier {i}" for i in range(1, 11)]  # x1 à x10
mes_equipes = [f"Equipe {i}" for i in range(1, 11)]   # e1 à e20

# --- LANCEMENT ---
df_resultat = generer_planning(mes_ateliers, mes_equipes)

# Affichage propre
# print(df_resultat.to_string(index=False))

# Optionnel : Exporter vers Excel (décommenter la ligne dessous si exécuté en local)
df_resultat.to_csv("mon_planning_equipes.csv", index=False)
