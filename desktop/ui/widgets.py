from PyQt6.QtWidgets import (QFrame, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QTextEdit, QPushButton,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from typing import Optional

from desktop.utils.constants import CARD_RADIUS, FONT_FAMILY


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
        # Désactiver l'ombre pour éviter que le texte du titre ne soit flou
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
