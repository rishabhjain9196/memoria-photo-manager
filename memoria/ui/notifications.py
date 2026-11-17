"""Generic local notifications: desktop when requested, bounded in-app history always available."""
import logging
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, Qt, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QHeaderView, QMenu,
                               QStyle, QSystemTrayIcon, QTreeWidget, QTreeWidgetItem)

from .motion import Dialog
from .widgets import button, hbox, label, vbox

MODES = {"background": "Desktop only when Memoria is in the background",
         "always": "Always show desktop notifications",
         "in-app": "In-app notifications only", "off": "Off (existing safety dialogs and Undo toasts remain)"}
CATEGORIES = {"index": "Indexing or rebuild completed",
              "completed": "Utilities, cleanup, export, compression or sync completed",
              "problems": "Tasks failed or some items could not be processed",
              "health": "Health check found problems",
              "cancelled": "Task cancelled or rebuild paused"}
# Only these fixed messages reach the OS; never interpolate task titles, filenames or exceptions.
EVENTS = {
    "index_complete": ("index", "Library indexing finished", "Open Photos & videos to browse the completed catalogue.", False),
    "rebuild_complete": ("index", "Library rebuild finished", "The catalogue rebuild finished. Originals and Recovery were kept.", False),
    "index_issues": ("problems", "Indexing needs attention", "Some files or folders could not be read. Open Memoria to review.", True),
    "results_ready": ("completed", "Analysis results are ready", "Open Memoria to review the results. No cleanup was applied.", False),
    "operation_complete": ("completed", "File operation completed", "Review the recorded changes in History & recovery.", False),
    "export_complete": ("completed", "Export completed", "The output is ready. Open Memoria to review its results.", False),
    "compression_complete": ("completed", "Video compression finished", "Open Video compressor to review the saved copies and quality results.", False),
    "edits_complete": ("completed", "Edited copies are ready", "New copies were saved. Originals were not edited in place.", False),
    "story_complete": ("completed", "Story export finished", "Open Story maker to find the exported output.", False),
    "operation_partial": ("problems", "Some items need attention", "Some items failed or were skipped. Open Memoria to review the details.", True),
    "task_failed": ("problems", "A task did not finish", "Open Memoria for the error details. Some steps may have completed.", True),
    "rebuild_failed": ("problems", "Library rebuild needs attention", "Use Resume rebuild to retry safely. You can skip shrinking if space is low.", True),
    "diagnostics_failed": ("problems", "Diagnostic report not saved", "Open Diagnostics for details. Any previous report remains available.", True),
    "health_problems": ("health", "Health check found problems", "Open Health check to review missing, unreadable or possibly damaged files.", True),
    "task_cancelled": ("cancelled", "Task stopped", "Open Memoria to review the task status and any completed work.", False),
    "index_paused": ("cancelled", "Indexing stopped", "Saved analysis is kept. Press F5 in Memoria to resume.", False),
    "rebuild_paused": ("cancelled", "Library rebuild paused", "Use Resume rebuild or reopen the library. Already-cleared catalogue data is not restored by cancellation.", True),
}


