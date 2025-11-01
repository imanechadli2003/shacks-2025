import json
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PySide6.QtGui import QIcon, QPixmap

SETTINGS_PATH = "settings.json"

class OptionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.resize(300, 200)

        layout = QVBoxLayout()

        # Icône visuelle
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap("assets/icon.png").scaled(48, 48))
        layout.addWidget(icon_label)

        layout.addWidget(QLabel("Type de sécurité :"))

        self.security_dropdown = QComboBox()
        self.security_dropdown.addItems(["Fermer auto", "Logger"])
        layout.addWidget(self.security_dropdown)

        self.current_label = QLabel()
        layout.addWidget(self.current_label)

        self.setLayout(layout)

        # Charger les paramètres existants
        self.settings = self.load_settings()
        self.security_dropdown.setCurrentText(self.settings.get("security_mode", "Fermer auto"))
        self.current_label.setText(f"Sélection actuelle : {self.security_dropdown.currentText()}")

        # Sauvegarder à chaque changement
        self.security_dropdown.currentTextChanged.connect(self.on_change)

    def on_change(self, text):
        self.current_label.setText(f"Sélection actuelle : {text}")
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
