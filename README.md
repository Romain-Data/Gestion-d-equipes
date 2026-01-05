# 🏆 Générateur de Tournoi - Gestion d'Équipes

Une application de bureau **moderne et intuitive** permettant de générer automatiquement des plannings de tournois sportifs ou associatifs (ex : Olympiades). Elle assure que chaque équipe rencontre un maximum d'adversaires différents tout en tournant sur différents ateliers.

## ✨ Fonctionnalités

*   **Génération Automatique** : Algorithme intelligent (basé sur le *Circle Method*) pour des rencontres équilibrées.
*   **Interface Moderne** : UI épurée, responsive et agréable (PyQt6).
*   **Export CSV** : Sauvegardez le planning global en un clic.
*   **Export Excel Avancé** : Générez un fichier Excel multi-onglets avec une feuille par équipe (Détail : Tour, Atelier, Adversaire).
*   **Gestion des cas complexes** : Gère automatiquement les nombres impairs d'équipes (équipes fantômes) et le surplus/manque d'ateliers.

## 🛠 Installation

### Prérequis
*   Python 3.8+
*   pip

### Étapes
1.  Clonez ce dépôt ou téléchargez les fichiers.
2.  Installez les dépendances via le fichier `requirements.txt` :

```bash
pip install -r requirements.txt
```

> **Note** : Les principales dépendances sont `PyQt6` (Interface), `pandas` (Données) et `openpyxl` (Export Excel).

## 🚀 Utilisation

Lancez l'application avec la commande suivante :

```bash
python main.py
```

1.  **Liste des Équipes** : Collez ou tapez la liste de vos équipes dans le panneau de gauche.
2.  **Liste des Ateliers** : Collez ou tapez la liste de vos ateliers (épreuves).
3.  Cliquez sur **"Générer le Planning"**.
4.  Visualisez le résultat dans le tableau central.
5.  Exportez en **CSV** (Global) ou en **Excel** (Par équipe) selon vos besoins.

## 📂 Architecture du Projet

Le projet a été refactorisé pour suivre les principes de *Clean Code*.

```
Gestion-d-equipes/
├── main.py                 # 🟢 Point d'entrée. Contrôleur principal de l'application.
├── create_tournament.py    # 🧠 Cœur logique. Contient l'algorithme de génération et les conversions.
├── requirements.txt        # 📦 Liste des dépendances Python.
│
├── ui/                     # 🎨 Composants graphiques (Widgets)
│   └── widgets.py          #    - CardFrame, InputSection, MainButton
│
└── utils/                  # ⚙️ Utilitaires et Configuration
    └── constants.py        #    - Couleurs, Polices, Paramètres globaux
```

## 🧩 Dépendances

*   **[PyQt6](https://pypi.org/project/PyQt6/)** : Framework GUI pour l'interface utilisateur.
*   **[pandas](https://pandas.pydata.org/)** : Manipulation puissante des données (DataFrames).
*   **[openpyxl](https://openpyxl.readthedocs.io/)** : Moteur d'écriture pour les fichiers Excel (.xlsx).

---
*Projet développé pour optimiser la gestion logistique des tournois.*
