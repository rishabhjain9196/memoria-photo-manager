"""Import photos and videos (or a readable copy of everything) from an iPhone/iPad backup."""
from __future__ import annotations

import html
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QButtonGroup, QCheckBox, QComboBox, QFileDialog, QLineEdit, QRadioButton, QWidget

from ..engine import iosbackup
from .motion import Dialog
from .tasks import LatestCall
from .widgets import Banner, button, fmt_size, hbox, label, vbox

_BANNER_IDS = {"warn": "warnBox", "info": "infoBox", "danger": "dangerBox", "trust": "trust"}


class IosImportDialog(Dialog):
    """Collects the choices; the caller runs ``iosbackup.extract`` as a task."""

    def __init__(self, parent, library=None):
        super().__init__(parent)
        self.setWindowTitle("Import from iPhone backup")
        self.setMinimumWidth(640)
        self.library = library
        self.backup: Optional[iosbackup.BackupInfo] = None
        self.entries: Optional[list[iosbackup.Entry]] = None
        self._summary: dict[str, tuple[int, int]] = {}

        self.picker = QComboBox()
        self.picker.currentIndexChanged.connect(self._picked)
        self.state = Banner("", "info")
        self.to_library = QRadioButton("Add new photos && videos to this library")
        self.to_folder = QRadioButton("Copy to a folder (readable copy of the backup)")
        modes = QButtonGroup(self)
        modes.addButton(self.to_library)
        modes.addButton(self.to_folder)
        self.to_library.setEnabled(library is not None)
        (self.to_library if library is not None else self.to_folder).setChecked(True)
        self.to_library.toggled.connect(self._refresh)
        self.folder = QLineEdit()
        self.folder.setPlaceholderText("Choose an empty or new folder")
        self.folder.textChanged.connect(self._refresh)
        self.browse_folder = button("Browse…", on_click=self._choose_folder)
        self.boxes: dict[str, QCheckBox] = {}
        cats = QWidget()
        cat_layout = vbox(spacing=4)
        for key, (title, help_text, media) in iosbackup.CATEGORIES.items():
            box = QCheckBox(title.replace("&", "&&"))
            box.setToolTip(help_text)
            box.setChecked(key == "camera_roll")
            box.toggled.connect(self._refresh)
            self.boxes[key] = box
            cat_layout.addWidget(box)
        cats.setLayout(cat_layout)
        self.total = label("", "small", wrap=True)
        self.go_btn = button("Import", "primary", self.accept)

        lay = vbox(label("Import from iPhone backup", "h2"),
                   label("Reads an unencrypted backup made by iTunes or the Apple Devices app. The backup is only "
                         "read, never changed. Copies keep each photo's original date; existing files are never "
                         "replaced, and an interrupted import resumes where it stopped.", "small", wrap=True),
                   hbox(self.picker, button("Other backup folder…", on_click=self._choose_backup)),
                   self.state, self.to_library, self.to_folder,
                   hbox(20, self.folder, self.browse_folder),
                   label("What to copy"), cats, self.total,
                   hbox(None, button("Cancel", on_click=self.reject), self.go_btn),
                   spacing=10, margins=(22, 18, 22, 18))
        self.setLayout(lay)

        self._reader = LatestCall(self)
        self._reader.result.connect(self._catalogue_read)
        self._reader.failed.connect(self._catalogue_failed)
        self._finder = LatestCall(self)
        self._finder.result.connect(self._found)
        self._finder.failed.connect(lambda error: self._set_state(f"Couldn't look for backups: {error}", "warn"))
        self._set_state("Looking for backups on this PC…", "info")
        self._finder.call(iosbackup.find_backups)
        self._refresh()

    # backups ------------------------------------------------------------------------------
    def _found(self, backups: list) -> None:
        self.picker.blockSignals(True)
        self.picker.clear()
        for b in backups:
            self.picker.addItem(b.label, b)
        self.picker.blockSignals(False)
        if backups:
            self._picked(0)
        else:
            folders = "<br>".join(html.escape(str(d)) for d in iosbackup.default_backup_dirs())
            self._set_state("No backups were found in the usual folders:<br>" + folders +
                            "<br>Use <b>Other backup folder…</b> to pick one (the folder that contains Manifest.db).",
                            "warn")
            self._refresh()

    def _choose_backup(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose the backup folder (contains Manifest.db)")
        if not path:
            return
        try:
            backup = iosbackup.read_backup(path)
        except iosbackup.BackupError as error:
            self._set_state(html.escape(str(error)), "danger")
            return
        self.picker.addItem(backup.label, backup)
        self.picker.setCurrentIndex(self.picker.count() - 1)

    def _picked(self, index: int) -> None:
        self.backup = self.picker.itemData(index)
        self.entries = None
        self._summary = {}
        if self.backup is None:
            return self._refresh()
        if self.backup.encrypted:
            self._set_state("This backup is <b>encrypted</b>. Memoria can't read encrypted backups. Turn off "
                            "“Encrypt local backup” and back up again, or decrypt it with a dedicated tool first.",
                            "danger")
            return self._refresh()
        self._set_state("Reading the backup catalogue…", "info")
        backup = self.backup
        self._reader.call(lambda: (backup, iosbackup.list_files(backup)))
        self._refresh()

    def _catalogue_read(self, value) -> None:
        backup, entries = value
        if backup is not self.backup:
            return
        self.entries = entries
        warn = self.backup.complete is False
        text = (f"<b>{html.escape(self.backup.device_name)}</b> · {len(entries):,} files in the backup"
                + (" · <b>This backup did not finish</b>; some files may be missing." if warn else ""))
        self._set_state(text, "warn" if warn else "trust")
        self._refresh()

    def _catalogue_failed(self, error) -> None:
        self.entries = None
        self._set_state(html.escape(str(error)), "danger")
        self._refresh()

    # choices ------------------------------------------------------------------------------
    def _choose_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose where to copy the backup's files")
        if path:
            self.folder.setText(path)

    def _set_state(self, text: str, kind: str) -> None:
        self.state.setText(text)
        self.state.setObjectName(_BANNER_IDS[kind])
        self.state.style().unpolish(self.state)
        self.state.style().polish(self.state)

    def _refresh(self, *_) -> None:
        library_mode = self.to_library.isChecked()
        self.folder.setEnabled(not library_mode)
        self.browse_folder.setEnabled(not library_mode)
        if self.entries is not None:
            self._summary = iosbackup.summarize(self.entries, media_only=library_mode)
        files = size = 0
        for key, box in self.boxes.items():
            title, _, media = iosbackup.CATEGORIES[key]
            box.setEnabled(media or not library_mode)
            count, nbytes = self._summary.get(key, (0, 0))
            title = title.replace("&", "&&")  # a single & would become a keyboard shortcut marker
            box.setText(f"{title}  —  {count:,} files, {fmt_size(nbytes)}" if self._summary else title)
            if box.isChecked() and box.isEnabled():
                files += count
                size += nbytes
        if library_mode and self.library is not None and self.backup is not None:
            target = iosbackup.default_library_folder(self.library, self.backup)
            hint = f"Into {target}. Photos the library already holds (same content) are skipped."
        else:
            hint = ""
        self.total.setText((f"Selected: {files:,} files, {fmt_size(size)}. " if self._summary else "") + hint)
        self.go_btn.setEnabled(bool(self.entries) and files > 0 and
                               (library_mode or bool(self.folder.text().strip())))

    def choices(self) -> dict:
        library_mode = self.to_library.isChecked()
        categories = [k for k, b in self.boxes.items() if b.isChecked() and b.isEnabled()]
        destination = (iosbackup.default_library_folder(self.library, self.backup) if library_mode
                       else Path(self.folder.text().strip()))
        return {"backup": self.backup, "entries": self.entries, "categories": categories,
                "destination": destination, "library_mode": library_mode}
