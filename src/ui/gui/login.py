# src/ui/gui/login.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QToolButton, QMenu, QMessageBox
)
from PySide6.QtCore import Qt
from logic import auth, session


def build_login_screen(on_success, on_reset):
    """
    Returns a QWidget containing the login UI.
    Calls on_success() when authentication succeeds.
    Calls on_reset() when user chooses to reset the vault.
    """
    widget = QWidget()
    
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # --- TOP BAR / SETTINGS ---
    top_bar_layout = QHBoxLayout()
    top_bar_layout.setContentsMargins(0, 0, 0, 0)
    top_bar_layout.addStretch()

    settings_btn = QToolButton()
    settings_btn.setText("⚙")
    settings_btn.setToolTip("Options")
    settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    settings_btn.setStyleSheet("""
        QToolButton {
            background: transparent;
            color: #94a3b8;
            font-size: 18px;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }
        QToolButton:hover {
            color: #f1f5f9;
            background-color: #1e293b;
        }
        QToolButton::menu-indicator {
            image: none; /* Removes the annoying native arrow dropdown indicator */
        }
    """)

    # Modern Dark Theme for the settings context menu
    menu = QMenu(widget)
    menu.setStyleSheet("""
        QMenu {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 4px 0px;
        }
        QMenu::item {
            color: #e2e8f0;
            padding: 6px 16px;
            font-size: 13px;
        }
        QMenu::item:selected {
            background-color: #7f1d1d;
            color: #fee2e2;
        }
    """)
    reset_action = menu.addAction("Reset Master Password")
    settings_btn.setMenu(menu)
    settings_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

    top_bar_layout.addWidget(settings_btn)
    layout.addLayout(top_bar_layout)

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
    pw.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center text looks incredibly sleek on standalone logins
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

    layout.addWidget(card)
    
    # Push everything from the bottom up to complete the centered alignment
    layout.addStretch()

    # --- ACTIONS & LOGIC ---
    def handle_login():
        password = pw.text().strip()
        if auth.verify_password(password):
            session.set_session_key(password)
            error.setVisible(False)
            on_success()
        else:
            error.setText("❌ Incorrect master password.")
            error.setVisible(True)
            pw.clear()
            pw.setFocus()

    btn.clicked.connect(handle_login)
    pw.returnPressed.connect(handle_login) # Allow pressing Enter key to submit seamlessly

    def handle_reset():
        # Custom-styled dark native message box confirmation
        msg_box = QMessageBox(widget)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Reset Vault")
        msg_box.setText("Are you absolutely sure you want to reset?")
        msg_box.setInformativeText(
            "This will permanently erase all data currently inside the vault. "
            "This action is immediate and completely irreversible."
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Quick inline styling for the dialog box text colors to match the app theme
        msg_box.setStyleSheet("QLabel { color: #f8fafc; } QPushButton { padding: 6px 14px; }")

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            auth.AUTH_FILE.unlink(missing_ok=True)
            session.set_session_key(None)
            on_reset()

    reset_action.triggered.connect(handle_reset)

    # Auto-focus the password field on load for instant typing convenience
    pw.setFocus()

    return widget