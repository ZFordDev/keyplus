# src/ui/gui/add_entry.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QWidget
)
from PySide6.QtCore import Qt
from logic import vault

# Matching modal specific layout styles
MODAL_DARK_STYLE = """
QDialog {
    background-color: #121824;
}
QLabel {
    color: #94a3b8;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    font-weight: 500;
}
QLineEdit {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f8fafc;
    font-size: 14px;
}
QLineEdit:focus {
    border: 1px solid #2563eb;
}
"""

class AddEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Entry")
        self.setModal(True)
        self.resize(380, 380) # Increased height slightly for layout breathing room
        self.setStyleSheet(MODAL_DARK_STYLE)

        # Remove default native context help buttons from titlebar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # --- HEADER ---
        title = QLabel("Add New Entry")
        title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 600;")
        layout.addWidget(title)
        
        # --- INPUT FORM FIELDS ---
        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)

        # Name Field Combo
        name_label = QLabel("Entry Name")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Google, GitHub")
        self.name_input.setFixedHeight(38)
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)

        # Domain Field Combo
        domain_label = QLabel("Domain")
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("e.g., google.com")
        self.domain_input.setFixedHeight(38)
        form_layout.addWidget(domain_label)
        form_layout.addWidget(self.domain_input)

        # Password Field Combo
        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("••••••••••••")
        self.password_input.setFixedHeight(38)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)

        layout.addLayout(form_layout)

        # --- DYNAMIC ERROR LABEL ---
        self.error = QLabel("")
        self.error.setStyleSheet("color: #f87171; font-size: 13px; font-weight: 500;")
        self.error.setWordWrap(True)
        self.error.setVisible(False)
        layout.addWidget(self.error)

        layout.addStretch()

        # --- ACTION BUTTONS ROW ---
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(38)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: #f1f5f9;
            }
        """)

        add_btn = QPushButton("Save Entry")
        add_btn.setFixedHeight(38)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(add_btn)
        layout.addLayout(btn_row)

        cancel_btn.clicked.connect(self.reject)
        add_btn.clicked.connect(self._handle_add)

        self.result_entry = None
        self.name_input.setFocus()

    def _handle_add(self):
        name = self.name_input.text().strip()
        domain = self.domain_input.text().strip()
        password = self.password_input.text().strip()

        if not name or not domain or not password:
            self.error.setText("⚠️ All fields are required.")
            self.error.setVisible(True)
            return

        self.error.setVisible(False)
        entry = vault.add_entry(name, domain, password)
        self.result_entry = entry
        self.accept()