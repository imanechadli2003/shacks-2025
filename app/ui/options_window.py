import json
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame, QSpacerItem, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import Qt

SETTINGS_PATH = "settings.json"

class OptionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shacks 2025 - Options")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.resize(500, 400)
        
        # Style moderne
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel#title {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#subtitle {
                color: #7f8c8d;
                font-size: 12px;
            }
            QLabel#section {
                color: #34495e;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                color: #000000;
                font-size: 13px;
                min-height: 25px;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
            QComboBox:focus {
                border: 2px solid #2980b9;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #000000;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QFrame#separator {
                background-color: #bdc3c7;
            }
            QLabel#status {
                color: #27ae60;
                font-size: 12px;
                font-style: italic;
                padding: 5px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # En-tête avec icône et titre
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap("assets/icon.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setFixedSize(64, 64)
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        title_label = QLabel("Shacks 2025")
        title_label.setObjectName("title")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Système de sécurité intelligent")
        subtitle_label.setObjectName("subtitle")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)

        # Séparateur
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(2)
        main_layout.addWidget(separator)

        # Section Options
        options_layout = QVBoxLayout()
        options_layout.setSpacing(15)
        
        security_label = QLabel("⚙️ Type de sécurité")
        security_label.setObjectName("section")
        options_layout.addWidget(security_label)

        security_desc = QLabel("Choisissez le mode de réaction en cas de détection d'intrus :")
        security_desc.setWordWrap(True)
        security_desc.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 5px;")
        options_layout.addWidget(security_desc)

        self.security_dropdown = QComboBox()
        self.security_dropdown.addItems(["Fermer auto", "Logger"])
        options_layout.addWidget(self.security_dropdown)

        self.current_label = QLabel()
        self.current_label.setObjectName("status")
        options_layout.addWidget(self.current_label)

        main_layout.addLayout(options_layout)
        
        # Espaceur pour pousser le contenu vers le haut
        main_layout.addStretch()

        self.setLayout(main_layout)

        # Charger les paramètres
        self.settings = self.load_settings()
        self.security_dropdown.setCurrentText(self.settings.get("security_mode", "Fermer auto"))
        self.current_label.setText(f"✓ Mode actif : {self.security_dropdown.currentText()}")

        self.security_dropdown.currentTextChanged.connect(self.on_change)

    def on_change(self, text):
        self.current_label.setText(f"✓ Mode actif : {text}")
        self.settings["security_mode"] = text
        self.save_settings()

    def load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_settings(self):
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2)
