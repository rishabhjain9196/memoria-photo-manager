"""Base class for every page plus the single, shared Find → Review → Apply → Undo flow."""
from __future__ import annotations

from html import escape
from typing import Any, Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ...engine import actions
from ...engine.actions import Action
from ...engine.progress import Progress
from .. import nav
from ..widgets import AppContext, MessageDialog, confirm, fmt_n, fmt_size, hbox, icon_chip, label, vbox

# Read-only tasks that still write catalogue structure (rescans, comparison indexes, face data): only the
# window that owns the library runs them.
VIEWER_BLOCKED = {"health", "compare", "people"}


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
        found = nav.identity(self.title)
        if found:
            chip = icon_chip(found[1], nav.color(self.title), 20, 40)
            top.insertWidget(0, chip)
            top.insertSpacing(1, 6)
            top.setStretch(0, 0)
            top.setStretch(2, 1)
            top.setAlignment(chip, Qt.AlignmentFlag.AlignTop)
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
            on_cancel: Optional[Callable[[], None]] = None, *, notify_success: bool = True,
            read_only: bool = False) -> bool:
        """Start a task. ``read_only`` tasks (they only read files and the catalogue) run side by side;
        anything that changes files runs alone."""
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
        diagnostic_key = key if key in OPERATIONS else "other"
        if read_only:
            if self.ctx.runner.viewer and key in VIEWER_BLOCKED:
                self.ctx.toast_requested.emit(f"{self.title} updates the catalogue, so run it in the Memoria window "
                                              "that opened this library first.", "")
                return False
            ok = self.ctx.parallel.run(title, fn, completed, on_cancel, diagnostic_key=diagnostic_key)
            if not ok:
                self.ctx.toast_requested.emit(
                    f"Please wait for “{self.ctx.parallel.refusal}” to finish first." if self.ctx.runner.busy else
                    f"“{title}” is already running — see the task bar.", "")
            return ok
        ok = self.ctx.runner.run(title, fn, completed, on_cancel, diagnostic_key=diagnostic_key)
        if not ok and not self.ctx.runner.viewer:
            self.ctx.toast_requested.emit(f"Please wait for “{self.ctx.runner.refusal}” to finish first. Changes "
                                          "don't run while a search is still reading the library.", "")
        return ok

    def apply_actions(self, kind: str, title: str, acts: list[Action], *, summary: str, details: list[str],
                      confirm_text: str, note: str, done_message: Callable[[actions.BatchResult], str],
                      after: Optional[Callable[[actions.BatchResult], None]] = None, rescan: bool = False,
                      require_ack: Optional[str] = None, confirm_action: bool = True,
                      before_apply: Optional[Callable[[], None]] = None,
                      on_declined: Optional[Callable[[], None]] = None) -> bool:
        if not acts:
            return False
        lib = self.lib

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

        def prepare(prog):
            from ...engine import assets
            prog.update(0, 0, "Reviewing linked photo, video and edit components...", force=True)
            try:
                return assets.prepare(lib, acts, kind)
            finally:
                lib.close_thread()

        def ready(prepared):
            plan = prepared.actions
            shown_details, acknowledgement, shown_summary = list(details), require_ack, summary
            shown_confirm = confirm_text
            if prepared.groups:
                count = sum(action.op != "rmdir" for action in plan)
                size = sum(action.size for action in plan)
                shown_summary = f"Final plan: {fmt_n(count, 'file')} ({fmt_size(size)}), including linked components."
                shown_confirm = ("Copy " if all(action.op in ("copy", "rmdir") for action in plan) else "Move ") + \
                    fmt_n(count, "file")
                shown_details[:0] = [
                    (f"<b>{prepared.extra_files} additional linked component(s) are included.</b>"
                     if prepared.extra_files else "<b>The reviewed linked components are handled together.</b>"),
                    "Matching names in the same folder link Live Photo image/video parts, RAW+JPEG and AAE/XMP "
                    "sidecars. Review these inferred links; Apple edit instructions are not applied.",
                    ("Additional components can include unique videos and edit sidecars."
                     if prepared.extra_files else "No additional linked files were added to this selection."),
                    *[" + ".join(escape(row["name"]) for row in group[:4])
                      + (f" (+{len(group) - 4} parts)" if len(group) > 4 else "")
                      for group in prepared.groups[:3]],
                ]
                if len(prepared.groups) > 3:
                    shown_details.append(f"{len(prepared.groups) - 3} more linked assets are included. "
                                         "Cancel and review smaller selections if needed.")
                acknowledgement = ((require_ack + " ") if require_ack else "") + \
                    "I reviewed the linked parts, including any unique video or edit files."
            if prepared.merges:
                shown_details.append(
                    f"<b>Organisation is preserved in retained copies ({len(prepared.merges)} merge(s)).</b> "
                    "Tags, static album membership and favourites are combined. Unset ratings/review states are "
                    "filled; the keeper wins conflicts. Face records and health baselines are not transferred. "
                    "Undo restores organisation only if it has not subsequently changed.")
            ids = [action.file_id for action in plan if action.file_id is not None]
            if (confirm_action or prepared.groups) and not confirm(
                    self, title, shown_summary, shown_details, shown_confirm, note=note,
                    thumbs=self.ctx.thumbs, file_ids=ids, require_ack=acknowledgement,
                    danger=bool(acknowledgement), note_kind="warn" if acknowledgement else "trust"):
                self.ctx.toast_requested.emit("Nothing was changed.", "")
                if on_declined:
                    on_declined()
                return

            def work(prog):
                try:
                    prog.check()
                    if before_apply:
                        before_apply()
                    result = actions.apply(lib, kind, title, plan,
                                           prog.step(0, 2, title) if rescan else prog, companions_reviewed=True)
                    if rescan and not result.cancelled:
                        from ...engine import scanner
                        scanner.index(lib, prog.step(1, 2, "Updating the catalogue"))
                    return result
                finally:
                    lib.close_thread()
            if not self.run(title, work, done, on_cancel=lambda: self.ctx.library_modified.emit(),
                            notify_success=False) and on_declined:
                on_declined()

        return self.run("Preparing " + title, prepare, ready, notify_success=False)


def recovery_note() -> str:
    return ("<b>Nothing is deleted.</b> Files are moved to this library's Recovery folder and every move "
            "is recorded. You can undo it from <b>History &amp; recovery</b> until Recovery is emptied.")


def recycle_summary(n: int, size: int) -> str:
    return f"{fmt_n(n, 'file')} ({fmt_size(size)}) will be moved to Recovery."
