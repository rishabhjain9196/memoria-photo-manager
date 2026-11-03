"""Visual style: light and dark palettes (Windows 11-like) and the Qt stylesheet built from them.

Call :func:`use` before creating widgets. Module attributes (``theme.ACCENT``…) always hold the
active palette, so widgets read colours when they are built. Switching theme rebuilds the window.
"""
from __future__ import annotations

ICON_FONT = "Segoe Fluent Icons"
ICON_FONT_FALLBACK = "Segoe MDL2 Assets"

# Badges keep the same strong colours in both themes (white text on top).
BADGE_OK = "#15803D"
BADGE_WARN = "#B45309"
BADGE_INFO = "#2563EB"
BADGE_MUTED = "#6B7280"

PALETTES: dict[str, dict[str, str]] = {
    "light": {
        "ACCENT": "#2563EB", "ACCENT_HOVER": "#1D4ED8", "ACCENT_SOFT": "#E8EFFE", "ACCENT_BORDER": "#C9D8FB",
        "INFO_TEXT": "#1E3A8A",
        "OK": "#15803D", "OK_SOFT": "#E7F6EC", "OK_BORDER": "#C7E9D2",
        "WARN": "#B45309", "WARN_SOFT": "#FDF3E1", "WARN_BORDER": "#F3D9A9",
        "DANGER": "#B91C1C", "DANGER_SOFT": "#FDECEC", "DANGER_BORDER": "#F5C2C2",
        "TEXT": "#1F2328", "MUTED": "#5E6670", "BORDER": "#E3E6EA", "INPUT_BORDER": "#CDD2D8",
        "BG": "#F4F5F7", "CARD": "#FFFFFF", "SIDEBAR": "#ECEEF2", "NAV_HOVER": "#E0E3E8",
        "HOVER": "#F0F2F5", "PRESSED": "#E5E8EC", "DISABLED_TEXT": "#A0A6AD", "DISABLED_BG": "#F4F5F7",
        "PRIMARY_DISABLED": "#9DB5F0", "PRIMARY_DISABLED_TEXT": "#EEF2FD", "DANGER_DISABLED": "#E9A9A9",
        "HEADER_BG": "#F7F8FA", "TRACK": "#E3E6EA", "TOAST_BG": "#1F2328", "TOAST_TEXT": "#FFFFFF",
        "TOAST_LINK": "#93B4FF", "SCROLL": "#C4C9D0", "SCROLL_HOVER": "#A7AEB7", "PLACEHOLDER": "#E9EBEF",
        "PREVIEW_BG": "#F0F2F5", "SEGMENT_BG": "#EBEDF0", "SEGMENT_BORDER": "#D5D9DF", "SUBTLE": "#ECEEF1",
        "SELECTION_TEXT": "#1F2328",
    },
    "dark": {
        "ACCENT": "#4C8DFF", "ACCENT_HOVER": "#6AA0FF", "ACCENT_SOFT": "#1E2D4A", "ACCENT_BORDER": "#2C4470",
        "INFO_TEXT": "#BFD4FF",
        "OK": "#4ADE80", "OK_SOFT": "#14291C", "OK_BORDER": "#1F4A2E",
        "WARN": "#F5B454", "WARN_SOFT": "#30250F", "WARN_BORDER": "#5A4217",
        "DANGER": "#F87171", "DANGER_SOFT": "#361919", "DANGER_BORDER": "#5C2626",
        "TEXT": "#E6E8EB", "MUTED": "#A1A7B0", "BORDER": "#34373D", "INPUT_BORDER": "#464A52",
        "BG": "#1B1C20", "CARD": "#24262B", "SIDEBAR": "#1F2024", "NAV_HOVER": "#2B2D33",
        "HOVER": "#2D3036", "PRESSED": "#353840", "DISABLED_TEXT": "#6B7079", "DISABLED_BG": "#222428",
        "PRIMARY_DISABLED": "#2C3E66", "PRIMARY_DISABLED_TEXT": "#8FA3C7", "DANGER_DISABLED": "#5C2B2B",
        "HEADER_BG": "#2A2C31", "TRACK": "#34373D", "TOAST_BG": "#0E0F12", "TOAST_TEXT": "#F2F3F5",
        "TOAST_LINK": "#93B4FF", "SCROLL": "#4A4E56", "SCROLL_HOVER": "#5E636C", "PLACEHOLDER": "#2E3036",
        "PREVIEW_BG": "#2A2C31", "SEGMENT_BG": "#2A2C31", "SEGMENT_BORDER": "#464A52", "SUBTLE": "#2A2C31",
        "SELECTION_TEXT": "#E6E8EB",
    },
}

MODES = {"system": "Match Windows", "light": "Light", "dark": "Dark"}


def settings():
    """App settings. ``MEMORIA_PROFILE`` keeps tests and tools out of the user's real settings."""
    import os
    from PySide6.QtCore import QSettings
    return QSettings("Memoria", os.environ.get("MEMORIA_PROFILE", "Memoria"))

