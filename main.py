import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QTextEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
                             QHeaderView, QFrame, QGraphicsDropShadowEffect)


import pandas as pd
from typing import Optional

from create_tournament import generer_planning_algo, conversions_par_equipe

# --- CONFIGURATION DE L'APPLICATION ---
BACKGROUND_COLOR = "#F5F7FA"
CARD_RADIUS = "15px"
# Correction : Utiliser la police système Mac en premier pour éviter le warning "Populating font family aliases".
# Le warning se produit car "Segoe UI" n'est pas trouvé sur Mac.
FONT_FAMILY = '".AppleSystemUIFont", "Helvetica Neue", "Arial", sans-serif'


class CardFrame(QFrame):
    """
    Une carte arrondie générique avec un ombrage et un dégradé optionnel.
    """
    def __init__(
        self,
        gradient: Optional[str] = None,
        bg_color: str = "white",
        parent: Optional[QWidget] = None,
        with_shadow: bool = True
    ):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # Style
        style = f"border-radius: {CARD_RADIUS};"
        if gradient:
            style += f"background: {gradient};"
        else:
            style += f"background-color: {bg_color}; border: 1px solid #E2E8F0;"
        self.setStyleSheet(style)

        # Ombre
        if with_shadow:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0, 0, 0, 30))
            self.setGraphicsEffect(shadow)


class InputSection(CardFrame):
    """
    Carte spécifique pour les saisies (Équipes ou Ateliers) avec icône, titre et zone de texte.
    """
    def __init__(
        self,
        title: str,
        placeholder: str,
        gradient: str,
        icon_emoji: str = "📝",
        default_text: str = "",
        parent: Optional[QWidget] = None
    ):
        super().__init__(gradient=gradient, parent=parent, with_shadow=False)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        self.setLayout(layout)

        # En-tête (Icône + Titre)
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon_emoji)
        icon_label.setStyleSheet("font-size: 20px; background: transparent; border: none;")

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #333; background: transparent; border: none;"
            )

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Zone de saisie (Boîte blanche à l'intérieur de la carte dégradée)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(placeholder)
        if default_text:
            self.text_input.setPlainText(default_text)

        # Partie Style : Saisie interne blanche avec coins arrondis
        # NOTE : FONT_FAMILY est maintenant insérée directement (elle contient ses propres guillemets pour les familles)
        self.text_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-family: {FONT_FAMILY};
                font-size: 14px;
                color: #333;
            }}
        """)

        layout.addWidget(self.text_input)

    def get_text(self) -> str:
        """Récupère le texte brut de la zone de saisie."""
        return self.text_input.toPlainText()


class MainButton(QPushButton):
    """
    Bouton noir solide en forme de pilule.
    """
    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        # NOTE : FONT_FAMILY insérée directement
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #000000;
                color: white;
                border-radius: 25px; /* Forme de pilule (hauteur/2) */
                font-family: {FONT_FAMILY};
                font-size: 14px;
                font-weight: bold;
                padding-left: 20px;
                padding-right: 20px;
            }}
            QPushButton:hover {{
                background-color: #333333;
            }}
            QPushButton:pressed {{
                background-color: #555555;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #888888;
            }}
        """)


