"""Explicit, non-media-destructive storage maintenance choices."""
from dataclasses import asdict

from PySide6.QtWidgets import QCheckBox, QDialog, QWidget

from ..engine.storage import ResetOptions
from .widgets import Banner, button, fmt_size, hbox, label, scroll, vbox


CHOICES = {
    "thumbnails": ("Photo/video thumbnails", "Recreated while rebuilding. People thumbnails are kept unless People is cleared."),
    "analysis": ("File analysis and duplicate hashes", "Re-read dates, dimensions and quality. Original file metadata is not edited."),
    "videos": ("Similar-video signatures", "Recreated next time you find similar videos."),
    "people": ("People, face data, names and corrections", "Names and corrections are lost. Use Find people to start again."),
    "albums": ("Saved albums", "Album definitions are lost. Exported folders and photos stay untouched."),
    "organisation": ("Tags, ratings, favourites and Pick/Reject marks",
                     "User choices are lost, including for missing and Recovery items. Originals are unchanged."),
    "health": ("Health fingerprints", "Loses the old reference for detecting damage. Run Health check to establish a new baseline."),
    "missing": ("Missing-file records", "Forget missing entries and their organisation/album/face links. No files are deleted."),
    "duplicate_choices": ("Previous Keep both/all choices", "Show previously kept duplicate groups for review again."),
    "compact": ("Shrink storage files", "Optional: returns unused database space to disk. Needs temporary disk space."),
}


class StorageDialog(QDialog):
    def __init__(self, parent, sizes: dict[str, int], interrupted: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Storage & reset")
        self.setMinimumWidth(600)
        self.resize(650, 600)
        self.interrupted = interrupted
        self.boxes = {}
        self.ack = QCheckBox("I understand these catalogue records cannot be restored by Undo.")
        self.go_btn = button("Clear selected && rebuild", "primary", self.accept)
        self.skip_compact = QCheckBox("Skip shrinking storage files (use this if disk space is low)")
        lay = vbox(label("Storage & reset", "h2"),
                   label(f"Catalogue: {fmt_size(sizes['catalogue'])}   "
                         f"Thumbnail storage: {fmt_size(sizes['thumbnails'])}", wrap=True),
                   label("For new or changed files, try Rescan library (F5) first. "
                         "Reset is for stale results, mistakes or starting over.", "small", wrap=True),
                   Banner("Photos, videos, exported files, Recovery files and Undo history are never deleted here. "
                          "Only selected catalogue data is cleared.", "info"),
                   spacing=10, margins=(22, 18, 22, 18))
        if interrupted:
            lay.addWidget(label("A previous reset did not finish. Resume it from its last completed phase. "
                                "Data already cleared is not cleared again during rebuilding.", wrap=True))
            lay.addWidget(self.skip_compact)
            self.go_btn.setText("Resume rebuild")
        else:
            lay.addLayout(hbox(button("Safe rebuild (soft)", on_click=lambda: self.preset(False)),
                               button("Start fresh (hard)", on_click=lambda: self.preset(True)), None))
            choices = QWidget()
            choices_layout = vbox(spacing=6)
            for key, (title, help_text) in CHOICES.items():
                box = QCheckBox(title)
                box.setToolTip(help_text)
                box.toggled.connect(self._selection_changed)
                self.boxes[key] = box
                choices_layout.addWidget(box)
                choices_layout.addWidget(label(help_text, "small", wrap=True))
            choices.setLayout(choices_layout)
            lay.addWidget(scroll(choices), 1)
            lay.addWidget(self.ack)
            self.ack.toggled.connect(self._selection_changed)
            lay.addWidget(label("Cleared storage is reused unless you select Shrink. Thumbnails and analysis rebuild "
                                "now; People, Albums, Health check and Similar videos are run separately. "
                                "If interrupted, reopen this library or resume here.", wrap=True))
            self.preset(False)
        lay.addLayout(hbox(None, button("Cancel", on_click=self.reject), self.go_btn))
        self.setLayout(lay)

    def options(self) -> ResetOptions:
        return ResetOptions(**{key: box.isChecked() for key, box in self.boxes.items()})

    def preset(self, clear_all: bool) -> None:
        defaults = asdict(ResetOptions())
        self.ack.setChecked(False)
        for key, box in self.boxes.items():
            box.setChecked(defaults[key] if not clear_all else key != "compact")
        self._selection_changed()

    def _selection_changed(self) -> None:
        destructive = any(self.boxes[key].isChecked() for key in ("people", "albums", "organisation", "health", "missing", "duplicate_choices")
                          if key in self.boxes)
        self.ack.setVisible(destructive)
        self.go_btn.setEnabled(any(box.isChecked() for box in self.boxes.values()) and
                               (not destructive or self.ack.isChecked()))
