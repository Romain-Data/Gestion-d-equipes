import sys
from create_tournament import generer_planning_algo
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt

# --- L'INTERFACE GRAPHIQUE (GUI) ---

# --- L'INTERFACE GRAPHIQUE (GUI) ---


class TournoiApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Générateur de Tournoi par Équipes")
        self.resize(1000, 700)
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout principal (Vertical)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # --- Zone des entrées (Inputs) ---
        input_layout = QHBoxLayout()
        
        # Zone Équipes
        team_layout = QVBoxLayout()
        team_label = QLabel("Liste des Équipes (une par ligne) :")
        team_label.setStyleSheet("font-weight: bold;")
        self.team_input = QTextEdit()
        # Valeurs par défaut pour tester
        self.team_input.setPlainText("\n".join([f"Equipe {i}" for i in range(1, 21)]))
        team_layout.addWidget(team_label)
        team_layout.addWidget(self.team_input)
        
        # Zone Ateliers
        atelier_layout = QVBoxLayout()
        atelier_label = QLabel("Liste des Ateliers (un par ligne) :")
        atelier_label.setStyleSheet("font-weight: bold;")
        self.atelier_input = QTextEdit()
        # Valeurs par défaut
        self.atelier_input.setPlainText("\n".join([f"Atelier {i}" for i in range(1, 11)]))
        atelier_layout.addWidget(atelier_label)
        atelier_layout.addWidget(self.atelier_input)
        
        input_layout.addLayout(team_layout)
        input_layout.addLayout(atelier_layout)
        
        layout.addLayout(input_layout)
        
        # --- Bouton Générer ---
        self.btn_generer = QPushButton("Générer le Planning")
        self.btn_generer.setStyleSheet("font-size: 14px; padding: 10px; background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_generer.clicked.connect(self.lancer_generation)
        layout.addWidget(self.btn_generer)
        
        # --- Tableau de résultats ---
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        # --- Bouton Export ---
        self.btn_export = QPushButton("Exporter en Excel (CSV)")
        self.btn_export.clicked.connect(self.exporter_csv)
        self.btn_export.setEnabled(False) # Désactivé tant qu'il n'y a pas de résultat
        layout.addWidget(self.btn_export)
        
        # Variable pour stocker le dataframe
        self.df_resultat = None

    def lancer_generation(self):
        # 1. Récupération des données
        raw_teams = self.team_input.toPlainText().strip().split('\n')
        raw_ateliers = self.atelier_input.toPlainText().strip().split('\n')
        
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

# --- POINT D'ENTRÉE ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TournoiApp()
    window.show()
    sys.exit(app.exec())