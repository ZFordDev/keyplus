# src/ui/gui/setup.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt
from logic import auth, session


def build_setup_screen(on_success):
    """
    Returns a QWidget containing the setup UI.
    Calls on_success() when the vault is initialized.
    """
    widget = QWidget()
    
    # Use a clean layout with no outer margins so it aligns perfectly with KeyPlusFrame
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)

    # --- CRITICAL WARNING BANNER ---
    # Give the warning container its own background block to make it look like an alert card
    warning_container = QWidget()
    warning_container.setStyleSheet("""
        QWidget {
            background-color: #2d1e24;
            border: 1px solid #7f1d1d;
            border-radius: 8px;
        }
    """)
    warning_layout = QVBoxLayout(warning_container)
    warning_layout.setContentsMargins(14, 14, 14, 14)

    warning = QLabel(
        "⚠️ WARNING\n\n"
        "Creating a new master password will completely overwrite and ERASE access "
        "to all existing vault data.\n\n"
        "Your old entries will be permanently unrecoverable."
    )
    warning.setStyleSheet("color: #f87171; font-size: 13px; font-weight: 500; line-height: 1.4;")
    warning.setWordWrap(True)
    warning_layout.addWidget(warning)
    layout.addWidget(warning_container)

    # --- SPACER TO CREATE VISUAL BREAK ---
    layout.addSpacing(10)

    # --- FORM SECTION ---
    form_container = QWidget()
    form_layout = QVBoxLayout(form_container)
    form_layout.setContentsMargins(0, 0, 0, 0)
    form_layout.setSpacing(12)

    title = QLabel("Set Master Password")
    title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 4px;")
    form_layout.addWidget(title)

    # Input Fields
    pw1 = QLineEdit()
    pw1.setEchoMode(QLineEdit.Password)
    pw1.setPlaceholderText("Enter new master password")
    pw1.setFixedHeight(40) # Slightly taller inputs feel significantly more high-end
    form_layout.addWidget(pw1)

    pw2 = QLineEdit()
    pw2.setEchoMode(QLineEdit.Password)
    pw2.setPlaceholderText("Confirm master password")
    pw2.setFixedHeight(40)
    form_layout.addWidget(pw2)

    # --- Error Label (Hidden initially so it doesn't leave an empty gap) ---
    error = QLabel("")
    error.setStyleSheet("color: #f87171; font-size: 13px; font-weight: 500; margin-top: 4px;")
    error.setWordWrap(True)
    error.setVisible(False)
    form_layout.addWidget(error)

    layout.addWidget(form_container)
    
    # Pushes the button to the bottom beautifully
    layout.addStretch()

    # --- BUTTON ---
    btn = QPushButton("Initialize Vault")
    btn.setFixedHeight(42)
    layout.addWidget(btn)

    def handle_setup():
        p1 = pw1.text().strip()
        p2 = pw2.text().strip()

        if not p1:
            error.setText("Password cannot be blank.")
            error.setVisible(True)
            return

        if p1 != p2:
            error.setText("Passwords do not match. Please try again.")
            error.setVisible(True)
            return

        error.setVisible(False)
        auth.create_password(p1)
        session.set_session_key(p1)
        on_success()

    btn.clicked.connect(handle_setup)

    return widget