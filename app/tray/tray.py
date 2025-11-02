import asyncio
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer
from pathlib import Path

from app.ui.intrusion_report_window import IntrusionReportWindow
from ..utils.settings import settings
from app.utils.ressources import resource_path
from app.utils.tracking.trigger_intrusion_alert import trigger_intrusion_alert
from ..ui.options_window import OptionsWindow
from ..camera.camera_capture import CameraCapture
from ..camera.intruder import Intruder


class SystemTray(QSystemTrayIcon):
    def __init__(self, app):
        icon_path = resource_path("assets/icon.png")
        super().__init__(QIcon(icon_path), parent=None)
        self.app = app
        self.setToolTip("Sneak Snap")

        # --- Menu du tray ---
        menu = QMenu()
        reports_action = QAction("Voir les rapports", self)
        reports_action.triggered.connect(self.open_reports)
        menu.addAction(reports_action)

        options_action = QAction("Options", self)
        options_action.triggered.connect(self.open_options)
        menu.addAction(options_action)

        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.setVisible(True)

        self.windows = []
        self.camera = CameraCapture()

        # --- Charger les images de référence ---
        self.load_reference_images()

        # --- Compteur de détections ---
        self.intruder_count = 0
        self.threshold = 3

        # --- Timer principal ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.tache_periodique)
        self.timer.start(1000)

    # ---------- FONCTIONS UTILITAIRES ----------
    def load_reference_images(self):
        """Charge les images de référence depuis captures/reference."""
        reference_dir = Path("captures/reference")
        reference_images = [str(p) for p in reference_dir.glob("reference_*.jpg")]

        if reference_images:
            self.intruder_detector = Intruder(reference_paths=reference_images)
            print(f"[Intruder] {len(reference_images)} image(s) de référence chargée(s) : {reference_images}")
        else:
            self.intruder_detector = None
            print("[Intruder] ATTENTION : Aucune image de référence trouvée !")

    # ---------- INTERFACE ----------
    def open_options(self):
        win = OptionsWindow()
        if hasattr(win, "reference_window_opened"):
            win.reference_window_opened.connect(self.stop_monitoring)
        if hasattr(win, "reference_window_closed"):
            win.reference_window_closed.connect(self.start_monitoring)
        win.show()
        self.windows.append(win)

    def open_reports(self):
        win = IntrusionReportWindow()
        win.showMaximized()
        self.windows.append(win)

    # ---------- SURVEILLANCE ----------
    def tache_periodique(self):
        if not self.intruder_detector:
            print("[Intruder] Aucun détecteur actif.")
            return

        self.camera.capture_image()
        is_intruder = self.intruder_detector.is_intruder(
            path_frame="captures/last_capture.jpg", tolerance=0.6
        )

        # Si indéterminé, ne rien faire (ne pas modifier le compteur)
        if is_intruder is None:
            print("[Intruder] Résultat indéterminé, itération ignorée.")
            return

        if is_intruder is True:
            self.intruder_count += 1
            print(f"[Intruder] Détection {self.intruder_count}/{self.threshold}")
        elif is_intruder is False:
            self.intruder_count = 0
            print("[Intruder] Visage reconnu, compteur réinitialisé.")

        if self.intruder_count >= self.threshold:
            self.trigger_intrusion_alert()
            self.intruder_count = 0

    def trigger_intrusion_alert(self):
        mode = settings.get("security_mode")
        asyncio.run(trigger_intrusion_alert(mode))
        
        print("[Intruder] Alerte envoyée.")

    # ---------- CYCLE DE VIE ----------
    def stop_monitoring(self):
        print("[Tray] Surveillance arrêtée.")
        self.timer.stop()
        self.camera.release()

    def start_monitoring(self):
        print("[Tray] Surveillance relancée.")
        self.camera = CameraCapture()
        self.load_reference_images()
        self.timer.start(3000)

    def quit_app(self):
        self.timer.stop()
        self.camera.release()
        self.camera.delete_last_image()
        self.app.quit()