class NotificationManager(QObject):
    changed = Signal()
    restore_requested = Signal()
    settings_requested = Signal()

    def __init__(self, owner, settings, *, foreground=None, tray=None):
        super().__init__(owner)
        self.owner, self.settings = owner, settings
        self.recent = []
        self.unread = 0
        self._closed = False
        self._foreground = foreground or self._is_foreground
        self.mode = settings.value("notifications_mode", "background")
        if self.mode not in MODES:
            logging.getLogger(__name__).warning("Unknown notification preference; using background delivery")
            self.mode = "background"
        saved = settings.value("notifications_events", list(CATEGORIES), list) or []
        self.enabled_events = set(saved) & CATEGORIES.keys()
        self.tray = tray if tray is not None else self._native_tray()
        if self.tray is not None:
            icon = owner.windowIcon()
            if icon.isNull():
                icon = QIcon(str(Path(__file__).parent / "assets" / "memoria.png"))
            if icon.isNull():
                icon = owner.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
            self.tray.setIcon(icon)
            self.tray.setToolTip("Memoria")
            self.tray.messageClicked.connect(self.restore_requested.emit)
            self.tray.activated.connect(self._activated)
            menu = QMenu(owner)
            menu.addAction("Open Memoria", self.restore_requested.emit)
            menu.addAction("Notification settings", self.settings_requested.emit)
            self.tray.setContextMenu(menu)
            self._sync_tray()

    def _sync_tray(self):
        if self.tray is not None:
            if self.mode in ("background", "always") and self.enabled_events and not self._closed:
                self.tray.show()
            else:
                self.tray.hide()

    def _native_tray(self):
        app = QApplication.instance()
        if app is None or app.platformName() == "offscreen":
            return None
        if not QSystemTrayIcon.isSystemTrayAvailable() or not QSystemTrayIcon.supportsMessages():
            return None
        return QSystemTrayIcon(self.owner)

    def _is_foreground(self):
        app = QApplication.instance()
        return not self.owner.isMinimized() and app is not None and app.applicationState() == Qt.ApplicationState.ApplicationActive

    def _activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.restore_requested.emit()

    def configure(self, mode, categories):
        categories = set(categories)
        if mode not in MODES or not categories <= CATEGORIES.keys():
            raise ValueError("Invalid notification settings")
        self.mode, self.enabled_events = mode, categories
        self.settings.setValue("notifications_mode", mode)
        self.settings.setValue("notifications_events", sorted(categories))
        self._sync_tray()
        self.changed.emit()

    @Slot(str, int)
    def notify(self, event, count=0):
        if event not in EVENTS or not isinstance(count, int) or count < 0:
            raise ValueError("Invalid notification event")
        if self._closed:
            return
        category, title, text, warning = EVENTS[event]
        if self.mode == "off" or category not in self.enabled_events:
            return
        if count:
            text = f"Items: {count:,}. " + text
        self.recent.insert(0, {"event": event, "title": title, "text": text,
                               "time": datetime.now().strftime("%H:%M:%S")})
        del self.recent[50:]
        self.unread = min(50, self.unread + 1)
        # Determine focus before local listeners update the UI.
        desktop = self.mode == "always" or self.mode == "background" and not self._foreground()
        if desktop and self.tray is not None:
            icon = QSystemTrayIcon.MessageIcon.Warning if warning else QSystemTrayIcon.MessageIcon.Information
            self.tray.showMessage(f"Memoria — {title}", text, icon, 10000)
        self.changed.emit()

    def mark_read(self):
        if self.unread:
            self.unread = 0
            self.changed.emit()

    def clear(self):
        self.recent.clear()
        self.unread = 0
        self.changed.emit()

    def close(self):
        self._closed = True
        if self.tray is not None:
            self.tray.hide()


class NotificationsDialog(Dialog):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("Notifications")
        self.resize(720, 640)
        self.mode = QComboBox()
        for key, text in MODES.items():
            self.mode.addItem(text, key)
        self.mode.setCurrentIndex(self.mode.findData(manager.mode))
        self.events = {}
        layout = vbox(label("Notifications", "h2"), self.mode, spacing=8, margins=(20, 18, 20, 18))
        for key, text in CATEGORIES.items():
            box = QCheckBox(text)
            box.setChecked(key in manager.enabled_events)
            self.events[key] = box
            layout.addWidget(box)
        available = ("Desktop delivery is available, but Windows notification/Focus Assist settings may suppress it."
                     if manager.tray is not None else
                     "Desktop notifications are unavailable in this session. Events still appear below.")
        layout.addWidget(label(available + " No filenames, library paths or raw errors are sent to the desktop.",
                               "small", wrap=True))
        layout.addWidget(label("Recent events (up to 50; newest first)", "h2"))
        self.history = QTreeWidget()
        self.history.setHeaderLabels(["Time", "Event", "Details"])
        self.history.setRootIsDecorated(False)
        self.history.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.history.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.history.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.history.setWordWrap(True)
        layout.addWidget(self.history, 1)
        layout.addWidget(label("Existing progress, safety dialogs and Undo toasts stay unchanged. Closing Memoria "
                               "still exits the app; the tray icon does not keep it running.", "small", wrap=True))
        layout.addLayout(hbox(button("Clear recent", on_click=manager.clear), None,
                              button("Close", on_click=self.accept)))
        self.setLayout(layout)
        self.mode.currentIndexChanged.connect(self._save)
        for box in self.events.values():
            box.toggled.connect(self._save)
        manager.changed.connect(self._refresh)
        self._refresh()
        manager.mark_read()

    def _save(self):
        self.manager.configure(self.mode.currentData(), [key for key, box in self.events.items() if box.isChecked()])

    def _refresh(self):
        self.history.clear()
        for row in self.manager.recent:
            item = QTreeWidgetItem([row["time"], row["title"], row["text"]])
            item.setToolTip(2, row["text"])
            self.history.addTopLevelItem(item)
        if self.isVisible() and self.isActiveWindow():
            self.manager.mark_read()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.ActivationChange and self.isActiveWindow():
            self.manager.mark_read()
