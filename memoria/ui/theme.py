"""Visual style: light, calm, Windows 11-like."""
from __future__ import annotations

ACCENT = "#2563EB"
ACCENT_HOVER = "#1D4ED8"
ACCENT_SOFT = "#E8EFFE"
OK = "#15803D"
OK_SOFT = "#E7F6EC"
WARN = "#B45309"
WARN_SOFT = "#FDF3E1"
DANGER = "#B91C1C"
DANGER_SOFT = "#FDECEC"
TEXT = "#1F2328"
MUTED = "#5E6670"
BORDER = "#E3E6EA"
BG = "#F4F5F7"
CARD = "#FFFFFF"
SIDEBAR = "#ECEEF2"

ICON_FONT = "Segoe Fluent Icons"
ICON_FONT_FALLBACK = "Segoe MDL2 Assets"

QSS = f"""
* {{ font-family: 'Segoe UI Variable Text', 'Segoe UI'; font-size: 10pt; color: {TEXT}; }}
QMainWindow, #content {{ background: {BG}; }}
#sidebar {{ background: {SIDEBAR}; border-right: 1px solid {BORDER}; }}
#appTitle {{ font-size: 15pt; font-weight: 600; }}
#libraryLabel {{ color: {MUTED}; font-size: 9pt; }}
#navGroup {{ color: {MUTED}; font-size: 8pt; font-weight: 600; letter-spacing: 1px; padding: 10px 14px 2px 14px; }}
QPushButton#nav {{ text-align: left; padding: 7px 12px; border: none; border-radius: 6px; background: transparent; }}
QPushButton#nav:hover {{ background: #E0E3E8; }}
QPushButton#nav:checked {{ background: {CARD}; font-weight: 600; color: {ACCENT}; }}
#pageTitle {{ font-size: 19pt; font-weight: 600; }}
#pageSubtitle {{ color: {MUTED}; font-size: 10pt; }}
#h2 {{ font-size: 12.5pt; font-weight: 600; }}
#muted {{ color: {MUTED}; }}
#small {{ color: {MUTED}; font-size: 9pt; }}
#card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; }}
#tile {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; }}
#tileValue {{ font-size: 18pt; font-weight: 600; }}
#tileLabel {{ color: {MUTED}; font-size: 9pt; }}
#trust {{ background: {OK_SOFT}; border: 1px solid #C7E9D2; border-radius: 8px; color: {OK}; padding: 8px 12px; }}
#warnBox {{ background: {WARN_SOFT}; border: 1px solid #F3D9A9; border-radius: 8px; color: {WARN}; padding: 8px 12px; }}
#dangerBox {{ background: {DANGER_SOFT}; border: 1px solid #F5C2C2; border-radius: 8px; color: {DANGER}; padding: 8px 12px; }}
#infoBox {{ background: {ACCENT_SOFT}; border: 1px solid #C9D8FB; border-radius: 8px; color: #1E3A8A; padding: 8px 12px; }}
QPushButton {{ background: {CARD}; border: 1px solid #CDD2D8; border-radius: 6px; padding: 6px 14px; min-height: 20px; }}
QPushButton:hover {{ background: #F0F2F5; }}
QPushButton:pressed {{ background: #E5E8EC; }}
QPushButton:disabled {{ color: #A0A6AD; background: #F4F5F7; border-color: #E3E6EA; }}
QPushButton#primary {{ background: {ACCENT}; color: white; border: 1px solid {ACCENT}; font-weight: 600; }}
QPushButton#primary:hover {{ background: {ACCENT_HOVER}; }}
QPushButton#primary:disabled {{ background: #9DB5F0; border-color: #9DB5F0; color: #EEF2FD; }}
QPushButton#danger {{ background: {DANGER}; color: white; border: 1px solid {DANGER}; font-weight: 600; }}
QPushButton#danger:disabled {{ background: #E9A9A9; border-color: #E9A9A9; }}
QPushButton#link {{ border: none; background: transparent; color: {ACCENT}; padding: 2px 4px; }}
QPushButton#link:hover {{ text-decoration: underline; }}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit {{ background: {CARD}; border: 1px solid #CDD2D8; border-radius: 6px; padding: 5px 8px; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QPlainTextEdit:focus {{ border: 1px solid {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QListView, QTreeView, QTableView, QListWidget, QTreeWidget, QTableWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; outline: none; }}
QTreeView::item, QTableView::item, QListWidget::item, QTreeWidget::item {{ padding: 4px; }}
QTreeView::item:selected, QTableView::item:selected, QListWidget::item:selected, QTreeWidget::item:selected {{ background: {ACCENT_SOFT}; color: {TEXT}; }}
QHeaderView::section {{ background: #F7F8FA; border: none; border-bottom: 1px solid {BORDER}; padding: 6px; color: {MUTED}; font-weight: 600; }}
QProgressBar {{ background: #E3E6EA; border: none; border-radius: 3px; height: 6px; text-align: center; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 3px; }}
#taskBar {{ background: {CARD}; border-top: 1px solid {BORDER}; }}
#toast {{ background: #1F2328; border-radius: 8px; }}
#toast QLabel {{ color: white; }}
#toast QPushButton {{ background: transparent; color: #93B4FF; border: none; font-weight: 600; }}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{ background: transparent; padding: 8px 14px; border: none; color: {MUTED}; }}
QTabBar::tab:selected {{ color: {ACCENT}; border-bottom: 2px solid {ACCENT}; font-weight: 600; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QCheckBox, QRadioButton {{ spacing: 6px; }}
QSplitter::handle {{ background: transparent; }}
QToolTip {{ background: #1F2328; color: white; border: none; padding: 6px; }}
QDialog {{ background: {CARD}; }}
QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #C4C9D0; border-radius: 4px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #A7AEB7; }}
QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: #C4C9D0; border-radius: 4px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
QMenu {{ background: {CARD}; border: 1px solid {BORDER}; padding: 4px; }}
QMenu::item {{ padding: 6px 18px; border-radius: 4px; }}
QMenu::item:selected {{ background: {ACCENT_SOFT}; }}
"""
