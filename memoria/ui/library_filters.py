"""Reusable catalogue filter dialog; all filters are read-only."""
from dataclasses import replace
from datetime import datetime

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDateEdit, QDialog, QDoubleSpinBox, QFormLayout, QLineEdit,
                               QSpinBox, QTabWidget, QWidget)

from .motion import Dialog
from ..engine import catalogue
from .widgets import MessageDialog, button, fmt_date, fmt_duration, fmt_size, hbox, label, scroll, vbox

KINDS = [("media", "Photos & videos"), ("image", "Photos"), ("video", "Videos"),
         ("problems", "Problems"), ("other", "Other files"), ("all", "All files")]
SORTS = [("newest", "Newest first"), ("oldest", "Oldest first"), ("largest", "Largest first"),
         ("rating_desc", "Rating: highest first"), ("rating_asc", "Rating: lowest first"),
         ("smallest", "Smallest first"), ("name", "Name"), ("format", "File format"),
         ("modified_newest", "Recently modified"), ("modified_oldest", "Least recently modified"),
         ("megapixels_desc", "Resolution: highest first"), ("megapixels_asc", "Resolution: lowest first"),
         ("duration_desc", "Video: longest first"), ("duration_asc", "Video: shortest first"),
         ("bitrate_desc", "Overall bitrate: highest first"), ("bitrate_asc", "Overall bitrate: lowest first"),
         ("fps_desc", "Frame rate: highest first"), ("fps_asc", "Frame rate: lowest first"),
         ("video_codec", "Video codec"), ("audio_codec", "Audio codec"), ("camera", "Camera"), ("lens", "Lens"),
         ("iso_asc", "ISO: lowest first"), ("iso_desc", "ISO: highest first"),
         ("aperture_asc", "F-number: lowest first"), ("aperture_desc", "F-number: highest first"),
         ("exposure_asc", "Shutter: fastest first"), ("exposure_desc", "Shutter: slowest first"),
         ("focal_asc", "Focal length: shortest first"), ("focal_desc", "Focal length: longest first")]
RANGES = {
    "megapixels": ("Resolution (MP)", " MP", 4, 1_000_000),
    "duration": ("Video length (seconds)", " s", 2, 1_000_000_000),
    "bitrate": ("Overall bitrate (Mbps, estimated)", " Mbps", 3, 1_000_000),
    "fps": ("Reported frame rate (fps)", " fps", 3, 1_000_000),
    "iso": ("ISO sensitivity", "", 0, 1_000_000_000),
    "aperture": ("Aperture (f-number)", "", 2, 1000),
    "exposure": ("Exposure / shutter time (seconds)", " s", 6, 86400),
    "focal": ("Focal length (actual mm)", " mm", 2, 100000),
}


def sort_caption(row: dict, key: str) -> str:
    if key.startswith("rating_"):
        return "★" * row.get("rating", 0) or "Unrated"
    if key in ("largest", "smallest"):
        return fmt_size(row["size"])
    if key.startswith("modified_"):
        return fmt_date(datetime.fromtimestamp(row["mtime"]).isoformat())
    if key == "format":
        return row["ext"].lstrip(".").upper() or "No extension"
    if key == "name":
        return row["name"]
    if key in ("camera", "lens", "video_codec", "audio_codec"):
        value = row.get(key)
        if key == "audio_codec" and value == "":
            return "No audio"
        return value or "Unknown"
    metric = key.rsplit("_", 1)[0]
    if metric in ("duration", "fps", "bitrate") and row["kind"] != "video":
        return "Not a video"
    if metric == "megapixels":
        w, h = row.get("width"), row.get("height")
        return f"{w}×{h} · {w*h/1_000_000:.2f} MP" if w and h else "Unknown resolution"
    if metric == "duration":
        value = row.get("duration")
        return fmt_duration(value) or "Unknown duration"
    if metric == "bitrate":
        value = catalogue.overall_bitrate(row)
        return f"≈{value:.3f} Mbps" if value is not None else "Unknown bitrate"
    if metric in RANGES:
        field = {"exposure": "exposure_seconds", "focal": "focal_length_mm"}.get(metric, metric)
        value = row.get(field)
        if value is None or value <= 0:
            return "Unknown"
        if metric == "exposure" and value < 1:
            return f"1/{1/value:g} s"
        return f"{'f/' if metric == 'aperture' else ''}{value:g}{RANGES[metric][1]}"
    return fmt_date(row["taken_at"]) if row.get("taken_at") else row["name"]


