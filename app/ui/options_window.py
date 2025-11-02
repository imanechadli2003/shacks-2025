from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame, QSpacerItem, QSizePolicy, QPushButton, QLineEdit, QScrollArea
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import Qt, Signal

from app.ui.intrusion_report_window import IntrusionReportWindow
from app.utils.const import TOKEN_DISCORD, GUILD_ID
from ..utils.settings import settings
from .reference_window import ReferenceWindow
from text_to_num import text2num
import threading
import asyncio
from app.utils.use_discord import recuperer_usernames

class OptionsWindow(QWidget):
    reference_window_opened = Signal()
    reference_window_closed = Signal()
    discord_users_loaded = Signal(list)
    discord_users_failed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shacks 2025 - Options")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.resize(500, 400)
        
        self.reference_window = None
        self.intrusion_report_window = None
        
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
                background-color: #f5f5f5;
                color: #000000;
                font-size: 13px;
                min-height: 25px;
            }
            QComboBox:hover {
                border: 2px solid #018849;
            }
            QComboBox:focus {
                border: 2px solid #016a37;
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
                selection-background-color: #018849;
                selection-color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ffffff;
                color: #000000;
                font-size: 13px;
                min-height: 25px;
            }
            QLineEdit:hover {
                border: 2px solid #018849;
            }
            QLineEdit:focus {
                border: 2px solid #016a37;
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
            QPushButton {
                padding: 10px 20px;
                border: 2px solid #018849;
                border-radius: 5px;
                background-color: #f5f5f5;
                color: #018849;
                font-size: 13px;
                font-weight: bold;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #f0f9f5;
                border: 2px solid #016a37;
                color: #016a37;
            }
            QPushButton:pressed {
                background-color: #e0f2ea;
                border: 2px solid #014d28;
                color: #014d28;
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
        
        security_label = QLabel("Type de sécurité")
        security_label.setObjectName("section")
        options_layout.addWidget(security_label)

        security_desc = QLabel("Choisissez le mode de réaction en cas de détection d'intrus :")
        security_desc.setWordWrap(True)
        security_desc.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 5px;")
        options_layout.addWidget(security_desc)

        self.security_dropdown = QComboBox()
        self.security_dropdown.addItems(["Fermeture automatique", "Contre-espionnage"])
        options_layout.addWidget(self.security_dropdown)

        main_layout.addLayout(options_layout)

        # Section Discord
        discord_layout = QVBoxLayout()
        discord_layout.setSpacing(15)

        discord_label = QLabel("Discord")
        discord_label.setObjectName("section")
        discord_layout.addWidget(discord_label)

        discord_desc = QLabel("Choisissez l'utilisateur Discord à notifier. Charge les pseudos depuis le serveur.")
        discord_desc.setWordWrap(True)
        discord_desc.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 5px;")
        discord_layout.addWidget(discord_desc)

        discord_row = QHBoxLayout()
        discord_row.setSpacing(10)

        self.discord_user_dropdown = QComboBox()
        self.discord_user_dropdown.setEditable(False)
        discord_row.addWidget(self.discord_user_dropdown)

        self.discord_load_button = QPushButton("Charger")
        self.discord_load_button.clicked.connect(self.on_load_discord_users)
        discord_row.addWidget(self.discord_load_button)

        discord_layout.addLayout(discord_row)

        self.discord_error_label = QLabel("")
        self.discord_error_label.setStyleSheet("color: #e74c3c; font-size: 12px; font-style: italic;")
        self.discord_error_label.setVisible(False)
        discord_layout.addWidget(self.discord_error_label)

        main_layout.addLayout(discord_layout)
        
        # Section Durée du contre-espionnage
        duration_layout = QVBoxLayout()
        duration_layout.setSpacing(15)
        
        duration_label = QLabel("Durée du contre-espionnage")
        duration_label.setObjectName("section")
        duration_layout.addWidget(duration_label)

        duration_desc = QLabel("Nombre de secondes pendant lesquelles le système espionnera l'intrus en français :")
        duration_desc.setWordWrap(True)
        duration_desc.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 5px;")
        duration_layout.addWidget(duration_desc)

        duration_input_layout = QHBoxLayout()
        duration_input_layout.setSpacing(10)
        
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("Ex: vingt trois")
        duration_input_layout.addWidget(self.duration_input)
        
        self.duration_button = QPushButton("Valider")
        self.duration_button.clicked.connect(self.on_validate_duration)
        duration_input_layout.addWidget(self.duration_button)
        
        duration_layout.addLayout(duration_input_layout)
        
        # Label pour les messages d'erreur
        self.duration_error_label = QLabel("")
        self.duration_error_label.setStyleSheet("color: #e74c3c; font-size: 12px; font-style: italic;")
        self.duration_error_label.setVisible(False)
        duration_layout.addWidget(self.duration_error_label)

        main_layout.addLayout(duration_layout)
        
        # Section Image de référence
        reference_layout = QVBoxLayout()
        reference_layout.setSpacing(15)
        
        reference_label = QLabel("Image de référence")
        reference_label.setObjectName("section")
        reference_layout.addWidget(reference_label)

        reference_desc = QLabel("Définissez l'image de référence utilisée pour la détection d'intrus :")
        reference_desc.setWordWrap(True)
        reference_desc.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 5px;")
        reference_layout.addWidget(reference_desc)

        self.reference_button = QPushButton("Définir images de référence")
        self.reference_button.clicked.connect(self.on_set_reference)
        reference_layout.addWidget(self.reference_button)

        main_layout.addLayout(reference_layout)

        # Section Rapport d'intrusion
        reports_layout = QVBoxLayout()
        reports_layout.setSpacing(15)

        reports_label = QLabel("Rapports d'intrusion")
        reports_label.setObjectName("section")
        reports_layout.addWidget(reports_label)

        reports_desc = QLabel("Consultez les rapports d'intrusion générés :")
        reports_desc.setWordWrap(True)
        reports_desc.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 5px;")
        reports_layout.addWidget(reports_desc)

        self.reports_button = QPushButton("Voir les rapports")
        self.reports_button.clicked.connect(self.on_open_intrusion_report)
        reports_layout.addWidget(self.reports_button)

        main_layout.addLayout(reports_layout)
        
        # Espaceur pour pousser le contenu vers le haut
        main_layout.addStretch()

        # Conteneur scrollable pour garder une hauteur fixe et scroller quand le contenu grandit
        container_widget = QWidget()
        container_widget.setLayout(main_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container_widget)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll)
        self.setLayout(root_layout)
        # Hauteur fixe, largeur libre (redimensionnable si l'utilisateur veut)
        self.setFixedHeight(400)

        # Charger les paramètres
        self.security_dropdown.setCurrentText(settings.get("security_mode"))
        
        # Charger la durée du contre-espionnage
        duration_value = settings.get("espionnage_duration_str", "vingt trois")
        self.duration_input.setText(str(duration_value))

        self.security_dropdown.currentTextChanged.connect(self.on_change)

        # Préselection Discord si déjà sauvegardé (affiche le nom si présent avant chargement)
        saved_username = settings.get("discord_username")
        if saved_username:
            self.discord_user_dropdown.addItem(saved_username)

        # Connexions signaux Discord
        self.discord_users_loaded.connect(self._on_discord_users_loaded)
        self.discord_users_failed.connect(self._on_discord_users_failed)

    def on_change(self, text):
        settings.set("security_mode", text)
    
    def on_validate_duration(self):
        """Valide et sauvegarde la durée du contre-espionnage."""
        try:
            duration_str = self.duration_input.text().strip()
            try:
                duration = text2num(duration_str, "fr")
                if duration <= 0:
                    self.duration_error_label.setText("La durée doit être positive")
                    self.duration_error_label.setVisible(True)
                    return
                settings.set("espionnage_duration", duration)
                settings.set("espionnage_duration_str", duration_str)
                self.duration_error_label.setVisible(False)
                print(f"[OptionsWindow] Durée du contre-espionnage mise à jour: {duration}s")
            except ValueError:
                self.duration_error_label.setText("Ce n'est pas un nombre français valide")
                self.duration_error_label.setVisible(True)
        except ValueError as e:
            self.duration_error_label.setText(f"⚠️ Valeur invalide: entrez un nombre ou du texte (ex: 'trois cents')")
            self.duration_error_label.setVisible(True)
            print(f"[OptionsWindow] Valeur invalide pour la durée: {self.duration_input.text()} ({e})")
    
    def on_set_reference(self):
        if self.reference_window is None or not self.reference_window.isVisible():
            self.reference_window = ReferenceWindow()
            self.reference_window.window_closed.connect(self.on_reference_window_closed)
            self.reference_window.showMaximized()
            self.reference_window_opened.emit()
        else:
            self.reference_window.activateWindow()
    def on_open_intrusion_report(self):
        if self.intrusion_report_window is None or not self.intrusion_report_window.isVisible():
            self.intrusion_report_window = IntrusionReportWindow()
            self.intrusion_report_window.showMaximized()
        else:
            self.intrusion_report_window.activateWindow()
    
    def on_reference_window_closed(self):
        self.reference_window_closed.emit()

    # --- Discord helpers ---
    def on_load_discord_users(self):
        """Charge les pseudos Discord via l'API du bot dans un thread séparé."""
        self.discord_error_label.setVisible(False)
        self.discord_load_button.setEnabled(False)
        self.discord_load_button.setText("Chargement...")

        def _worker():
            try:
                users = asyncio.run(recuperer_usernames(TOKEN_DISCORD, int(GUILD_ID)))
                self.discord_users_loaded.emit(users)
            except Exception as e:
                self.discord_users_failed.emit(str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_discord_users_loaded(self, users: list):
        # users: List[{"id": int, "name": str}]
        self.discord_user_dropdown.clear()
        if users:
            # Trie par nom insensible à la casse
            for u in sorted(users, key=lambda x: x.get("name", "").lower()):
                self.discord_user_dropdown.addItem(u.get("name", ""), u.get("id"))

            # Restaure sélection sauvegardée si présente (priorité à l'ID, sinon par nom)
            saved_user_id = settings.get("discord_user_id")
            if saved_user_id is not None:
                for i in range(self.discord_user_dropdown.count()):
                    if self.discord_user_dropdown.itemData(i) == saved_user_id:
                        self.discord_user_dropdown.setCurrentIndex(i)
                        break
            else:
                saved_username = settings.get("discord_username")
                if saved_username:
                    idx = self.discord_user_dropdown.findText(saved_username)
                    if idx >= 0:
                        self.discord_user_dropdown.setCurrentIndex(idx)
        else:
            self.discord_user_dropdown.addItem("(Aucun membre trouvé)")

        self.discord_load_button.setEnabled(True)
        self.discord_load_button.setText("Charger")

        # Sauvegarde immédiate de la sélection actuelle (id + nom)
        self._save_selected_discord_user()

        # Connect change handler après remplissage pour persister id + nom
        self.discord_user_dropdown.currentIndexChanged.connect(lambda _: self._save_selected_discord_user())

    def _on_discord_users_failed(self, error: str):
        self.discord_error_label.setText(f"Erreur de chargement des membres: {error}")
        self.discord_error_label.setVisible(True)
        self.discord_load_button.setEnabled(True)
        self.discord_load_button.setText("Charger")

    def _save_selected_discord_user(self):
        username = self.discord_user_dropdown.currentText()
        user_id = self.discord_user_dropdown.currentData()
        if username and user_id and not str(username).startswith("("):
            try:
                settings.set("discord_username", username)
                settings.set("discord_user_id", int(user_id))
            except Exception:
                # Ne pas bloquer l'UI si conversion échoue
                pass
        
