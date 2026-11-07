"""Reusable catalogue filter dialog; all filters are read-only."""
from dataclasses import replace

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QCheckBox, QComboBox, QDateEdit, QDialog, QDoubleSpinBox, QFormLayout

from ..engine import catalogue
from .widgets import MessageDialog, button, hbox, label, vbox

KINDS = [("media", "Photos & videos"), ("image", "Photos"), ("video", "Videos"),
         ("problems", "Problems"), ("other", "Other files"), ("all", "All files")]
SORTS = [("newest", "Newest first"), ("oldest", "Oldest first"), ("largest", "Largest first"),
         ("smallest", "Smallest first"), ("name", "Name")]


class FilterDialog(QDialog):
    def __init__(self, parent, lib, current: catalogue.Filters):
        super().__init__(parent)
        self.setWindowTitle("Filter library")
        self.current = current
        self.setMinimumWidth(520)
        form = QFormLayout()
        self.folder = QComboBox()
        for folder in catalogue.folders(lib):
            self.folder.addItem(folder or "Library root", folder)
        self.folder.setCurrentIndex(max(0, self.folder.findData(current.folder)))
        self.recursive = QCheckBox("Include subfolders")
        self.recursive.setChecked(current.recursive)
        self.kind = QComboBox()
        for key, text in KINDS:
            self.kind.addItem(text, key)
        self.kind.setCurrentIndex(self.kind.findData(current.kind))
        self.ext = QComboBox()
        self.ext.addItem("Any format", None)
        for row in lib.db.execute("SELECT DISTINCT ext FROM files ORDER BY ext"):
            self.ext.addItem(row[0] or "(no extension)", row[0])
        self.ext.setCurrentIndex(max(0, self.ext.findData(current.extension)))
        self.use_dates = QCheckBox("Limit capture dates (inclusive)")
        self.use_dates.setChecked(bool(current.start or current.end))
        self.start, self.end = QDateEdit(), QDateEdit()
        for widget in (self.start, self.end):
            widget.setCalendarPopup(True)
            widget.setDisplayFormat("dd MMM yyyy")
        self.start.setDate(QDate.fromString(current.start, "yyyy-MM-dd") if current.start else QDate(1900, 1, 1))
        self.end.setDate(QDate.fromString(current.end, "yyyy-MM-dd").addDays(-1) if current.end else QDate.currentDate())
        for widget in (self.start, self.end):
            widget.setEnabled(self.use_dates.isChecked())
            self.use_dates.toggled.connect(widget.setEnabled)
        self.minimum, self.maximum = QDoubleSpinBox(), QDoubleSpinBox()
        for widget in (self.minimum, self.maximum):
            widget.setRange(0, 1_000_000_000)
            widget.setSuffix(" MiB")
            widget.setDecimals(2)
        self.minimum.setValue(current.min_bytes / 1024**2)
        self.maximum.setValue((current.max_bytes or 0) / 1024**2)
        self.maximum.setSpecialValueText("No maximum")
        self.location = QComboBox()
        for text, key in (("Anywhere", "all"), ("Has valid GPS", "gps"), ("No valid GPS", "none")):
            self.location.addItem(text, key)
        self.location.setCurrentIndex(self.location.findData(current.location))
        self.keep_area = QCheckBox("Keep selected map area")
        self.keep_area.setChecked(current.bbox is not None)
        self.keep_area.setVisible(current.bbox is not None)
        self.faces = QComboBox()
        for text, key in (("Any", "all"), ("Has detected faces", "any"), ("Scanned: no faces", "none"),
                          ("Not scanned for faces", "unscanned")):
            self.faces.addItem(text, key)
        self.faces.setCurrentIndex(self.faces.findData(current.faces))
        self.person = QComboBox()
        self.person.addItem("Anyone", None)
        for row in lib.db.execute("SELECT id,name FROM people ORDER BY name"):
            self.person.addItem(row["name"], row["id"])
        self.person.setCurrentIndex(max(0, self.person.findData(current.person)))
        for title, widget in (("Folder", self.folder), ("", self.recursive), ("Type", self.kind),
                              ("Format", self.ext), ("", self.use_dates), ("From", self.start), ("Through", self.end),
                              ("Minimum size", self.minimum), ("Maximum size", self.maximum),
                              ("Location", self.location), ("", self.keep_area), ("Faces", self.faces),
                              ("Person", self.person)):
            form.addRow(title, widget)
        self.setLayout(vbox(form, label("Dates use the catalogue's best available date, including filename or modified "
                                       "date when camera metadata is unavailable. Face filters use Find people results.",
                                       "small", wrap=True),
                            hbox(None, button("Cancel", on_click=self.reject),
                                 button("Apply filters", "primary", self._accept)), margins=(20, 18, 20, 18)))

    def selected(self):
        return replace(self.current, folder=self.folder.currentData(), recursive=self.recursive.isChecked(),
                       kind=self.kind.currentData(), extension=self.ext.currentData(), undated=False,
                       start=self.start.date().toString("yyyy-MM-dd") if self.use_dates.isChecked() else None,
                       end=self.end.date().addDays(1).toString("yyyy-MM-dd") if self.use_dates.isChecked() else None,
                       min_bytes=int(self.minimum.value() * 1024**2),
                       max_bytes=int(self.maximum.value() * 1024**2) if self.maximum.value() else None,
                       location=self.location.currentData(),
                       bbox=self.current.bbox if self.keep_area.isChecked() else None,
                       faces=self.faces.currentData(), person=self.person.currentData())

    def _accept(self):
        try:
            catalogue.where(self.selected())
        except ValueError as e:
            MessageDialog(self, "Check the filters", str(e)).exec()
            return
        self.accept()