MODE = "light"     # what the user chose: system | light | dark
NAME = "light"     # what is applied: light | dark
QSS = ""

# Populated by use(); listed here for editors and type checkers.
ACCENT = ACCENT_HOVER = ACCENT_SOFT = ACCENT_BORDER = INFO_TEXT = ""
OK = OK_SOFT = OK_BORDER = WARN = WARN_SOFT = WARN_BORDER = DANGER = DANGER_SOFT = DANGER_BORDER = ""
TEXT = MUTED = BORDER = INPUT_BORDER = BG = CARD = SIDEBAR = NAV_HOVER = HOVER = PRESSED = ""
DISABLED_TEXT = DISABLED_BG = PRIMARY_DISABLED = PRIMARY_DISABLED_TEXT = DANGER_DISABLED = ""
HEADER_BG = TRACK = TOAST_BG = TOAST_TEXT = TOAST_LINK = SCROLL = SCROLL_HOVER = PLACEHOLDER = ""
PREVIEW_BG = SEGMENT_BG = SEGMENT_BORDER = SUBTLE = SELECTION_TEXT = ""


def system_prefers_dark() -> bool:
    """Ask Qt whether the operating system is using a dark colour scheme."""
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QGuiApplication
        app = QGuiApplication.instance()
        if app is not None:
            return app.styleHints().colorScheme() == Qt.ColorScheme.Dark
    except Exception:
        pass
    return False


def use(mode: str = "light") -> str:
    """Activate a theme mode (system | light | dark). Returns the applied palette name."""
    global MODE, NAME, QSS
    MODE = mode if mode in MODES else "light"
    NAME = ("dark" if system_prefers_dark() else "light") if MODE == "system" else MODE
    globals().update(PALETTES[NAME])
    QSS = _build_qss()
    return NAME


def qpalette():
    """A QPalette matching the active theme, for native parts that ignore the stylesheet."""
    from PySide6.QtGui import QColor, QPalette
    p = QPalette()
    R = QPalette.ColorRole
    for role, color in ((R.Window, BG), (R.WindowText, TEXT), (R.Base, CARD), (R.AlternateBase, HEADER_BG),
                        (R.Text, TEXT), (R.Button, CARD), (R.ButtonText, TEXT), (R.ToolTipBase, TOAST_BG),
                        (R.ToolTipText, TOAST_TEXT), (R.Highlight, ACCENT), (R.HighlightedText, "#FFFFFF"),
                        (R.PlaceholderText, MUTED), (R.Link, ACCENT), (R.Mid, BORDER), (R.Dark, INPUT_BORDER)):
        p.setColor(role, QColor(color))
    for role in (R.Text, R.WindowText, R.ButtonText):
        p.setColor(QPalette.ColorGroup.Disabled, role, QColor(DISABLED_TEXT))
    return p


def badge_colors(kind: str) -> tuple[str, str]:
    return {"keep": (BADGE_OK, "white"), "best": (BADGE_OK, "white"), "warn": (BADGE_WARN, "white"),
            "info": (BADGE_INFO, "white"), "muted": (BADGE_MUTED, "white")}.get(kind, (BADGE_INFO, "white"))