def metadata_filter_notes(filters: catalogue.Filters) -> list[str]:
    notes = []
    if filters.root_id is not None:
        notes.append(f"Library folder #{filters.root_id}")
    if filters.availability != "all":
        notes.append(f"{filters.availability.capitalize()} folders")
    if filters.min_rating or filters.max_rating < 5:
        notes.append(f"Rating: {filters.min_rating}–{filters.max_rating}")
    if filters.favorite is not None:
        notes.append("Favourites" if filters.favorite else "Not favourites")
    if filters.review != "all":
        notes.append(f"Review: {filters.review}")
    if filters.tags:
        notes.append(f"Tags ({filters.tag_mode}): {', '.join(filters.tags)}")
    for key in ("camera", "lens", "video_codec", "audio_codec"):
        value = getattr(filters, key)
        if value is not None:
            notes.append(f"{key.replace('_', ' ').capitalize()}: {value or 'No audio'}")
    if filters.orientation != "all":
        notes.append(filters.orientation.capitalize())
    if filters.min_width or filters.min_height:
        notes.append(f"Minimum dimensions: {filters.min_width}×{filters.min_height} px")
    for key, (title, unit, _, _) in RANGES.items():
        low, high = getattr(filters, f"min_{key}"), getattr(filters, f"max_{key}")
        if low is not None or high is not None:
            notes.append(f"{title}: {f'{low:g}' if low is not None else 'any'}–"
                         f"{f'{high:g}' if high is not None else 'any'}{unit}")
    return notes


