from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from .options_window import OptionsWindow

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
        quit_action.triggered.connect(self.app.quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.setVisible(True)
        self.show()

        self.windows = []

    def open_options(self):
        win = OptionsWindow()
        win.show()
        self.windows.append(win)
