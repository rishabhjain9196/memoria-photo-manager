"""Task-bar rows for read-only tasks that run side by side (see ``tasks.ParallelTasks``)."""
from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QProgressBar, QSizePolicy, QVBoxLayout

from ..engine import activity
from .task_stats import TaskStats
from .widgets import button, hbox, label


class _Row(QFrame):
    def __init__(self, bar: "ParallelBar", task):
        super().__init__()
        self.task_id = task.id
        self.stats = TaskStats()
        self.title = label(task.title + ("  · background" if task.background else ""), "h2")
        self.message = label("", "muted")
        self.message.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.pct = label("", "small")
        self.speed = label("", "small")
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.pause = button("Pause", on_click=lambda: bar.ctx.parallel.toggle_pause(self.task_id))
        self.cancel = button("Cancel", on_click=lambda: bar.ctx.parallel.cancel(self.task_id))
        top = hbox(self.title, self.message, 10, self.pct, 10, self.speed, 10, self.pause, self.cancel)
        top.setStretch(1, 1)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(4)
        lay.addLayout(top)
        lay.addWidget(self.progress)

    def render(self, task) -> None:
        fraction = task.fraction
        self.stats.update(fraction, task.detail)
        paused = task.pause.is_set()
        self.message.setText(("Paused while a change runs — " if task.held else "Paused — " if paused else "")
                             + task.message)
        self.message.setToolTip(task.message)
        if fraction is None:
            self.progress.setRange(0, 0)
            self.pct.setText("")
        else:
            self.progress.setRange(0, 1000)
            self.progress.setValue(int(1000 * fraction))
            self.pct.setText(f"{fraction:.0%}")
        parts = [p for p in (self.stats.speed_text(), self.stats.time_text()) if p]
        self.speed.setText(" · ".join(parts))
        self.pause.setText("Resume" if paused and not task.held else "Pause")
        self.pause.setEnabled(not task.held)


class ParallelBar(QFrame):
    """One row per running read-only task, above the main task bar."""

    def __init__(self, ctx, paths=lambda: ()):
        super().__init__()
        self.setObjectName("taskBar")
        self.ctx = ctx
        self.paths = paths
        self.rows: dict[int, _Row] = {}
        self.system = label("", "small")
        self.system.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.system_stats = TaskStats()
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(28, 8, 28, 10)
        self.layout_.setSpacing(6)
        self.layout_.addWidget(self.system)
        ctx.parallel.changed.connect(self._sync)
        ctx.parallel.progressed.connect(self._progress)
        ctx.runner.busy_changed.connect(lambda _busy: self._tick())
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)
        self.hide()

    def _sync(self) -> None:
        tasks = self.ctx.parallel.tasks
        for task_id in [i for i in self.rows if i not in tasks]:
            row = self.rows.pop(task_id)
            self.layout_.removeWidget(row)
            row.deleteLater()
        for task_id, task in tasks.items():
            if task_id not in self.rows:
                row = _Row(self, task)
                self.rows[task_id] = row
                self.layout_.insertWidget(self.layout_.count() - 1, row)
            self.rows[task_id].render(task)
        visible = bool(tasks)
        if visible and self.isHidden():
            self.system_stats.start()
            self.timer.start()
        elif not visible:
            self.timer.stop()
        self.setVisible(visible)
        self._tick()

    def _progress(self, task_id: int) -> None:
        task, row = self.ctx.parallel.tasks.get(task_id), self.rows.get(task_id)
        if task and row:
            row.render(task)

    def _tick(self) -> None:
        for task_id, row in self.rows.items():
            task = self.ctx.parallel.tasks.get(task_id)
            if task:
                row.render(task)
        # The main task bar shows system activity while a change runs; otherwise it is shown here.
        show = bool(self.rows) and not self.ctx.runner.busy
        self.system.setVisible(show)
        if show:
            self.system_stats.system(activity.snapshot(self.paths()))
            text = self.system_stats.system_text()
            self.system.setText(text)
            self.system.setToolTip(text.replace("   ·   ", "\n"))
