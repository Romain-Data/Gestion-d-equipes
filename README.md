# 🏆 Générateur de Tournoi - Gestion d'Équipes

Une application **hybride (Bureau & Web)** moderne et intuitive permettant de générer automatiquement des plannings de tournois sportifs ou associatifs. Elle assure que chaque équipe rencontre un maximum d'adversaires différents tout en tournant sur différents ateliers.

## ✨ Fonctionnalités

*   **Génération Automatique** : Algorithme intelligent (basé sur le *Circle Method*) pour des rencontres équilibrées.
*   **Deux Interfaces** :
    *   🖥️ **Desktop** : Application native fluide avec PyQt6.
    *   🌐 **Web** : Interface légère et accessible via navigateur (FastAPI + Tailwind).
*   **Exports Complets** :
    *   **CSV** : Planning global.
    *   **Excel** : Fichier multi-onglets avec une feuille par équipe (Détail : Tour, Atelier, Adversaire).
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

## 🚀 Utilisation

### 🖥️ Mode Bureau (Desktop)
Lancez l'application native :

```bash
python -m desktop.main
```

### 🌐 Mode Web
Lancez le serveur local :

```bash
uvicorn web.main:app --reload
```
Puis ouvrez votre navigateur à l'adresse : [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Fonctionnement général
1.  **Saisie** : Entrez la liste des équipes et des ateliers.
2.  **Génération** : Cliquez sur le bouton "Générer".
3.  **Export** : Téléchargez les résultats en CSV ou Excel.

## 📂 Architecture du Projet

Le projet respecte une architecture modulaire et *Clean Code*.

```
Gestion-d-equipes/
├── core/                   # 🧠 Cœur logique (Indépendant de l'interface)
│   └── algo.py             #    - Algorithme de génération et conversions
│
├── desktop/                # 🖥️ Application Bureau (PyQt6)
│   ├── main.py             #    - Point d'entrée Desktop
│   ├── ui/                 #    - Widgets graphiques
│   └── utils/              #    - Constantes
│
├── web/                    # 🌐 Application Web (FastAPI)
│   ├── main.py             #    - Backend API
│   └── static/             #    - Frontend (HTML/JS/Tailwind)
│       └── index.html
│
└── requirements.txt        # 📦 Liste des dépendances
```

## 🧩 Dépendances Majeures

*   **[PyQt6](https://pypi.org/project/PyQt6/)** : Interface Bureau.
*   **[FastAPI](https://fastapi.tiangolo.com/)** : Framework API Web.
*   **[pandas](https://pandas.pydata.org/)** : Manipulation des données.
*   **[openpyxl](https://openpyxl.readthedocs.io/)** : Export Excel.

---
*Projet développé pour optimiser la gestion logistique des tournois.*
