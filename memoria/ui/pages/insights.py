"""Read-only storage distributions, capture timeline and offline photo locations."""
from dataclasses import replace

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QComboBox, QListWidget, QListWidgetItem, QSplitter, QTabWidget, QWidget

from ...engine import catalogue, geography
from ..insight_charts import BarChart, GeoChart
from ..library_filters import FilterDialog
from ..tasks import BackgroundCall
from ..widgets import button, fmt_size, hbox, label, vbox
from .base import Page


class InsightsPage(Page):
    title = "Library insights"
    subtitle = "Explore catalogue storage, dates and GPS locations. Nothing here changes your files."

    def __init__(self, ctx):
        super().__init__(ctx)
        self.filters = catalogue.Filters(kind="all")
        self.prefix = ""
        self.bounds = None
        self._closed = False
        self.folder = QComboBox()
        self.folder.setMinimumWidth(200)
        self.header_actions.addWidget(self.folder)
        self.header_actions.addWidget(button("Filters…", on_click=self._filters))
        self.header_actions.addWidget(button("Clear", "link", self._clear))
        self.summary = label("", "muted", wrap=True)
        self.status = label("", "small", wrap=True)
        self.tabs = QTabWidget()
        self.folders = BarChart("Immediate subfolder", "bytes")
        self.types = BarChart("File format", "bytes")
        storage_split = QSplitter()
        storage_split.addWidget(self.folders)
        storage_split.addWidget(self.types)
        storage_tab = QWidget()
        storage_layout = vbox(label("Click a folder to drill down, or a format to browse its files. "
                                        "Sizes include every selected indexed file, not Recovery or cache storage.",
                                        "small", wrap=True),
                                  storage_split, button("Browse selected folder", on_click=self._browse))
        storage_layout.setStretchFactor(storage_split, 1)
        storage_tab.setLayout(storage_layout)
        self.tabs.addTab(storage_tab, "Storage")
        self.time = BarChart("Year / month / day", "count")
        self.period_label = label("All dates", "h2")
        self.album_list = QListWidget()
        self.album_list.setAccessibleName("Albums containing files in the selected time period")
        timeline_right = QWidget()
        album_layout = vbox(label("Albums in this period", "h2"), self.album_list,
                            label("Select an album to open it. Only saved albums are linked.", "small", wrap=True))
        album_layout.setStretchFactor(self.album_list, 1)
        timeline_right.setLayout(album_layout)
        time_split = QSplitter()
        time_split.addWidget(self.time)
        time_split.addWidget(timeline_right)
        timeline_tab = QWidget()
        timeline_layout = vbox(hbox(button("All years", on_click=lambda: self._period("")),
                                         button("Up", on_click=self._up), self.period_label, None,
                                         button("Browse this period", on_click=self._browse_period)),
                                   label("Click year → month → day. Day opens matching photos/videos. Undated files are "
                                         "excluded. Dates may come from camera metadata, filenames or file-modified dates.",
                                         "small", wrap=True), time_split)
        timeline_layout.setStretchFactor(time_split, 1)
        timeline_tab.setLayout(timeline_layout)
        self.tabs.addTab(timeline_tab, "Timeline")
        self.map = GeoChart()
        self.locations = QListWidget()
        self.locations.setAccessibleName("GPS clusters; select to browse matching files")
        self.locations.setMaximumWidth(260)
        map_split = QSplitter()
        map_split.addWidget(self.map)
        map_split.addWidget(self.locations)
        self.map_note = label("", "small", wrap=True)
        map_tab = QWidget()
        map_layout = vbox(hbox(button("Auto", on_click=lambda: self._map_bounds(None)),
                                   button("India", on_click=lambda: self._map_bounds(geography.INDIA)),
                                   button("World", on_click=lambda: self._map_bounds(geography.WORLD)), None),
                              self.map_note, map_split,
                              label("Offline · Made with Natural Earth · Approximate boundaries. Wheel to zoom; "
                                    "click a marker or location in the list to browse. GPS is never uploaded.",
                                    "small", wrap=True))
        map_layout.setStretchFactor(map_split, 1)
        map_tab.setLayout(map_layout)
        self.tabs.addTab(map_tab, "Map")
        self.body.addWidget(self.summary)
        self.body.addWidget(self.status)
        self.body.addWidget(self.tabs, 1)
        self.bg = BackgroundCall(self)
        self.bg.result.connect(self._show)
        self.bg.failed.connect(self._failed)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(180)
        self.timer.timeout.connect(self._load)
        self.folder.currentIndexChanged.connect(self._folder)
        self.folders.chosen.connect(self._drill_folder)
        self.types.chosen.connect(lambda row: self.ctx.browse_requested.emit(
            replace(self.filters, extension=row["key"])))
        self.time.chosen.connect(self._time_click)
        self.album_list.itemActivated.connect(self._open_album)
        self.album_list.itemClicked.connect(self._open_album)
        self.map.chosen.connect(self._location)
        self.map.zoomed.connect(self._map_bounds)
        self.locations.itemActivated.connect(lambda item: self._location(item.data(Qt.ItemDataRole.UserRole)))
        self.locations.itemClicked.connect(lambda item: self._location(item.data(Qt.ItemDataRole.UserRole)))
        ctx.albums_changed.connect(self._mark_stale)
        ctx.people_changed.connect(self._mark_stale)

    def shutdown(self):
        self._closed = True
        self.timer.stop()
        self.bg.wait()

    def refresh(self):
        self.folder.blockSignals(True)
        self.folder.clear()
        for folder in catalogue.folders(self.lib):
            self.folder.addItem(folder or "Whole library", folder)
        selected = self.folder.findData(self.filters.folder)
        if selected < 0:
            self.folder.addItem(f"{self.filters.folder} (not currently indexed)", self.filters.folder)
            selected = self.folder.count() - 1
        self.folder.setCurrentIndex(selected)
        self.folder.blockSignals(False)
        self._load()

    def _load(self):
        if self._closed:
            return
        if self.lib is None or self.busy:
            self.stale = True
            return
        if self.bg.running:
            self.timer.start()
            return
        lib, filters, prefix, bounds, generation = self.lib, self.filters, self.prefix, self.bounds, self.ctx.generation
        self.status.setText("Reading catalogue…")
        self.tabs.setEnabled(False)
        def work():
            try:
                return {"generation": generation, "request": (filters, prefix, bounds),
                        "distribution": catalogue.distribution(lib, filters),
                        "time": catalogue.timeline(lib, filters, prefix),
                        "albums": catalogue.matching_albums(lib, catalogue.in_period(filters, prefix)),
                        "map": catalogue.map_data(lib, filters, bounds)}
            finally:
                lib.close_thread()
        self.bg.call(work)

    def _show(self, data):
        if self._closed:
            return
        if data["generation"] != self.ctx.generation or data["request"] != (self.filters, self.prefix, self.bounds):
            self.stale = True
            self.timer.start()
            return
        self.timer.stop()
        self.tabs.setEnabled(True)
        self.status.setText("Click a bar or map marker to explore. Data reflects the last scan; F5 refreshes the library.")
        distribution = data["distribution"]
        self.summary.setText(f"{distribution['count']:,} indexed files · {fmt_size(distribution['bytes'])} · "
                             f"{self.filters.folder or 'Library root'}"
                             f"{' (including subfolders)' if self.filters.recursive else ' (direct files only)'} · "
                             f"Type: {self.filters.kind}"
                             + (" · Custom filters active" if self.filters != catalogue.Filters(
                                 kind=self.filters.kind, folder=self.filters.folder, recursive=self.filters.recursive) else ""))
        self.folders.set_rows(distribution["folders"])
        self.types.set_rows(distribution["types"])
        self.time.set_rows(data["time"])
        self.period_label.setText(self.prefix or "All dates")
        self.album_list.clear()
        for album in data["albums"]:
            item = QListWidgetItem(f"{album['name']} · {album['count']:,} matching files")
            item.setData(Qt.ItemDataRole.UserRole, album["id"])
            self.album_list.addItem(item)
        if not data["albums"]:
            item = QListWidgetItem("No saved albums in this period")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.album_list.addItem(item)
        self.map.set_data(data["map"])
        self.map_note.setText(f"{data['map']['gps_count']:,} files have valid GPS; "
                              f"{data['map']['visible_count']:,} in this view. Files without GPS are not plotted.")
        self.locations.clear()
        for cell in sorted(data["map"]["cells"], key=lambda c: -c["count"]):
            item = QListWidgetItem(f"{cell['count']:,} files · {cell['lat']:.3f}, {cell['lon']:.3f}")
            item.setData(Qt.ItemDataRole.UserRole, cell)
            self.locations.addItem(item)

    def _failed(self, error):
        if self._closed:
            return
        self.status.setText(f"Could not load insights: {error}")
        self.tabs.setEnabled(False)
        self.ctx.toast_requested.emit("Insights could not be loaded. Check the message above the charts.", "")

    def _filters(self):
        dlg = FilterDialog(self, self.lib, self.filters)
        if dlg.exec():
            self.filters = dlg.selected()
            self.prefix, self.bounds = "", None
            self.refresh()

    def _clear(self):
        self.filters, self.prefix, self.bounds = catalogue.Filters(kind="all"), "", None
        self.refresh()

    def _folder(self):
        self.filters = replace(self.filters, folder=self.folder.currentData() or "", recursive=True)
        self._load()

    def _drill_folder(self, row):
        if row["direct"]:
            self.ctx.browse_requested.emit(replace(self.filters, folder=row["key"], recursive=False))
        else:
            self.folder.setCurrentIndex(self.folder.findData(row["key"]))

    def _browse(self):
        self.ctx.browse_requested.emit(self.filters)

    def _period(self, prefix):
        self.prefix = prefix
        self._load()

    def _up(self):
        self._period(self.prefix[:4] if len(self.prefix) > 4 else "")

    def _time_click(self, row):
        if len(row["key"]) == 10:
            self.ctx.browse_requested.emit(catalogue.in_period(self.filters, row["key"]))
        else:
            self._period(row["key"])

    def _browse_period(self):
        self.ctx.browse_requested.emit(catalogue.in_period(self.filters, self.prefix))

    def _open_album(self, item):
        album_id = item.data(Qt.ItemDataRole.UserRole)
        if album_id is not None:
            self.ctx.album_requested.emit(album_id)

    def _map_bounds(self, bounds):
        self.bounds = bounds
        self.timer.start()

    def _location(self, cell):
        self.ctx.browse_requested.emit(replace(self.filters, location="gps",
                                               bbox=tuple(cell[key] for key in ("south", "north", "west", "east"))))
