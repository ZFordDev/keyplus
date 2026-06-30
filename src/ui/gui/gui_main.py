from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from logic import auth, session
from ui.gui.setup import build_setup_screen
from ui.gui.login import build_login_screen
from ui.gui.dash import build_dashboard
from ui.gui.view_entry import build_view_entry
from ui.gui.add_entry import AddEntryDialog

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
    def __init__(self):
        super().__init__()
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
        if not auth.password_exists():
            self.show_setup_screen()
        else:
            self.show_login_screen()

    # ---------------------------------------------------------
    # ROUTER SCREENS
    # ---------------------------------------------------------
    def show_setup_screen(self):
        self._clear_body()
        def on_success(): self.show_dashboard()
        setup_widget = build_setup_screen(on_success)
        self.body.addWidget(setup_widget)

    def show_login_screen(self):
        self._clear_body()
        login_widget = build_login_screen(
            on_success=self.show_dashboard,
            on_reset=self.show_setup_screen
        )
        self.body.addWidget(login_widget)

    # ---------------------------------------------------------
    # GUI: Dashboard
    # ---------------------------------------------------------
    def show_dashboard(self):
        # Intercept if session expired before rendering
        if not session.get_session_key(): 
            self.show_login_screen()
            return

        self._clear_body()
        dashboard_widget = build_dashboard(
            on_view_entry=self.show_view_entry,
            on_add_entry=self.show_add_entry_modal,
            on_logout=self.show_login_screen
        )
        self.body.addWidget(dashboard_widget)

    # ---------------------------------------------------------
    # GUI: view entry
    # ---------------------------------------------------------
    def show_view_entry(self, entry_id):
        # Intercept right here when they click an item!
        if not session.get_session_key():
            self.show_login_screen()
            return

        self._clear_body()
        view_widget = build_view_entry(entry_id, on_back=self.show_dashboard)
        self.body.addWidget(view_widget)

    def show_add_entry_modal(self):
        dialog = AddEntryDialog(self)
        if dialog.exec():
            self.show_dashboard()

    def _clear_body(self):
        while self.body.count():
            item = self.body.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


def launch_gui():
    app = QApplication([])
    frame = KeyPlusFrame()
    frame.show()
    app.exec()

if __name__ == "__main__":
    launch_gui()