from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer
from ..ui.options_window import OptionsWindow
from ..camera.camera_capture import CameraCapture
from ..camera.intruder import Intruder

class SystemTray(QSystemTrayIcon):
    def __init__(self, app):
        super().__init__(QIcon("assets/icon.png"), parent=None)
        self.app = app
        self.setToolTip("Shacks 2025 - Sécurité")

        menu = QMenu()
        options_action = QAction("Options", self)
        options_action.triggered.connect(self.open_options)
        menu.addAction(options_action)

        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.setVisible(True)
        self.show()

        self.windows = []

        # Initialiser la caméra
        self.camera = CameraCapture()
        
        self.intruder_detector = Intruder(path_reference="captures/reference/face.jpg")

        # Timer pour exécuter la capture toutes les 5 secondes
        self.timer = QTimer()
        self.timer.timeout.connect(self.tache_periodique)
        self.timer.start(3000)  # toutes les 3 secondes

    def open_options(self):
        win = OptionsWindow()
        win.show()
        self.windows.append(win)

    def tache_periodique(self):
        try:
            self.camera.capture_image()
            is_intruder_detected = self.intruder_detector.is_intruder(
                path_frame="captures/last_capture.jpg",
                tolerance=0.6
            )
            if is_intruder_detected:
                self.showMessage(
                    "Alerte Intrusion",
                    "Un intrus a été détecté !",
                    QSystemTrayIcon.Critical
                )
        except Exception as e:
            print(f"Erreur capture caméra : {e}")

    def quit_app(self):
        self.timer.stop()
        self.camera.release()
        self.camera.delete_last_image()
        self.app.quit()
