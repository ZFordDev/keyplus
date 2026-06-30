# src/ui/gui/view_entry.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt
from logic import vault


def build_view_entry(entry_id, on_back):
    """
    Shows details for a single vault entry.
    Takes on_back callback to handle navigation back to the dashboard.
    """
    entry = vault.get_entry(entry_id)

    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)

    # --- TOP BAR & NAVIGATION ---
    top_bar = QHBoxLayout()
    
    back_btn = QPushButton("← Back")
    back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    back_btn.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            color: #94a3b8;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #1e293b;
            color: #f1f5f9;
        }
    """)
    back_btn.clicked.connect(on_back)
    top_bar.addWidget(back_btn)
    top_bar.addStretch()
    layout.addLayout(top_bar)

    # Error handling state
    if not entry:
        error_box = QWidget()
        error_box.setStyleSheet("background-color: #2d1e24; border: 1px solid #7f1d1d; border-radius: 8px;")
        err_layout = QVBoxLayout(error_box)
        
        msg = QLabel("⚠️ Entry not found or has been deleted.")
        msg.setStyleSheet("color: #f87171; font-weight: 500;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        err_layout.addWidget(msg)
        
        layout.addWidget(error_box)
        layout.addStretch()
        return widget

    # --- TITLE SECTION ---
    header = QWidget()
    header_layout = QVBoxLayout(header)
    header_layout.setContentsMargins(0, 4, 0, 8)
    header_layout.setSpacing(4)

    title = QLabel(entry["name"])
    title.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: 700;")
    header_layout.addWidget(title)
    
    layout.addLayout(header_layout)

    # --- DATA CARD LAYER ---
    card = QWidget()
    card.setStyleSheet("""
        QWidget {
            background-color: #1a2234;
            border: 1px solid #2d3748;
            border-radius: 8px;
        }
        QLabel {
            color: #64748b;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            border: none;
        }
        QLineEdit {
            background-color: #121824;
            border: 1px solid #242f47;
            border-radius: 6px;
            padding: 8px 12px;
            color: #f8fafc;
            font-size: 14px;
        }
    """)
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(18, 18, 18, 18)
    card_layout.setSpacing(14)

    # Domain Row
    dom_layout = QVBoxLayout()
    dom_layout.setSpacing(6)
    dom_label = QLabel("Domain")
    dom_val = QLineEdit(entry['domain'])
    dom_val.setReadOnly(True) # Makes it selectable and copyable, but uneditable
    dom_layout.addWidget(dom_label)
    dom_layout.addWidget(dom_val)
    card_layout.addLayout(dom_layout)

    # Password Row
    pw_layout = QVBoxLayout()
    pw_layout.setSpacing(6)
    pw_label = QLabel("Password")
    pw_val = QLineEdit(entry['password'])
    pw_val.setReadOnly(True)
    pw_layout.addWidget(pw_label)
    pw_layout.addWidget(pw_val)
    card_layout.addLayout(pw_layout)

    layout.addWidget(card)

    # --- FOOTER METADATA ---
    meta_widget = QWidget()
    meta_layout = QVBoxLayout(meta_widget)
    meta_layout.setContentsMargins(4, 0, 4, 0)
    meta_layout.setSpacing(4)

    created = QLabel(f"Created: {entry['created']}")
    created.setStyleSheet("color: #475569; font-size: 12px;")
    meta_layout.addWidget(created)

    if entry.get("updated") and entry["updated"] != entry["created"]:
        updated = QLabel(f"Last Modified: {entry['updated']}")
        updated.setStyleSheet("color: #475569; font-size: 12px;")
        meta_layout.addWidget(updated)

    layout.addLayout(meta_layout)
    layout.addStretch()

    return widget