def _build_qss() -> str:
    return f"""
* {{ font-family: 'Segoe UI Variable Text', 'Segoe UI'; font-size: 10pt; color: {TEXT}; }}
QMainWindow, #content {{ background: {BG}; }}
#sidebar {{ background: {SIDEBAR}; border-right: 1px solid {BORDER}; }}
#appTitle {{ font-size: 15pt; font-weight: 600; }}
#libraryLabel {{ color: {MUTED}; font-size: 9pt; }}
#navGroup {{ color: {MUTED}; font-size: 8pt; font-weight: 600; letter-spacing: 1px; padding: 10px 14px 2px 14px; }}
QPushButton#nav {{ text-align: left; padding: 7px 12px; border: none; border-radius: 6px; background: transparent; }}
QPushButton#nav:hover {{ background: {NAV_HOVER}; }}
QPushButton#nav:checked {{ background: {CARD}; font-weight: 600; color: {ACCENT}; }}
#navBadge {{ background: {ACCENT_SOFT}; color: {ACCENT}; border-radius: 9px; padding: 0 7px; font-size: 8pt; font-weight: 600; }}
#pageTitle {{ font-size: 19pt; font-weight: 600; }}
#pageSubtitle {{ color: {MUTED}; font-size: 10pt; }}
#h2 {{ font-size: 12.5pt; font-weight: 600; }}
#muted {{ color: {MUTED}; }}
#small {{ color: {MUTED}; font-size: 9pt; }}
#card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; }}
#tile {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; }}
#tileValue {{ font-size: 18pt; font-weight: 600; }}
#tileLabel {{ color: {MUTED}; font-size: 9pt; }}
#trust {{ background: {OK_SOFT}; border: 1px solid {OK_BORDER}; border-radius: 8px; color: {OK}; padding: 8px 12px; }}
#warnBox {{ background: {WARN_SOFT}; border: 1px solid {WARN_BORDER}; border-radius: 8px; color: {WARN}; padding: 8px 12px; }}
#dangerBox {{ background: {DANGER_SOFT}; border: 1px solid {DANGER_BORDER}; border-radius: 8px; color: {DANGER}; padding: 8px 12px; }}
#infoBox {{ background: {ACCENT_SOFT}; border: 1px solid {ACCENT_BORDER}; border-radius: 8px; color: {INFO_TEXT}; padding: 8px 12px; }}
#selectionBar {{ background: {ACCENT_SOFT}; border: 1px solid {ACCENT_BORDER}; border-radius: 8px; }}
QPushButton {{ background: {CARD}; border: 1px solid {INPUT_BORDER}; border-radius: 6px; padding: 6px 14px; min-height: 20px; }}
QPushButton:hover {{ background: {HOVER}; }}
QPushButton:pressed {{ background: {PRESSED}; }}
QPushButton:disabled {{ color: {DISABLED_TEXT}; background: {DISABLED_BG}; border-color: {BORDER}; }}
QPushButton#primary {{ background: {ACCENT}; color: white; border: 1px solid {ACCENT}; font-weight: 600; }}
QPushButton#primary:hover {{ background: {ACCENT_HOVER}; }}
QPushButton#primary:disabled {{ background: {PRIMARY_DISABLED}; border-color: {PRIMARY_DISABLED}; color: {PRIMARY_DISABLED_TEXT}; }}
QPushButton#danger {{ background: {DANGER}; color: white; border: 1px solid {DANGER}; font-weight: 600; }}
QPushButton#danger:disabled {{ background: {DANGER_DISABLED}; border-color: {DANGER_DISABLED}; }}
QPushButton#link {{ border: none; background: transparent; color: {ACCENT}; padding: 2px 4px; }}
QPushButton#link:hover {{ text-decoration: underline; }}
QPushButton#link:disabled {{ color: {DISABLED_TEXT}; background: transparent; }}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit {{ background: {CARD}; border: 1px solid {INPUT_BORDER}; border-radius: 6px; padding: 5px 8px; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QPlainTextEdit:focus {{ border: 1px solid {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{ background: {CARD}; border: 1px solid {BORDER}; selection-background-color: {ACCENT_SOFT}; selection-color: {SELECTION_TEXT}; }}
QListView, QTreeView, QTableView, QListWidget, QTreeWidget, QTableWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; outline: none; }}
QTreeView::item, QTableView::item, QListWidget::item, QTreeWidget::item {{ padding: 4px; }}
QTreeView::item:selected, QTableView::item:selected, QListWidget::item:selected, QTreeWidget::item:selected {{ background: {ACCENT_SOFT}; color: {SELECTION_TEXT}; }}
QHeaderView::section {{ background: {HEADER_BG}; border: none; border-bottom: 1px solid {BORDER}; padding: 6px; color: {MUTED}; font-weight: 600; }}
QTableCornerButton::section {{ background: {HEADER_BG}; border: none; }}
QProgressBar {{ background: {TRACK}; border: none; border-radius: 3px; height: 6px; text-align: center; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 3px; }}
QSlider::groove:horizontal {{ height: 4px; background: {TRACK}; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {ACCENT}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }}
#taskBar {{ background: {CARD}; border-top: 1px solid {BORDER}; }}
#toast {{ background: {TOAST_BG}; border: 1px solid {BORDER}; border-radius: 8px; }}
#toast QLabel {{ color: {TOAST_TEXT}; }}
#toast QPushButton {{ background: transparent; color: {TOAST_LINK}; border: none; font-weight: 600; }}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{ background: transparent; padding: 8px 14px; border: none; color: {MUTED}; }}
QTabBar::tab:selected {{ color: {ACCENT}; border-bottom: 2px solid {ACCENT}; font-weight: 600; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QCheckBox, QRadioButton {{ spacing: 6px; }}
QSplitter::handle {{ background: transparent; }}
QToolTip {{ background: {TOAST_BG}; color: {TOAST_TEXT}; border: 1px solid {BORDER}; padding: 6px; }}
QMenu {{ background: {CARD}; border: 1px solid {BORDER}; padding: 4px; }}
QMenu::item {{ padding: 6px 18px; border-radius: 4px; }}
QMenu::item:selected {{ background: {ACCENT_SOFT}; color: {SELECTION_TEXT}; }}
QMenu::separator {{ height: 1px; background: {BORDER}; margin: 4px 8px; }}
QDialog {{ background: {CARD}; }}
QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {SCROLL}; border-radius: 4px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {SCROLL_HOVER}; }}
QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {SCROLL}; border-radius: 4px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
"""


use("light")
