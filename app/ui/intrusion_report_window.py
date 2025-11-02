from PySide6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
	QGridLayout, QSizePolicy, QPushButton
)
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices
from PySide6.QtCore import Qt, QEvent, QUrl
from pathlib import Path

from app.utils.ressources import resource_path
from app.utils.reports import reports_manager
from datetime import datetime

class IntrusionReportWindow(QWidget):
	def __init__(self):
		super().__init__()
  
		self.setWindowTitle("Shacks 2025 - Rapports d'intrusion")
		self.setWindowIcon(QIcon(resource_path("assets/icon.png")))
		self.resize(900, 650)

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
			QFrame#separator {
				background-color: #bdc3c7;
			}
			/* Carte de rapport */
			QFrame#card {
				background-color: #ffffff;
				border: 1px solid #e0e0e0;
				border-radius: 10px;
			}
			QLabel#cardTitle {
				color: #2c3e50;
				font-size: 14px;
				font-weight: bold;
			}
			QLabel#cardMeta {
				color: #7f8c8d;
				font-size: 12px;
			}
			QLabel#thumb {
				background-color: #ecf0f1;
				border: 1px solid #bdc3c7;
				border-radius: 5px;
			}
			QPushButton {
				padding: 8px 16px;
				border: 2px solid #018849;
				border-radius: 5px;
				background-color: #f5f5f5;
				color: #018849;
				font-size: 12px;
				font-weight: bold;
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

		title_label = QLabel("Rapports d'intrusion")
		title_label.setObjectName("title")
		title_layout.addWidget(title_label)

		subtitle_label = QLabel("Historique des événements et éléments visuels")
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

		# Section
		section_label = QLabel("Rapports")
		section_label.setObjectName("section")
		main_layout.addWidget(section_label)

		# Zone scrollable
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		scroll.setFrameShape(QFrame.NoFrame)

		content = QWidget()
		grid = QGridLayout(content)
		grid.setContentsMargins(0, 0, 0, 0)
		grid.setHorizontalSpacing(16)
		grid.setVerticalSpacing(16)

		# Charger les rapports réels depuis le gestionnaire
		reports = reports_manager.get_all_reports()

		# Ajouter les cartes en grille (3 colonnes)
		columns = 3
		for idx, report in enumerate(reports):
			row = idx // columns
			col = idx % columns
			card = self._create_card(report)
			grid.addWidget(card, row, col)

		# Si aucun rapport, afficher un placeholder
		if not reports:
			placeholder = QLabel("Aucun rapport d'intrusion pour le moment")
			placeholder.setAlignment(Qt.AlignCenter)
			placeholder.setStyleSheet("color: #95a5a6; font-size: 14px;")
			grid.addWidget(placeholder, 0, 0, 1, columns)

		print(f"[IntrusionReportWindow] cartes créées: {len(reports)}")

		scroll.setWidget(content)
		main_layout.addWidget(scroll)

		self.setLayout(main_layout)

	def _format_date_from_id(self, report_id: str) -> str:
		"""Extrait le timestamp en ms de l'ID (report_{ms}) et le formate en jj/mm/aaaa HH:MM:SS."""
		try:
			ms = int(report_id.split("_")[1])
			dt = datetime.fromtimestamp(ms / 1000)
			return dt.strftime("%d/%m/%Y %H:%M:%S")
		except Exception:
			return report_id

	def _create_card(self, report):
		card = QFrame()
		card.setObjectName("card")
		card_layout = QVBoxLayout(card)
		card_layout.setContentsMargins(12, 12, 12, 12)
		card_layout.setSpacing(10)

		# Image de couverture: utiliser l'image de l'intrus si disponible
		if getattr(report, "intruder_image_path", None):
			cover = QLabel()
			cover.setObjectName("thumb")
			cover.setAlignment(Qt.AlignCenter)
			cover.setFixedSize(260, 195)  # Taille fixe pour éviter les boucles de resize
			cover.setScaledContents(False)
			pix = QPixmap(report.intruder_image_path)
			if not pix.isNull():
				# Redimensionner une seule fois à la taille fixe
				scaled = pix.scaled(260, 195, Qt.KeepAspectRatio, Qt.SmoothTransformation)
				cover.setPixmap(scaled)
			else:
				cover.setText("Image invalide")
				cover.setStyleSheet("color: #95a5a6; font-size: 12px;")
			card_layout.addWidget(cover, 0, Qt.AlignHCenter)
		else:
			placeholder = QLabel("Aucune image d'intrus")
			placeholder.setAlignment(Qt.AlignCenter)
			placeholder.setStyleSheet("color: #95a5a6; font-size: 12px;")
			placeholder.setObjectName("thumb")
			placeholder.setFixedSize(260, 195)
			card_layout.addWidget(placeholder, 0, Qt.AlignHCenter)

		# Infos (titre + date)
		title = f"Rapport {report.id}"
		date = self._format_date_from_id(report.id)
		name_label = QLabel(title)
		name_label.setObjectName("cardTitle")
		name_label.setStyleSheet("background-color: transparent;")
		date_label = QLabel(date)
		date_label.setObjectName("cardMeta")
		date_label.setStyleSheet("background-color: transparent;")

		card_layout.addWidget(name_label)
		card_layout.addWidget(date_label)

		# Bouton pour afficher le rapport complet
		btn = QPushButton("Afficher rapport complet")
		btn.clicked.connect(lambda: self.on_show_full_report(report))
		card_layout.addWidget(btn)

		# Bouton pour afficher la timeline détaillée (HTML)
		btn_timeline = QPushButton("Afficher la timeline détaillée")
		btn_timeline.clicked.connect(lambda: self.on_show_timeline(report))
		# Optionnel: désactiver si pas de HTML connu
		html_path = Path(getattr(report, "html_report_path", ""))
		btn_timeline.setEnabled(html_path.exists())
		if not html_path.exists():
			btn_timeline.setToolTip("Aucun fichier de timeline trouvé pour ce rapport")
		card_layout.addWidget(btn_timeline)

		# Forcer la carte à s'étirer correctement
		card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		return card

	def on_show_full_report(self, report):
		"""Ouvre le PDF du rapport si disponible, sinon le dossier du rapport."""
		try:
			pdf_path = Path(getattr(report, "pdf_path", ""))
			if pdf_path.exists():
				QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf_path)))
				return
			# fallback: ouvrir le dossier contenant
			folder = Path(getattr(report, "json_summary_path", "")).parent
			if folder.exists():
				QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
			else:
				print(f"[IntrusionReportWindow] Chemins introuvables pour le rapport {report.id}")
		except Exception as e:
			print(f"[IntrusionReportWindow] Erreur à l'ouverture du rapport {getattr(report, 'id', '')}: {e}")

	def on_show_timeline(self, report):
		"""Ouvre la timeline détaillée (rapport HTML) si disponible, sinon le dossier du rapport."""
		try:
			html_path = Path(getattr(report, "html_report_path", ""))
			if html_path.exists():
				QDesktopServices.openUrl(QUrl.fromLocalFile(str(html_path)))
				return
			# fallback: ouvrir le dossier contenant
			folder = Path(getattr(report, "json_summary_path", "")).parent
			if folder.exists():
				QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))
			else:
				print(f"[IntrusionReportWindow] Timeline introuvable pour le rapport {getattr(report, 'id', '')}")
		except Exception as e:
			print(f"[IntrusionReportWindow] Erreur à l'ouverture de la timeline {getattr(report, 'id', '')}: {e}")

