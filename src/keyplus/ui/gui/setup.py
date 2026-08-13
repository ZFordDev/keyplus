# KeyPlus GUI setup screen
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from keyplus.application.errors import KeyPlusError
from keyplus.storage.migration import find_legacy_pair


def build_setup_screen(service, on_success):
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
    warning.setStyleSheet(
        "color: #f87171; font-size: 13px; font-weight: 500; line-height: 1.4;"
    )
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
    title.setStyleSheet(
        "color: #ffffff; font-size: 18px; font-weight: 600; margin-bottom: 4px;"
    )
    form_layout.addWidget(title)

    # Input Fields
    pw1 = QLineEdit()
    pw1.setEchoMode(QLineEdit.Password)
    pw1.setPlaceholderText("Enter new master password")
    pw1.setFixedHeight(40)  # Slightly taller inputs feel significantly more high-end
    form_layout.addWidget(pw1)

    pw2 = QLineEdit()
    pw2.setEchoMode(QLineEdit.Password)
    pw2.setPlaceholderText("Confirm master password")
    pw2.setFixedHeight(40)
    form_layout.addWidget(pw2)

    # --- Error Label (Hidden initially so it doesn't leave an empty gap) ---
    error = QLabel("")
    error.setStyleSheet(
        "color: #f87171; font-size: 13px; font-weight: 500; margin-top: 4px;"
    )
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
    migrate_btn = QPushButton("Migrate a KeyPlus 0.2 Vault")
    migrate_btn.setFixedHeight(42)
    layout.addWidget(migrate_btn)

    def handle_setup():
        p1 = pw1.text()
        p2 = pw2.text()

        if not p1:
            error.setText("Password cannot be blank.")
            error.setVisible(True)
            return

        if p1 != p2:
            error.setText("Passwords do not match. Please try again.")
            error.setVisible(True)
            return

        error.setVisible(False)
        try:
            service.initialize(p1)
            on_success()
        except KeyPlusError as exc:
            error.setText(str(exc))
            error.setVisible(True)

    btn.clicked.connect(handle_setup)

    def handle_migration():
        selected = QFileDialog.getExistingDirectory(
            widget, "Select the folder containing auth.db and vault.json"
        )
        if not selected:
            return
        pair = find_legacy_pair(Path(selected))
        if pair is None:
            QMessageBox.warning(
                widget,
                "Legacy vault not found",
                "The selected folder does not contain both auth.db and vault.json.",
            )
            return
        password, accepted = QInputDialog.getText(
            widget,
            "Legacy master password",
            "Master password:",
            QLineEdit.EchoMode.Password,
        )
        if not accepted:
            return
        try:
            service.migrate_legacy(pair, password)
            QMessageBox.information(
                widget,
                "Migration complete",
                "The 0.3 vault was created and the original 0.2 files were preserved.",
            )
            on_success()
        except KeyPlusError as exc:
            QMessageBox.critical(widget, "Migration failed", str(exc))

    migrate_btn.clicked.connect(handle_migration)

    return widget
