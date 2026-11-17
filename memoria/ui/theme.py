"""Visual style: light and dark palettes (Windows 11-like) and the Qt stylesheet built from them.

Call :func:`use` before creating widgets. Module attributes (``theme.ACCENT``…) always hold the
active palette, so widgets read colours when they are built. Switching theme rebuilds the window.
"""
from __future__ import annotations

ICON_FONT = "Segoe Fluent Icons"
ICON_FONT_FALLBACK = "Segoe MDL2 Assets"

# Badges keep the same strong colours in both themes (white text on top).
BADGE_OK = "#0F7B4F"
BADGE_WARN = "#A15C07"
BADGE_INFO = "#3557D6"
BADGE_MUTED = "#5D6676"

# A restrained, slate-neutral system with one indigo-blue accent. Status colours are muted, and
# solid danger fills are separate from danger text so destructive buttons never look garish.
PALETTES: dict[str, dict[str, str]] = {
    "light": {
        "ACCENT": "#3557D6", "ACCENT_HOVER": "#2B49BC", "ACCENT_PRESSED": "#233E9F", "ACCENT_SOFT": "#EDF1FD",
        "ACCENT_BORDER": "#D3DCF8", "INFO_TEXT": "#23367F",
        "OK": "#0F7B4F", "OK_SOFT": "#ECF7F1", "OK_BORDER": "#CDE9DA",
        "WARN": "#A15C07", "WARN_SOFT": "#FDF6E9", "WARN_BORDER": "#F0DEB8",
        "DANGER": "#B42318", "DANGER_SOFT": "#FDF0EF", "DANGER_BORDER": "#F4D0CC",
        "DANGER_SOLID": "#C4321F", "DANGER_SOLID_HOVER": "#A82A1A",
        "TEXT": "#161B26", "MUTED": "#5D6676", "BORDER": "#E4E7EC", "INPUT_BORDER": "#D0D5DD",
        "BG": "#F6F7F9", "CARD": "#FFFFFF", "SIDEBAR": "#F0F2F5", "NAV_HOVER": "#E6E9EE", "NAV_ACTIVE": "#FFFFFF",
        "HOVER": "#F3F5F8", "PRESSED": "#E9ECF1", "DISABLED_TEXT": "#9AA3AF", "DISABLED_BG": "#F4F5F7",
        "PRIMARY_DISABLED": "#AFBDEE", "PRIMARY_DISABLED_TEXT": "#F3F5FD", "DANGER_DISABLED": "#E8B6AF",
        "HEADER_BG": "#F9FAFB", "TRACK": "#E4E7EC", "TOAST_BG": "#1C2230", "TOAST_TEXT": "#FFFFFF",
        "TOAST_LINK": "#AFC0FF", "SCROLL": "#CDD2DA", "SCROLL_HOVER": "#AEB5C0", "PLACEHOLDER": "#EDEFF2",
        "PREVIEW_BG": "#F2F4F7", "SEGMENT_BG": "#EEF0F3", "SEGMENT_BORDER": "#D6DAE1", "SUBTLE": "#EEF0F3",
        "SELECTION_TEXT": "#161B26", "SHADOW": "#2E101828",
    },
    "dark": {
        "ACCENT": "#5476EE", "ACCENT_HOVER": "#6887F1", "ACCENT_PRESSED": "#4766DA", "ACCENT_SOFT": "#1C2440",
        "ACCENT_BORDER": "#2D3A63", "INFO_TEXT": "#C3D0FB",
        "OK": "#4CC38A", "OK_SOFT": "#12261D", "OK_BORDER": "#1E4332",
        "WARN": "#E9AE4B", "WARN_SOFT": "#29200F", "WARN_BORDER": "#4D3A17",
        "DANGER": "#F0857A", "DANGER_SOFT": "#2D1715", "DANGER_BORDER": "#532620",
        "DANGER_SOLID": "#C23A2C", "DANGER_SOLID_HOVER": "#D44A3B",
        "TEXT": "#E8EAEE", "MUTED": "#9AA2AE", "BORDER": "#2B2F36", "INPUT_BORDER": "#3A3F48",
        "BG": "#121418", "CARD": "#1A1D22", "SIDEBAR": "#16181C", "NAV_HOVER": "#22262C", "NAV_ACTIVE": "#1F2430",
        "HOVER": "#23272E", "PRESSED": "#2B3038", "DISABLED_TEXT": "#636A75", "DISABLED_BG": "#1A1D22",
        "PRIMARY_DISABLED": "#27325A", "PRIMARY_DISABLED_TEXT": "#8592BC", "DANGER_DISABLED": "#47231F",
        "HEADER_BG": "#1F2228", "TRACK": "#2B2F36", "TOAST_BG": "#262A31", "TOAST_TEXT": "#F2F3F5",
        "TOAST_LINK": "#9DB2FF", "SCROLL": "#3A3F48", "SCROLL_HOVER": "#4C525C", "PLACEHOLDER": "#23272E",
        "PREVIEW_BG": "#1F2228", "SEGMENT_BG": "#1F2228", "SEGMENT_BORDER": "#3A3F48", "SUBTLE": "#1F2228",
        "SELECTION_TEXT": "#E8EAEE", "SHADOW": "#80000000",
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
ACCENT = ACCENT_HOVER = ACCENT_PRESSED = ACCENT_SOFT = ACCENT_BORDER = INFO_TEXT = ""
OK = OK_SOFT = OK_BORDER = WARN = WARN_SOFT = WARN_BORDER = DANGER = DANGER_SOFT = DANGER_BORDER = ""
DANGER_SOLID = DANGER_SOLID_HOVER = NAV_ACTIVE = SHADOW = ""
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
#appTitle {{ font-size: 14pt; font-weight: 600; }}
#libraryLabel {{ color: {MUTED}; font-size: 9pt; }}
#navGroup {{ color: {MUTED}; font-size: 7.5pt; font-weight: 600; letter-spacing: 1px; padding: 10px 14px 3px 14px; }}
QPushButton#nav {{ text-align: left; padding: 6px 12px; border: 1px solid transparent; border-radius: 8px; background: transparent; }}
QPushButton#nav:hover {{ background: {NAV_HOVER}; }}
QPushButton#nav:checked {{ background: {NAV_ACTIVE}; border-color: {BORDER}; font-weight: 600; color: {ACCENT}; }}
#navBadge {{ background: {ACCENT_SOFT}; color: {ACCENT}; border-radius: 9px; padding: 0 7px; font-size: 8pt; font-weight: 600; }}
QPushButton#sideMenu {{ text-align: left; padding: 6px 10px; border: 1px solid transparent; border-radius: 8px; background: transparent; color: {MUTED}; }}
QPushButton#sideMenu:hover {{ background: {NAV_HOVER}; color: {TEXT}; }}
QPushButton#sideMenu:disabled {{ color: {DISABLED_TEXT}; background: transparent; }}
QPushButton#sideMenu::menu-indicator {{ image: none; width: 0; }}
#pageTitle {{ font-size: 18pt; font-weight: 600; }}
#pageSubtitle {{ color: {MUTED}; font-size: 10pt; }}
#h2 {{ font-size: 12pt; font-weight: 600; }}
#muted {{ color: {MUTED}; }}
#small {{ color: {MUTED}; font-size: 9pt; }}
#card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}
#tile {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}
#tileValue {{ font-size: 18pt; font-weight: 600; }}
#tileLabel {{ color: {MUTED}; font-size: 9pt; }}
#trust {{ background: {OK_SOFT}; border: 1px solid {OK_BORDER}; border-radius: 10px; color: {OK}; padding: 9px 13px; }}
#warnBox {{ background: {WARN_SOFT}; border: 1px solid {WARN_BORDER}; border-radius: 10px; color: {WARN}; padding: 9px 13px; }}
#dangerBox {{ background: {DANGER_SOFT}; border: 1px solid {DANGER_BORDER}; border-radius: 10px; color: {DANGER}; padding: 9px 13px; }}
#infoBox {{ background: {ACCENT_SOFT}; border: 1px solid {ACCENT_BORDER}; border-radius: 10px; color: {INFO_TEXT}; padding: 9px 13px; }}
#selectionBar {{ background: {ACCENT_SOFT}; border: 1px solid {ACCENT_BORDER}; border-radius: 10px; }}
QPushButton {{ background: {CARD}; border: 1px solid {INPUT_BORDER}; border-radius: 8px; padding: 6px 14px; min-height: 20px; }}
QPushButton:hover {{ background: {HOVER}; border-color: {SEGMENT_BORDER}; }}
QPushButton:pressed {{ background: {PRESSED}; }}
QPushButton:disabled {{ color: {DISABLED_TEXT}; background: {DISABLED_BG}; border-color: {BORDER}; }}
QPushButton#primary {{ background: {ACCENT}; color: white; border: 1px solid {ACCENT}; font-weight: 600; }}
QPushButton#primary:hover {{ background: {ACCENT_HOVER}; border-color: {ACCENT_HOVER}; }}
QPushButton#primary:pressed {{ background: {ACCENT_PRESSED}; border-color: {ACCENT_PRESSED}; }}
QPushButton#primary:disabled {{ background: {PRIMARY_DISABLED}; border-color: {PRIMARY_DISABLED}; color: {PRIMARY_DISABLED_TEXT}; }}
QPushButton#danger {{ background: {DANGER_SOLID}; color: white; border: 1px solid {DANGER_SOLID}; font-weight: 600; }}
QPushButton#danger:hover {{ background: {DANGER_SOLID_HOVER}; border-color: {DANGER_SOLID_HOVER}; }}
QPushButton#danger:disabled {{ background: {DANGER_DISABLED}; border-color: {DANGER_DISABLED}; }}
QPushButton#link {{ border: none; background: transparent; color: {ACCENT}; padding: 2px 4px; }}
QPushButton#link:hover {{ color: {ACCENT_HOVER}; text-decoration: underline; }}
QPushButton#link:disabled {{ color: {DISABLED_TEXT}; background: transparent; }}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit {{ background: {CARD}; border: 1px solid {INPUT_BORDER}; border-radius: 8px; padding: 5px 9px; }}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {{ border-color: {SCROLL_HOVER}; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QPlainTextEdit:focus {{ border: 1px solid {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{ background: {CARD}; border: 1px solid {BORDER}; padding: 4px; selection-background-color: {ACCENT_SOFT}; selection-color: {SELECTION_TEXT}; }}
QListView, QTreeView, QTableView, QListWidget, QTreeWidget, QTableWidget {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; outline: none; }}
QTreeView::item, QTableView::item, QListWidget::item, QTreeWidget::item {{ padding: 5px 4px; }}
QTreeView::item:hover, QListWidget::item:hover, QTreeWidget::item:hover {{ background: {HOVER}; }}
QTreeView::item:selected, QTableView::item:selected, QListWidget::item:selected, QTreeWidget::item:selected {{ background: {ACCENT_SOFT}; color: {SELECTION_TEXT}; }}
QHeaderView::section {{ background: {HEADER_BG}; border: none; border-bottom: 1px solid {BORDER}; padding: 7px 6px; color: {MUTED}; font-weight: 600; font-size: 9pt; }}
QTableCornerButton::section {{ background: {HEADER_BG}; border: none; }}
QProgressBar {{ background: {TRACK}; border: none; border-radius: 3px; height: 6px; text-align: center; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 3px; }}
QSlider::groove:horizontal {{ height: 4px; background: {TRACK}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {CARD}; border: 2px solid {ACCENT}; width: 12px; height: 12px; margin: -6px 0; border-radius: 8px; }}
#taskBar {{ background: {CARD}; border-top: 1px solid {BORDER}; }}
#toast {{ background: {TOAST_BG}; border: 1px solid {BORDER}; border-radius: 12px; }}
#toast QLabel {{ color: {TOAST_TEXT}; }}
#toast QPushButton {{ background: transparent; color: {TOAST_LINK}; border: none; font-weight: 600; }}
#toast QPushButton:hover {{ text-decoration: underline; }}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{ background: transparent; padding: 8px 14px; border: none; border-bottom: 2px solid transparent; color: {MUTED}; }}
QTabBar::tab:hover {{ color: {TEXT}; }}
QTabBar::tab:selected {{ color: {ACCENT}; border-bottom: 2px solid {ACCENT}; font-weight: 600; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QCheckBox, QRadioButton {{ spacing: 7px; }}
QSplitter::handle {{ background: transparent; }}
QToolTip {{ background: {TOAST_BG}; color: {TOAST_TEXT}; border: 1px solid {BORDER}; padding: 6px 8px; }}
QMenu {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; padding: 5px; }}
QMenu::item {{ padding: 7px 22px 7px 14px; border-radius: 6px; }}
QMenu::item:selected {{ background: {ACCENT_SOFT}; color: {SELECTION_TEXT}; }}
QMenu::item:disabled {{ color: {DISABLED_TEXT}; }}
QMenu::separator {{ height: 1px; background: {BORDER}; margin: 5px 8px; }}
QDialog {{ background: {CARD}; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {SCROLL}; border-radius: 3px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {SCROLL_HOVER}; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {SCROLL}; border-radius: 3px; min-width: 30px; }}
QScrollBar::handle:horizontal:hover {{ background: {SCROLL_HOVER}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
"""


use("light")
