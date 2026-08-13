"""Master-password change dialog backed by the shared vault service."""

from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

from keyplus.application.errors import KeyPlusError


class ChangePasswordDialog(QDialog):
    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Change Master Password")
        self.setModal(True)
        self.resize(400, 360)

        layout = QVBoxLayout(self)
        warning = QLabel(
            "Existing encrypted backups keep the password that protected them "
            "when they were created."
        )
        warning.setWordWrap(True)
        layout.addWidget(warning)

        self.current_password = self._password_field("Current master password")
        self.new_password = self._password_field("New master password")
        self.confirm_password = self._password_field("Confirm new master password")
        layout.addWidget(self.current_password)
        layout.addWidget(self.new_password)
        layout.addWidget(self.confirm_password)

        self.error = QLabel("")
        self.error.setStyleSheet("color: #f87171;")
        self.error.setWordWrap(True)
        self.error.setVisible(False)
        layout.addWidget(self.error)

        submit = QPushButton("Change Master Password")
        submit.clicked.connect(self._submit)
        layout.addWidget(submit)
        self.current_password.setFocus()

    @staticmethod
    def _password_field(placeholder: str) -> QLineEdit:
        field = QLineEdit()
        field.setEchoMode(QLineEdit.EchoMode.Password)
        field.setPlaceholderText(placeholder)
        return field

    def _submit(self) -> None:
        current = self.current_password.text()
        replacement = self.new_password.text()
        confirmation = self.confirm_password.text()
        if not current:
            self._show_error("Enter the current master password.")
            return
        if not replacement:
            self._show_error("The new master password cannot be empty.")
            return
        if replacement != confirmation:
            self._show_error("The new master passwords do not match.")
            return
        try:
            self.service.change_master_password(current, replacement)
        except KeyPlusError as exc:
            self._show_error(str(exc))
            self.current_password.clear()
            self.current_password.setFocus()
            return
        self.accept()

    def _show_error(self, message: str) -> None:
        self.error.setText(message)
        self.error.setVisible(True)
