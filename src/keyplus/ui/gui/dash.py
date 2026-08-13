# KeyPlus GUI dashboard
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def build_dashboard(
    service, on_view_entry, on_add_entry, on_backup, on_change_password, on_logout
):
    """
    Dashboard showing all vault entries.
    Calls on_view_entry(entry_id) when an entry is clicked.
    Calls on_add_entry() when Add Entry is pressed.
    Calls on_logout() when Logout is pressed.
    """
    widget = QWidget()

    # Primary view layout matching our margins
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(24)

    # --- MODERN TOP HEADER BAR ---
    header_widget = QWidget()
    header_layout = QHBoxLayout(header_widget)
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(8)  # Tight spacing between action buttons

    # Title Left-aligned
    title = QLabel("Vault")
    title.setStyleSheet("color: #ffffff; font-size: 22px; font-weight: 700;")
    header_layout.addWidget(title)

    header_layout.addStretch()

    # Manual Logout Button (Destructive/Outline Style)
    logout_btn = QPushButton("Logout")
    logout_btn.setFixedHeight(36)
    logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    logout_btn.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            color: #ef4444;
            font-size: 13px;
            font-weight: 600;
            padding: 0px 14px;
            border-radius: 6px;
            border: 1px solid #ef4444;
        }
        QPushButton:hover {
            background-color: #fca5a5;
            color: #991b1b;
        }
    """)
    logout_btn.clicked.connect(on_logout)
    header_layout.addWidget(logout_btn)

    # Styled Primary Action Button Right-aligned
    add_btn = QPushButton("+ Add Entry")
    add_btn.setFixedHeight(36)
    add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    add_btn.setStyleSheet("""
        QPushButton {
            background-color: #2563eb;
            color: #ffffff;
            font-size: 13px;
            font-weight: 600;
            padding: 0px 16px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #1d4ed8;
        }
    """)
    add_btn.clicked.connect(on_add_entry)
    header_layout.addWidget(add_btn)

    layout.addWidget(header_widget)

    vault_actions = QHBoxLayout()
    backup_btn = QPushButton("Create Backup")
    backup_btn.setFixedHeight(36)
    backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    backup_btn.clicked.connect(on_backup)
    vault_actions.addWidget(backup_btn)

    password_btn = QPushButton("Change Password")
    password_btn.setFixedHeight(36)
    password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    password_btn.clicked.connect(on_change_password)
    vault_actions.addWidget(password_btn)
    layout.addLayout(vault_actions)

    # --- ENTRIES LIST SECTION ---
    entries = service.list_entries()

    # Empty State Layout
    if not entries:
        empty_container = QWidget()
        empty_layout = QVBoxLayout(empty_container)
        empty_layout.setContentsMargins(0, 40, 0, 0)
        empty_layout.setSpacing(12)

        icon_label = QLabel("📂")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 40px;")
        empty_layout.addWidget(icon_label)

        empty_msg = QLabel("Your vault is completely empty.")
        empty_msg.setStyleSheet("color: #64748b; font-size: 14px; font-weight: 500;")
        empty_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_msg)

        subtitle_msg = QLabel(
            "Click '+ Add Entry' above to save your first password securely."
        )
        subtitle_msg.setStyleSheet("color: #475569; font-size: 12px;")
        subtitle_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(subtitle_msg)

        layout.addWidget(empty_container)
        layout.addStretch()
        return widget

    # Refined Modern List Widget
    list_widget = QListWidget()
    list_widget.setCursor(Qt.CursorShape.PointingHandCursor)
    list_widget.setStyleSheet("""
        QListWidget {
            background-color: #1a2234;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 6px;
            outline: 0;
        }
        QListWidget::item {
            color: #f1f5f9;
            background-color: transparent;
            border-bottom: 1px solid #242f47;
            padding: 14px 16px;
            border-radius: 4px;
        }
        QListWidget::item:last {
            border-bottom: none; /* Clean separation line removal for last entry */
        }
        QListWidget::item:hover {
            background-color: #24304a;
            color: #ffffff;
        }
        QListWidget::item:selected {
            background-color: #2563eb;
            color: #ffffff;
        }
    """)

    # Populate the rows elegantly
    for e in entries:
        # Construct clean label spacing
        display_text = f"{e.name}  ·  {e.domain}"
        item = QListWidgetItem(display_text)
        item.setData(Qt.UserRole, e.id)
        list_widget.addItem(item)

    def handle_click(item):
        entry_id = item.data(Qt.UserRole)
        on_view_entry(entry_id)

    list_widget.itemClicked.connect(handle_click)
    layout.addWidget(list_widget)

    return widget