class TournamentApp(QMainWindow):
    """
    Application principale générant les plannings de tournoi.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Générateur de Tournoi")
        self.resize(1100, 750)

        # Style de la fenêtre principale
        # NOTE : FONT_FAMILY insérée directement
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BACKGROUND_COLOR};
            }}
            QLabel {{
                font-family: {FONT_FAMILY};
            }}
            /* Scrollbar Moderne */
            QScrollBar:vertical {{
                border: none;
                background: #F1F5F9;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: #CBD5E1;
                min-height: 30px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #94A3B8;
            }}
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        # Widget Central
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout Principal (Horizontal : Panneau Gauche 1/3, Panneau Droit 2/3)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)
        main_widget.setLayout(main_layout)

        # --- PANNEAU GAUCHE (Saisies) ---
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)

        # 1. Étiquette Titre (Optionnelle, correspond à la maquette 'Générateur de Tournoi')
        app_title = QLabel("Générateur de Tournoi")
        app_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #000; margin-bottom: 10px;")
        left_panel.addWidget(app_title)

        # 2. Carte Équipes (Dégradé : Jaune -> Bleuâtre)
        # Approximation simple en gradient linéaire de l'image
        teams_gradient = "qlinear-gradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #FDE68A, stop:1 #BAE6FD)"
        # CORRECTION : Suppression du double échappement sur les retours à la ligne
        default_teams = "\n".join([f"Equipe {i}" for i in range(1, 21)])
        self.teams_card = InputSection(
            "Liste des Équipes",
            "Collez les équipes ici...",
            teams_gradient,
            "",
            default_teams
        )
        left_panel.addWidget(self.teams_card)

        # 3. Carte Ateliers (Dégradé : Verdâtre -> Bleuâtre)
        ateliers_gradient = "qlinear-gradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #D1FAE5, stop:1 #BFDBFE)"
        # CORRECTION : Suppression du double échappement sur les retours à la ligne
        default_ateliers = "\n".join([f"Atelier {i}" for i in range(1, 11)])
        self.ateliers_card = InputSection(
            "Liste des Ateliers",
            "Collez les ateliers ici...",
            ateliers_gradient,
            "",
            default_ateliers
        )
        left_panel.addWidget(self.ateliers_card)

        # Espaceur
        left_panel.addStretch()

        # 4. Bouton Générer
        self.btn_generer = MainButton("Générer le Planning")
        self.btn_generer.clicked.connect(self.lancer_generation)
        left_panel.addWidget(self.btn_generer)

        # Ajout du Panneau Gauche au Layout Principal
        # Widget conteneur pour contrôler la largeur
        left_container = QWidget()
        left_container.setLayout(left_panel)
        left_container.setFixedWidth(350)  # Largeur fixe pour l'aspect barre latérale
        main_layout.addWidget(left_container)

        # --- PANNEAU DROIT (Résultats) ---
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)
        right_panel.setContentsMargins(0, 30, 0, 0)  # Alignement haut avec les cartes

        # 1. Carte Résultats (Blanche)
        self.results_card = CardFrame(bg_color="white")
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(20, 20, 20, 20)
        self.results_card.setLayout(results_layout)

        # Tableau
        self.table = QTableWidget()
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                gridline-color: #EEE;
                font-family: {FONT_FAMILY};
                font-size: 13px;
                selection-background-color: #E0F2FE;
                selection-color: #000;
            }}
            QHeaderView::section {{
                background-color: #F8FAFC;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #64748B;
                font-size: 12px;
                text-transform: uppercase;
            }}
        """)
        self.table.setShowGrid(False)  # Aspect épuré
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        results_layout.addWidget(self.table)

        right_panel.addWidget(self.results_card)

        # 2. Zone des Boutons d'Export
        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)

        self.btn_export = MainButton("Exporter en Excel (CSV)")
        self.btn_export.clicked.connect(self.exporter_csv)
        self.btn_export.setEnabled(False)
        export_layout.addWidget(self.btn_export)

        self.btn_export_teams = MainButton("Exporter Planning Équipes (Excel)")
        self.btn_export_teams.clicked.connect(self.exporter_excel_equipes)
        self.btn_export_teams.setEnabled(False)

        # Ardoise Foncée
        self.btn_export_teams.setStyleSheet(self.btn_export.styleSheet().replace("#000000", "#1E293B"))
        export_layout.addWidget(self.btn_export_teams)

        right_panel.addLayout(export_layout)

        main_layout.addLayout(right_panel, stretch=2)  # Prendre l'espace restant

        self.df_resultat: Optional[pd.DataFrame] = None

    def lancer_generation(self):
        """Récupère les entrées, lance l'algorithme et affiche les résultats."""
        # 1. Récupération des données
        raw_teams = self.teams_card.get_text().strip().split('\n')
        raw_ateliers = self.ateliers_card.get_text().strip().split('\n')

        # Nettoyage des lignes vides
        teams = [t.strip() for t in raw_teams if t.strip()]
        ateliers = [a.strip() for a in raw_ateliers if a.strip()]

        if not teams or not ateliers:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer au moins une équipe et un atelier.")
            return

        # 2. Appel de l'algo
        try:
            self.df_resultat = generer_planning_algo(ateliers, teams)
            self.afficher_tableau()
            self.btn_export.setEnabled(True)
            self.btn_export_teams.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

    def afficher_tableau(self):
        """Remplit le QTableWidget avec les données du DataFrame."""
        if self.df_resultat is None:
            return

        df = self.df_resultat

        # Configuration du tableau
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns)

        # Remplissage
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                valeur = str(df.iloc[i, j])
                item = QTableWidgetItem(valeur)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

        # Ajustement esthétique
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Ajustement CSS pour les couleurs alternées si setAlternatingRowColors ne choisit pas les bonnes
        self.table.setStyleSheet(self.table.styleSheet() + """
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F1F5F9;
            }
        """)

    def exporter_csv(self):
        """Exporte le tableau global au format CSV."""
        if self.df_resultat is None:
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier", "", "Fichiers CSV (*.csv)")

        if filename:
            try:
                self.df_resultat.to_csv(filename, index=False, sep=';', encoding='utf-8-sig')
                QMessageBox.information(self, "Succès", "Fichier enregistré avec succès !")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer le fichier : {str(e)}")

    def exporter_excel_equipes(self):
        """Exporte un fichier Excel avec un onglet par équipe."""
        if self.df_resultat is None:
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Enregistrer les plannings", "", "Fichiers Excel (*.xlsx)")

        if filename:
            try:
                # 1. Conversion
                plannings = conversions_par_equipe(self.df_resultat)

                # 2. Ecriture Excel multi-feuilles
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    for equipe, df_eq in plannings.items():
                        # Nom de feuille propre (Excel limite à 31 chars)
                        sheet_name = equipe[:30].replace(":", "").replace("/", "")
                        df_eq.to_excel(writer, sheet_name=sheet_name, index=False)

                QMessageBox.information(self, "Succès", "Fichier Excel généré avec succès !")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'enregister le fichier : {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TournamentApp()
    window.show()
    sys.exit(app.exec())
