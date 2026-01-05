import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QTextEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
                             QHeaderView, QFrame, QGraphicsDropShadowEffect)


from create_tournament import generer_planning_algo

# --- APP CONFIGURATION ---
BACKGROUND_COLOR = "#F5F7FA"
CARD_RADIUS = "15px"
# Fix: Use Mac-native font first to avoid "Populating font family aliases" warning.
# The warning happens because "Segoe UI" is not found on Mac.
FONT_FAMILY = '".AppleSystemUIFont", "Helvetica Neue", "Arial", sans-serif'


class CardFrame(QFrame):
    """A generic rounded card with a shadow and optional gradient."""
    def __init__(self, gradient=None, bg_color="white", parent=None, with_shadow=True):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # Style
        style = f"border-radius: {CARD_RADIUS};"
        if gradient:
            style += f"background: {gradient};"
        else:
            style += f"background-color: {bg_color}; border: 1px solid #E2E8F0;"
        self.setStyleSheet(style)

        # Shadow
        if with_shadow:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QColor(0, 0, 0, 30))
            self.setGraphicsEffect(shadow)


class InputSection(CardFrame):
    """Specific card for inputs (Teams or Ateliers) with icon, title, and text area."""
    def __init__(self, title, placeholder, gradient, icon_emoji="📝", default_text="", parent=None):
        # Disable shadow to prevent text blurring on titles
        super().__init__(gradient=gradient, parent=parent, with_shadow=False)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Header (Icon + Title)
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

        # Input Area (White box inside the gradient card)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(placeholder)
        if default_text:
            self.text_input.setPlainText(default_text)

        # Style part: Internal white input with rounded corners
        # NOTE: FONT_FAMILY is now inserted directly (it contains its own quotes for families)
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

    def get_text(self):
        return self.text_input.toPlainText()


class MainButton(QPushButton):
    """Pill-shaped solid black button."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        # NOTE: FONT_FAMILY inserted directly
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #000000;
                color: white;
                border-radius: 25px; /* Pill shape (height/2) */
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
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Générateur de Tournoi")
        self.resize(1100, 750)

        # Main Window Styling
        # NOTE: FONT_FAMILY inserted directly
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BACKGROUND_COLOR};
            }}
            QLabel {{
                font-family: {FONT_FAMILY};
            }}
            /* Modern Scrollbar */
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

        # Central Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main Layout (Horizontal: Left Panel 1/3, Right Panel 2/3)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)
        main_widget.setLayout(main_layout)

        # --- LEFT PANEL (Inputs) ---
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)

        # 1. Title Label (Optional, matches mock 'Générateur de Tournoi')
        app_title = QLabel("Générateur de Tournoi")
        app_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #000; margin-bottom: 10px;")
        left_panel.addWidget(app_title)

        # 2. Teams Card (Gradient: Yellow -> Blueish)
        # Using simple linear-gradient approximation of the image
        teams_gradient = "qlinear-gradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #FDE68A, stop:1 #BAE6FD)"
        # FIX: Remove double escaping on newlines
        default_teams = "\n".join([f"Equipe {i}" for i in range(1, 21)])
        self.teams_card = InputSection(
            "Liste des Équipes",
            "Collez les équipes ici...",
            teams_gradient,
            "",
            default_teams
        )
        left_panel.addWidget(self.teams_card)

        # 3. Ateliers Card (Gradient: Greenish -> Blueish)
        ateliers_gradient = "qlinear-gradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #D1FAE5, stop:1 #BFDBFE)"
        # FIX: Remove double escaping on newlines
        default_ateliers = "\n".join([f"Atelier {i}" for i in range(1, 11)])
        self.ateliers_card = InputSection(
            "Liste des Ateliers",
            "Collez les ateliers ici...",
            ateliers_gradient,
            "",
            default_ateliers
        )
        left_panel.addWidget(self.ateliers_card)

        # Spacer
        left_panel.addStretch()

        # 4. Generate Button
        self.btn_generer = MainButton("Générer le Planning")
        self.btn_generer.clicked.connect(self.lancer_generation)
        left_panel.addWidget(self.btn_generer)

        # Add Left Panel to Main Layout
        # Wrapper widget to control width
        left_container = QWidget()
        left_container.setLayout(left_panel)
        left_container.setFixedWidth(350)  # Fixed width for left sidebar look
        main_layout.addWidget(left_container)

        # --- RIGHT PANEL (Results) ---
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)
        right_panel.setContentsMargins(0, 30, 0, 0)  # Align top with cards

        # 1. Results Card (White)
        self.results_card = CardFrame(bg_color="white")
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(20, 20, 20, 20)
        self.results_card.setLayout(results_layout)

        # Table
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
        self.table.setShowGrid(False)  # Clean look
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        results_layout.addWidget(self.table)

        right_panel.addWidget(self.results_card)

        # 2. Export Button
        self.btn_export = MainButton("Exporter en Excel (CSV)")
        self.btn_export.clicked.connect(self.exporter_csv)
        self.btn_export.setEnabled(False)
        # Alignment for export button (Right aligned or full width? Mock shows bottom right or center. Let's do Full)
        right_panel.addWidget(self.btn_export)

        main_layout.addLayout(right_panel, stretch=2)  # Take remaining space

        self.df_resultat = None

    def lancer_generation(self):
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
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

    def afficher_tableau(self):
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

        # Alternating row colors CSS adjustment needed if setAlternatingRowColors doesn't pick nice ones
        self.table.setStyleSheet(self.table.styleSheet() + """
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F1F5F9;
            }
        """)

    def exporter_csv(self):
        if self.df_resultat is None:
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier", "", "Fichiers CSV (*.csv)")

        if filename:
            try:
                self.df_resultat.to_csv(filename, index=False, sep=';', encoding='utf-8-sig')
                QMessageBox.information(self, "Succès", "Fichier enregistré avec succès !")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer le fichier : {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TournamentApp()
    window.show()
    sys.exit(app.exec())
