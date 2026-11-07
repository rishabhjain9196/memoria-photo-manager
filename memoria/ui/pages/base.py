"""Base class for every page plus the single, shared Find → Review → Apply → Undo flow."""
from __future__ import annotations

from typing import Any, Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ...engine import actions
from ...engine.actions import Action
from ...engine.progress import Progress
from ..widgets import AppContext, MessageDialog, confirm, fmt_n, fmt_size, hbox, label, vbox


class Page(QWidget):
    title = ""
    subtitle = ""
    glyph = "\uE80F"
    needs_library = True
    live_index_view = False

    def __init__(self, ctx: AppContext):
        super().__init__()
        self.ctx = ctx
        self.stale = True
        self.header_actions = hbox(spacing=8)
        head = vbox(label(self.title, "pageTitle"), label(self.subtitle, "pageSubtitle", wrap=True), spacing=2)
        top = hbox(head, 24, self.header_actions)
        top.setStretch(0, 1)
        top.setAlignment(self.header_actions, Qt.AlignmentFlag.AlignTop)
        self.body = QVBoxLayout()
        self.body.setSpacing(12)
        outer = vbox(top, 6, self.body, spacing=4, margins=(28, 22, 28, 16))
        self.setLayout(outer)
        ctx.library_opened.connect(self._mark_stale)
        ctx.library_modified.connect(self._mark_stale)
        ctx.runner.busy_changed.connect(self._busy_changed)
        ctx.indexing_changed.connect(self._busy_changed)

    # lifecycle ---------------------------------------------------------------------------
    @property
    def lib(self):
        return self.ctx.library

    def _busy_changed(self, busy: bool) -> None:
        self.setEnabled(not self.ctx.indexing or self.live_index_view)
        self.on_busy_changed(self.busy)
        if self.can_refresh and self.stale and self.isVisible():
            self._refresh_now()

    def _mark_stale(self) -> None:
        self.stale = True
        if self.isVisible() and self.can_refresh:
            self._refresh_now()

    def showEvent(self, e) -> None:
        super().showEvent(e)
        self.setEnabled(not self.ctx.indexing or self.live_index_view)
        self.on_busy_changed(self.busy)
        if self.stale and self.can_refresh:
            self._refresh_now()

    def _refresh_now(self) -> None:
        self.stale = False
        if self.lib is not None or not self.needs_library:
            self.refresh()

    def refresh(self) -> None:
        """Reload cheap state from the catalogue. Override."""

    def on_busy_changed(self, busy: bool) -> None:
        """Enable/disable buttons that start work. Override."""

    # helpers -----------------------------------------------------------------------------
    @property
    def busy(self) -> bool:
        return self.ctx.runner.busy or self.ctx.maintenance or self.ctx.indexing

    @property
    def can_refresh(self) -> bool:
        return not self.busy or (self.live_index_view and self.ctx.indexing and not self.ctx.maintenance)

    def run(self, title: str, fn: Callable[[Progress], Any], on_done: Optional[Callable[[Any], None]] = None,
            on_cancel: Optional[Callable[[], None]] = None, *, notify_success: bool = True) -> bool:
        if self.ctx.maintenance:
            self.ctx.toast_requested.emit("Finish the library rebuild using Resume rebuild first.", "")
            return False
        if self.ctx.indexing:
            self.ctx.toast_requested.emit("Photos can be browsed while indexing. Utilities unlock when indexing stops.", "")
            return False
        from ...engine.diagnostics import OPERATIONS
        key = self.__class__.__module__.rsplit(".", 1)[-1]
        def completed(result):
            if on_done:
                on_done(result)
            if notify_success:
                self.ctx.notification_requested.emit("results_ready", 0)
        ok = self.ctx.runner.run(title, fn, completed, on_cancel, diagnostic_key=key if key in OPERATIONS else "other")
        if not ok:
            self.ctx.toast_requested.emit(f"Please wait for “{self.ctx.runner.title}” to finish first.", "")
        return ok

    def apply_actions(self, kind: str, title: str, acts: list[Action], *, summary: str, details: list[str],
                      confirm_text: str, note: str, done_message: Callable[[actions.BatchResult], str],
                      after: Optional[Callable[[actions.BatchResult], None]] = None, rescan: bool = False) -> None:
        if not acts:
            return
        ids = [a.file_id for a in acts if a.file_id is not None]
        if not confirm(self, title, summary, details, confirm_text, note=note, thumbs=self.ctx.thumbs, file_ids=ids):
            return
        lib = self.lib

        def work(prog):
            if not rescan:
                return actions.apply(lib, kind, title, acts, prog)
            res = actions.apply(lib, kind, title, acts, prog.step(0, 2, title))
            if res.cancelled:
                return res
            from ...engine import scanner
            scanner.index(lib, prog.step(1, 2, "Updating the catalogue"))
            return res

        def done(res: actions.BatchResult):
            self.ctx.library_modified.emit()
            msg = done_message(res)
            if res.skipped:
                msg += f" {fmt_n(res.skipped, 'file')} skipped because {'it' if res.skipped == 1 else 'they'} changed since you reviewed."
            if res.cancelled:
                msg = "Stopped part-way. " + msg
            self.ctx.toast_requested.emit(msg, res.batch_id if res.done else "")
            if res.failed or res.skipped:
                self.ctx.notification_requested.emit("operation_partial", res.failed + res.skipped)
            elif res.cancelled:
                self.ctx.notification_requested.emit("task_cancelled", 0)
            elif res.done:
                self.ctx.notification_requested.emit("export_complete" if kind == "albums" else "operation_complete", res.done)
            if res.failed:
                MessageDialog(self, "Some files could not be changed",
                              f"{fmt_n(res.failed, 'file')} could not be processed. They were left exactly where they were.",
                              "\n".join(res.messages[:200])).exec()
            if after:
                after(res)

        self.run(title, work, done, on_cancel=lambda: self.ctx.library_modified.emit(), notify_success=False)


def recovery_note() -> str:
    return ("<b>Nothing is deleted.</b> Files are moved to this library's Recovery folder and every move "
            "is recorded. You can undo it from <b>History &amp; recovery</b> at any time.")


def recycle_summary(n: int, size: int) -> str:
    return f"{fmt_n(n, 'file')} ({fmt_size(size)}) will be moved to Recovery."
