# KeyPlus GUI login screen
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from keyplus.application.errors import KeyPlusError


def build_login_screen(service, on_success):
    """
    Returns a QWidget containing the login UI.
    Calls on_success() when authentication succeeds.
    """
    widget = QWidget()

    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # Push the login card down slightly so it's vertically balanced
    layout.addStretch()

    # --- MAIN LOGIN CARD CONTAINER ---
    card = QWidget()
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(0, 0, 0, 0)
    card_layout.setSpacing(16)

    # Brand Header Icon/Title combo
    header_layout = QVBoxLayout()
    header_layout.setSpacing(6)

    logo_label = QLabel("🔑")
    logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    logo_label.setStyleSheet("font-size: 32px; margin-bottom: 4px;")
    header_layout.addWidget(logo_label)

    title = QLabel("Welcome Back")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: 600;")
    header_layout.addWidget(title)

    subtitle = QLabel("Enter your master password to unlock the vault")
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    subtitle.setStyleSheet("color: #64748b; font-size: 13px;")
    header_layout.addWidget(subtitle)

    card_layout.addLayout(header_layout)
    card_layout.addSpacing(4)

    # Password Input
    pw = QLineEdit()
    pw.setEchoMode(QLineEdit.Password)
    pw.setPlaceholderText("Master password")
    pw.setFixedHeight(40)
    pw.setAlignment(
        Qt.AlignmentFlag.AlignCenter
    )  # Center text looks incredibly sleek on standalone logins
    card_layout.addWidget(pw)

    # Error Label (Hidden by default to maintain layout symmetry)
    error = QLabel("")
    error.setAlignment(Qt.AlignmentFlag.AlignCenter)
    error.setStyleSheet("color: #f87171; font-size: 13px; font-weight: 500;")
    error.setWordWrap(True)
    error.setVisible(False)
    card_layout.addWidget(error)

    # Unlock Button
    btn = QPushButton("Unlock Vault")
    btn.setFixedHeight(42)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    card_layout.addWidget(btn)

    restore_btn = QPushButton("Restore Encrypted Backup")
    restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    card_layout.addWidget(restore_btn)

    layout.addWidget(card)

    # Push everything from the bottom up to complete the centered alignment
    layout.addStretch()

    # --- ACTIONS & LOGIC ---
    def handle_login():
        password = pw.text()
        try:
            service.unlock(password)
            error.setVisible(False)
            on_success()
        except KeyPlusError as exc:
            error.setText(str(exc))
            error.setVisible(True)
            pw.clear()
            pw.setFocus()

    def handle_restore():
        backup, _ = QFileDialog.getOpenFileName(
            widget,
            "Restore encrypted KeyPlus backup",
            "",
            "KeyPlus vaults (*.vault);;All files (*)",
        )
        if not backup:
            return
        password = pw.text()
        if not password:
            error.setText("Enter the backup's master password first.")
            error.setVisible(True)
            pw.setFocus()
            return
        try:
            service.restore_backup(Path(backup), password)
            error.setVisible(False)
            on_success()
        except KeyPlusError as exc:
            error.setText(str(exc))
            error.setVisible(True)
            pw.clear()
            pw.setFocus()

    btn.clicked.connect(handle_login)
    restore_btn.clicked.connect(handle_restore)
    pw.returnPressed.connect(
        handle_login
    )  # Allow pressing Enter key to submit seamlessly

    # Auto-focus the password field on load for instant typing convenience
    pw.setFocus()

    return widget
