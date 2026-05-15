"""Society blue/gold/black PyQt theme."""

SOCIETY_QSS = """
QWidget {
    background-color: #05070D;
    color: #E8E6DD;
    font-family: "Segoe UI", "Inter", "Arial", sans-serif;
    font-size: 10pt;
}
QFrame, QGroupBox {
    background-color: #071A33;
    border: 1px solid #0B2D5C;
    border-radius: 8px;
    margin-top: 8px;
    padding: 8px;
}
QGroupBox::title {
    color: #D6A84F;
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    font-weight: 600;
}
QLabel#TitleLabel {
    color: #D6A84F;
    font-size: 18pt;
    font-weight: 700;
}
QLineEdit, QComboBox, QSpinBox {
    background-color: #0A1020;
    border: 1px solid #0B2D5C;
    border-radius: 5px;
    padding: 5px;
    color: #E8E6DD;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #D6A84F;
}
QPushButton {
    background-color: #0B2D5C;
    border: 1px solid #D6A84F;
    border-radius: 6px;
    padding: 7px 12px;
    color: #E8E6DD;
    font-weight: 600;
}
QPushButton:hover { background-color: #123D76; }
QPushButton:pressed { background-color: #071A33; }
QPushButton:disabled { color: #777; border-color: #444; background-color: #111827; }
QHeaderView::section {
    background-color: #071A33;
    color: #D6A84F;
    border: 1px solid #0B2D5C;
    padding: 5px;
}
QTableWidget, QTextEdit {
    background-color: #0A1020;
    border: 1px solid #0B2D5C;
    gridline-color: #0B2D5C;
}
QCheckBox { spacing: 6px; }
QProgressBar {
    border: 1px solid #0B2D5C;
    border-radius: 5px;
    text-align: center;
    background-color: #0A1020;
}
QProgressBar::chunk { background-color: #D6A84F; }
"""
