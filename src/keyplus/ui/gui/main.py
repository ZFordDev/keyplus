from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QWidget

from keyplus.application.errors import KeyPlusError
from keyplus.bootstrap import build_service

from .add_entry import AddEntryDialog
from .dash import build_dashboard
from .login import build_login_screen
from .setup import build_setup_screen
from .view_entry import build_view_entry

# Clean, professional modern dark palette
MODERN_DARK_STYLE = """
KeyPlusFrame {
    background-color: #121824;
}

QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
}

/* Reusable styles that will inherit across our child screens */
QLineEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f8fafc;
}
QLineEdit:focus {
    border: 1px solid #3b82f6;
}

QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #1d4ed8;
}
QPushButton:pressed {
    background-color: #1e40af;
}
"""


class KeyPlusFrame(QWidget):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self._route = "startup"
        self.resize(450, 650)
        self.setWindowTitle("KeyPlus Vault")
        self.setStyleSheet(MODERN_DARK_STYLE)

        # Main layout structure with clean, consistent padding
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget()
        root_layout.addWidget(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Generous padding inside the viewport for a spacious, high-end feel
        self.body = QVBoxLayout()
        self.body.setContentsMargins(32, 32, 32, 32)
        layout.addLayout(self.body)

        # --- ROUTER ---
        if not self.service.initialized:
            self.show_setup_screen()
        else:
            self.show_login_screen()
        self.session_timer = QTimer(self)
        self.session_timer.setInterval(1000)
        self.session_timer.timeout.connect(self._check_session)
        self.session_timer.start()

    # ---------------------------------------------------------
    # ROUTER SCREENS
    # ---------------------------------------------------------
    def show_setup_screen(self):
        self._route = "setup"
        self._clear_body()

        def on_success():
            self.show_dashboard()

        setup_widget = build_setup_screen(self.service, on_success)
        self.body.addWidget(setup_widget)

    def show_login_screen(self):
        self._route = "login"
        self._clear_body()
        login_widget = build_login_screen(self.service, on_success=self.show_dashboard)
        self.body.addWidget(login_widget)

    # ---------------------------------------------------------
    # GUI: Dashboard
    # ---------------------------------------------------------
    def show_dashboard(self):
        # Intercept if session expired before rendering
        if not self.service.unlocked:
            self.show_login_screen()
            return

        self._route = "dashboard"
        self._clear_body()
        dashboard_widget = build_dashboard(
            self.service,
            on_view_entry=self.show_view_entry,
            on_add_entry=self.show_add_entry_modal,
            on_backup=self.create_backup,
            on_logout=self.logout,
        )
        self.body.addWidget(dashboard_widget)

    # ---------------------------------------------------------
    # GUI: view entry
    # ---------------------------------------------------------
    def show_view_entry(self, entry_id):
        # Intercept right here when they click an item!
        if not self.service.unlocked:
            self.show_login_screen()
            return

        self._route = "entry"
        self._clear_body()
        view_widget = build_view_entry(
            self.service,
            entry_id,
            on_back=self.show_dashboard,
            on_edit=self.show_edit_entry_modal,
            on_delete=self.delete_entry,
        )
        self.body.addWidget(view_widget)

    def show_add_entry_modal(self):
        dialog = AddEntryDialog(self.service, self)
        if dialog.exec():
            self.show_dashboard()

    def show_edit_entry_modal(self, entry_id):
        entry = self.service.get_entry(entry_id)
        dialog = AddEntryDialog(self.service, self, entry=entry)
        if dialog.exec():
            self.show_view_entry(entry_id)

    def delete_entry(self, entry_id):
        try:
            entry = self.service.get_entry(entry_id)
        except KeyPlusError as exc:
            QMessageBox.critical(self, "KeyPlus error", str(exc))
            return
        answer = QMessageBox.question(
            self,
            "Delete entry",
            f"Delete '{entry.name}' permanently?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_entry(entry_id)
                self.show_dashboard()
            except KeyPlusError as exc:
                QMessageBox.critical(self, "Delete failed", str(exc))

    def logout(self):
        self.service.lock()
        self.show_login_screen()

    def create_backup(self):
        try:
            destination = self.service.create_backup()
        except KeyPlusError as exc:
            QMessageBox.critical(self, "Backup failed", str(exc))
            return
        QMessageBox.information(
            self,
            "Backup created",
            f"An encrypted backup was created at:\n{destination}",
        )

    def _check_session(self):
        if self._route in {"dashboard", "entry"} and not self.service.unlocked:
            self.show_login_screen()

    def _clear_body(self):
        while self.body.count():
            item = self.body.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


def launch_gui(service=None):
    app = QApplication([])
    frame = KeyPlusFrame(service or build_service())
    frame.show()
    return app.exec()


if __name__ == "__main__":
    launch_gui()
