from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QFileDialog, QProgressDialog
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtCore import Qt, QTimer, Signal
from ..camera.camera_capture import CameraCapture
import cv2
import os
from pathlib import Path
import shutil
from app.utils.ressources import resource_path

class ReferenceWindow(QWidget):
    window_closed = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shacks 2025 - Images de référence")
        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))
        self.resize(700, 600)
        
        self.camera = CameraCapture()
        self.captured_images = []
        self.reference_dir = Path("captures/reference")
        self.reference_dir.mkdir(parents=True, exist_ok=True)
        
        # Etat de fermeture et UI de chargement
        self._closing_dialog = None
        self.closing = False
        
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
            QLabel#preview {
                background-color: #2c3e50;
                border: 3px solid #bdc3c7;
                border-radius: 10px;
            }
            QLabel#thumbnail {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            
            QFrame#separator {
                background-color: #bdc3c7;
            }
            QPushButton#primary {
                padding: 12px 25px;
                border: 2px solid #018849;
                border-radius: 5px;
                background-color: #018849;
                color: white;
                font-size: 14px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton#primary:hover {
                background-color: #016a37;
                border: 2px solid #016a37;
            }
            QPushButton#primary:pressed {
                background-color: #014d28;
                border: 2px solid #014d28;
            }
            QPushButton#primary:disabled {
                background-color: #95a5a6;
                border: 2px solid #7f8c8d;
                color: #ecf0f1;
            }
            QPushButton#secondary {
                padding: 12px 25px;
                border: 2px solid #018849;
                border-radius: 5px;
                background-color: #f5f5f5;
                color: #018849;
                font-size: 14px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton#secondary:hover {
                background-color: #f0f9f5;
                border: 2px solid #016a37;
                color: #016a37;
            }
            QPushButton#secondary:pressed {
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
        
        title_label = QLabel("Images de référence")
        title_label.setObjectName("title")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Capturez des images pour la détection d'intrus")
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

        # Section Aperçu caméra
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(15)
        
        preview_label = QLabel("Aperçu de la caméra")
        preview_label.setObjectName("section")
        preview_layout.addWidget(preview_label)

        preview_desc = QLabel("Positionnez-vous devant la caméra et prenez une photo :")
        preview_desc.setWordWrap(True)
        preview_desc.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 5px;")
        preview_layout.addWidget(preview_desc)

        # Aperçu vidéo
        self.video_label = QLabel()
        self.video_label.setObjectName("preview")
        self.video_label.setFixedSize(640, 360)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Chargement de la caméra...")
        self.video_label.setStyleSheet("color: #ecf0f1; font-size: 14px;")
        preview_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)

        # Boutons de capture
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.gallery_button = QPushButton("Importer une image")
        self.gallery_button.setObjectName("secondary")
        self.gallery_button.clicked.connect(self.choose_from_gallery)
        button_layout.addWidget(self.gallery_button)
        
        self.capture_button = QPushButton("Prendre une photo")
        self.capture_button.setObjectName("primary")
        self.capture_button.clicked.connect(self.capture_photo)
        button_layout.addWidget(self.capture_button)
        
        button_layout.addStretch()
        preview_layout.addLayout(button_layout)

        main_layout.addLayout(preview_layout)

        # Section Images capturées
        gallery_layout = QVBoxLayout()
        gallery_layout.setSpacing(15)
        
        gallery_header_layout = QHBoxLayout()
        gallery_label = QLabel("Images capturées (max 3)")
        gallery_label.setObjectName("section")
        gallery_header_layout.addWidget(gallery_label)
        gallery_header_layout.addStretch()
        gallery_layout.addLayout(gallery_header_layout)

        # Conteneur des miniatures
        self.thumbnails_layout = QHBoxLayout()
        self.thumbnails_layout.setSpacing(10)
        
        # Créer 3 emplacements pour les miniatures
        self.thumbnail_labels = []
        for i in range(3):
            thumbnail = QLabel()
            thumbnail.setObjectName("thumbnail")
            thumbnail.setFixedSize(180, 135)
            thumbnail.setAlignment(Qt.AlignCenter)
            thumbnail.setText(f"Photo {i+1}")
            thumbnail.setStyleSheet("color: #95a5a6; font-size: 12px;")
            thumbnail.setScaledContents(False)
            self.thumbnail_labels.append(thumbnail)
            self.thumbnails_layout.addWidget(thumbnail)
        
        self.thumbnails_layout.addStretch()
        gallery_layout.addLayout(self.thumbnails_layout)

        main_layout.addLayout(gallery_layout)
        
        # Espaceur pour pousser le contenu vers le haut
        main_layout.addStretch()

        self.setLayout(main_layout)

        # Timer pour mettre à jour l'aperçu vidéo
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms = ~33 FPS
        
        # Charger les images existantes
        self.load_existing_images()

    def update_frame(self):
        """Met à jour l'aperçu vidéo"""
        frame = self.camera.get_frame()
        if frame is not None:
            # Redimensionner le frame pour l'aperçu
            frame = cv2.resize(frame, (640, 360))
            # Convertir BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convertir en QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            # Afficher dans le label
            self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def capture_photo(self):
        """Capture une photo et l'enregistre"""
        frame = self.camera.get_frame()
        if frame is not None:
            # Supprimer reference_3.jpg s'il existe
            ref3 = self.reference_dir / "reference_3.jpg"
            if ref3.exists():
                os.remove(ref3)
                print(f"Supprimé : {ref3}")
            
            # Renommer reference_2.jpg -> reference_3.jpg
            ref2 = self.reference_dir / "reference_2.jpg"
            if ref2.exists():
                os.rename(ref2, ref3)
                print(f"Renommé : {ref2} -> {ref3}")
            
            # Renommer reference_1.jpg -> reference_2.jpg
            ref1 = self.reference_dir / "reference_1.jpg"
            if ref1.exists():
                os.rename(ref1, ref2)
                print(f"Renommé : {ref1} -> {ref2}")
            
            # Sauvegarder la nouvelle photo en reference_1.jpg
            cv2.imwrite(str(ref1), frame)
            print(f"Photo capturée : {ref1}")
            
            # Recharger les images existantes
            self.load_existing_images()
    
    def choose_from_gallery(self):
        """Ouvre un dialogue pour choisir une image depuis la galerie"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            # Charger l'image avec OpenCV pour la valider
            frame = cv2.imread(file_path)
            if frame is not None:
                # Supprimer reference_3.jpg s'il existe
                ref3 = self.reference_dir / "reference_3.jpg"
                if ref3.exists():
                    os.remove(ref3)
                    print(f"Supprimé : {ref3}")
                
                # Renommer reference_2.jpg -> reference_3.jpg
                ref2 = self.reference_dir / "reference_2.jpg"
                if ref2.exists():
                    os.rename(ref2, ref3)
                    print(f"Renommé : {ref2} -> {ref3}")
                
                # Renommer reference_1.jpg -> reference_2.jpg
                ref1 = self.reference_dir / "reference_1.jpg"
                if ref1.exists():
                    os.rename(ref1, ref2)
                    print(f"Renommé : {ref1} -> {ref2}")
                
                # Copier l'image depuis la galerie en reference_1.jpg
                shutil.copy(file_path, str(ref1))
                print(f"Photo ajoutée depuis galerie : {ref1}")
                
                # Recharger les images existantes
                self.load_existing_images()
            else:
                print("Erreur : Impossible de charger l'image")

    def update_thumbnails(self):
        """Met à jour l'affichage des miniatures"""
        for i, label in enumerate(self.thumbnail_labels):
            if i < len(self.captured_images):
                pixmap = QPixmap(self.captured_images[i])
                scaled_pixmap = pixmap.scaled(180, 135, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(scaled_pixmap)
                label.setText("")
                label.setObjectName("thumbnail")
                label.setStyleSheet(self.styleSheet())
            else:
                label.setPixmap(QPixmap())
                label.setText(f"Photo {i+1}")
                label.setObjectName("thumbnail")
                label.setStyleSheet(self.styleSheet())

    def load_existing_images(self):
        """Charge les images de référence existantes"""
        self.captured_images = []
        if self.reference_dir.exists():
            # Charger dans l'ordre : reference_1, reference_2, reference_3
            for i in range(1, 4):
                img_path = self.reference_dir / f"reference_{i}.jpg"
                if img_path.exists():
                    self.captured_images.append(str(img_path))
        self.update_thumbnails()

    def closeEvent(self, event):
        """Affiche un chargement et finalise la fermeture proprement"""
        if self.closing:
            # Fermeture déjà en cours: laisser Qt terminer
            return super().closeEvent(event)
        
        # Intercepter la fermeture pour montrer un chargement
        event.ignore()
        self.show_closing_dialog()
        # Finaliser en asynchrone pour laisser le dialog s'afficher
        QTimer.singleShot(50, self._finalize_close)

    def show_closing_dialog(self):
        """Affiche un dialogue de progression (mode indéterminé)."""
        if self._closing_dialog is None:
            dlg = QProgressDialog("Fermeture en cours...", None, 0, 0, self)
            dlg.setWindowTitle("Veuillez patienter")
            dlg.setCancelButton(None)
            dlg.setWindowModality(Qt.ApplicationModal)
            dlg.setAutoClose(False)
            dlg.setAutoReset(False)
            dlg.setMinimumDuration(0)
            self._closing_dialog = dlg
            dlg.show()

    def _finalize_close(self):
        """Stoppe les tâches, libère la caméra puis ferme la fenêtre."""
        try:
            if hasattr(self, 'timer') and self.timer is not None:
                self.timer.stop()
        except Exception:
            pass
        try:
            if hasattr(self, 'camera') and self.camera is not None:
                self.camera.release()
        except Exception:
            pass
        
        # Notifier les autres composants
        self.window_closed.emit()

        # Fermer le dialog
        if self._closing_dialog is not None:
            self._closing_dialog.close()
            self._closing_dialog.deleteLater()
            self._closing_dialog = None

        # Marquer et fermer réellement
        self.closing = True
        self.close()