class FilterDialog(Dialog):
    def __init__(self, parent, lib, current: catalogue.Filters):
        super().__init__(parent)
        self.setWindowTitle("Filter library")
        self.current = current
        self.setMinimumWidth(600)
        self.resize(660, 650)
        form = QFormLayout()
        self.folder = QComboBox()
        self.folder.setEditable(True)
        folders = {current.folder, ""}
        folders.update(r[0] for r in lib.db.execute("SELECT DISTINCT folder FROM files ORDER BY folder LIMIT 1000"))
        for folder in sorted(folders, key=str.casefold):
            self.folder.addItem(lib.display_path(folder) if folder else "Library root", folder)
        self.folder.setToolTip("First 1,000 folders; you can also type a relative folder path.")
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
        self.undated = QCheckBox("Undated files only")
        self.undated.setChecked(current.undated)
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
                              ("Format", self.ext), ("", self.undated), ("", self.use_dates), ("From", self.start), ("Through", self.end),
                              ("Minimum size", self.minimum), ("Maximum size", self.maximum),
                              ("Location", self.location), ("", self.keep_area), ("Faces", self.faces),
                              ("Person", self.person)):
            form.addRow(title, widget)
        self.tabs = QTabWidget()
        general = QWidget()
        general.setLayout(form)
        self.tabs.addTab(scroll(general), "Files && dates")
        organisation_form = QFormLayout()
        self.root = QComboBox()
        self.root.addItem("All library folders", None)
        for root in lib.roots():
            self.root.addItem(root["label"] + ("" if root["online"] else " (offline)"), root["id"])
        self.root.setCurrentIndex(max(0, self.root.findData(current.root_id)))
        self.availability = QComboBox()
        for key in ("all", "online", "offline"):
            self.availability.addItem(key.capitalize(), key)
        self.availability.setCurrentIndex(self.availability.findData(current.availability))
        self.min_rating, self.max_rating = QSpinBox(), QSpinBox()
        for box, value in ((self.min_rating, current.min_rating), (self.max_rating, current.max_rating)):
            box.setRange(0, 5)
            box.setValue(value)
        self.favorite = QComboBox()
        for title, value in (("Any", None), ("Favourites only", True), ("Not favourites", False)):
            self.favorite.addItem(title, value)
        self.favorite.setCurrentIndex(self.favorite.findData(current.favorite))
        self.review = QComboBox()
        for key in ("all", "unreviewed", "pick", "reject"):
            self.review.addItem(key.capitalize(), key)
        self.review.setCurrentIndex(self.review.findData(current.review))
        self.tags = QLineEdit(", ".join(current.tags))
        self.tags.setPlaceholderText("Tag names, separated by commas")
        self.tag_mode = QComboBox()
        for key in ("all", "any"):
            self.tag_mode.addItem("Match " + key + " tags", key)
        self.tag_mode.setCurrentIndex(self.tag_mode.findData(current.tag_mode))
        for title, widget in (("Library folder", self.root), ("Availability", self.availability),
                              ("Minimum rating (0 = unrated)", self.min_rating), ("Maximum rating", self.max_rating),
                              ("Favourites", self.favorite), ("Review mark", self.review),
                              ("Tags", self.tags), ("Match", self.tag_mode)):
            organisation_form.addRow(title, widget)
        panel = QWidget()
        panel.setLayout(organisation_form)
        organisation_panel = panel
        self.metadata_text = {}
        self.ranges = {}
        dimensions_form, camera_form = QFormLayout(), QFormLayout()
        self.orientation = QComboBox()
        for key in ("all", "landscape", "portrait", "square"):
            self.orientation.addItem("Any orientation" if key == "all" else key.capitalize(), key)
        self.orientation.setCurrentIndex(self.orientation.findData(current.orientation))
        dimensions_form.addRow("Orientation (displayed)", self.orientation)
        self.min_width, self.min_height = QSpinBox(), QSpinBox()
        for key, widget in (("min_width", self.min_width), ("min_height", self.min_height)):
            widget.setRange(0, 1_000_000)
            widget.setSpecialValueText("Any")
            widget.setSuffix(" px")
            widget.setValue(getattr(current, key))
        dimensions_form.addRow("Minimum width / height (px)", hbox(self.min_width, self.min_height))
        for key in ("video_codec", "audio_codec", "camera", "lens"):
            box = QComboBox()
            box.addItem("Any", None)
            if key == "audio_codec":
                box.addItem("No audio stream", "")
            for row in lib.db.execute(f"SELECT DISTINCT {key} FROM files WHERE {key} IS NOT NULL AND "
                                      f"{key}!='' ORDER BY {key} COLLATE NOCASE"):
                box.addItem(row[0], row[0])
            value = getattr(current, key)
            if value is not None and box.findData(value) < 0:
                box.addItem(value, value)
            box.setCurrentIndex(max(0, box.findData(value)))
            self.metadata_text[key] = box
            (dimensions_form if key.endswith("codec") else camera_form).addRow(key.replace("_", " ").capitalize(), box)
        for key, (title, unit, decimals, maximum) in RANGES.items():
            low, high = QDoubleSpinBox(), QDoubleSpinBox()
            for side, box in (("min", low), ("max", high)):
                box.setRange(0, maximum)
                box.setDecimals(decimals)
                box.setSuffix(unit)
                box.setSpecialValueText("Any")
                box.setValue(getattr(current, f"{side}_{key}") or 0)
                box.setAccessibleName(f"{title}: {side}")
            self.ranges[key] = (low, high)
            (dimensions_form if key in ("megapixels", "duration", "bitrate", "fps") else camera_form).addRow(
                title + " (min / max)", hbox(low, high))
        for title, layout in (("Dimensions && video", dimensions_form), ("Camera && exposure", camera_form)):
            panel = QWidget()
            panel.setLayout(layout)
            self.tabs.addTab(scroll(panel), title)
        self.tabs.addTab(scroll(organisation_panel), "Organisation")
        outer = vbox(self.tabs, label("Missing metadata is excluded only when that field is filtered. Video ranges "
                                       "match videos; EXIF ranges match photos. Bitrate includes audio/container overhead "
                                       "and is not a quality score. Dates may be filename/modified-date fallbacks; "
                                       "face filters use Find people results.",
                                       "small", wrap=True),
                            hbox(None, button("Cancel", on_click=self.reject),
                                 button("Apply filters", "primary", self._accept)), margins=(20, 18, 20, 18))
        outer.setStretchFactor(self.tabs, 1)
        self.setLayout(outer)

    def selected(self):
        technical = {key: box.currentData() for key, box in self.metadata_text.items()}
        technical.update({f"{side}_{key}": box.value() or None for key, boxes in self.ranges.items()
                          for side, box in zip(("min", "max"), boxes)})
        folder = self.folder.currentData()
        if self.folder.currentText() != self.folder.itemText(self.folder.currentIndex()):
            folder = self.folder.currentText().strip()
        return replace(self.current, folder=folder or "", recursive=self.recursive.isChecked(),
                       kind=self.kind.currentData(), extension=self.ext.currentData(), undated=self.undated.isChecked(),
                       start=self.start.date().toString("yyyy-MM-dd") if self.use_dates.isChecked() else None,
                       end=self.end.date().addDays(1).toString("yyyy-MM-dd") if self.use_dates.isChecked() else None,
                       min_bytes=int(self.minimum.value() * 1024**2),
                       max_bytes=int(self.maximum.value() * 1024**2) if self.maximum.value() else None,
                       location=self.location.currentData(),
                       bbox=self.current.bbox if self.keep_area.isChecked() else None,
                       faces=self.faces.currentData(), person=self.person.currentData(),
                       orientation=self.orientation.currentData(), min_width=self.min_width.value(),
                       min_height=self.min_height.value(), root_id=self.root.currentData(),
                       availability=self.availability.currentData(), min_rating=self.min_rating.value(),
                       max_rating=self.max_rating.value(), favorite=self.favorite.currentData(),
                       review=self.review.currentData(), tags=tuple(t.strip() for t in self.tags.text().split(",") if t.strip()),
                       tag_mode=self.tag_mode.currentData(), **technical)

    def _accept(self):
        try:
            catalogue.where(self.selected())
        except ValueError as e:
            MessageDialog(self, "Check the filters", str(e)).exec()
            return
        self.accept()
