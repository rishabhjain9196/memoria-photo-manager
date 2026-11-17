"""Short, cheap UI transitions that never block work and switch off when motion is unwanted.

Every animation is purely cosmetic: it is under 200 ms, owned by the widget it animates,
and leaves the widget in its final state if it is interrupted, so no code path depends on it.
"""
from __future__ import annotations

import os

from PySide6.QtCore import QEasingCurve, QObject, QPoint, QPropertyAnimation, Qt
from PySide6.QtWidgets import QApplication, QDialog, QGraphicsOpacityEffect, QWidget

FAST = 120
NORMAL = 160
_ANIMATION = "_memoria_animation"
_reduced: bool | None = None


def _windows_animations_off() -> bool:
    """Respect Windows' "Animation effects" accessibility switch."""
    if os.name != "nt":
        return False
    try:
        import ctypes
        enabled = ctypes.c_int(1)
        # SPI_GETCLIENTAREAANIMATION
        if ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(enabled), 0):
            return not enabled.value
    except Exception:
        pass
    return False


def reduced() -> bool:
    global _reduced
    if _reduced is None:
        from . import theme
        try:
            preference = theme.settings().value("reduce_motion", False, bool)
        except Exception:
            preference = False
        _reduced = bool(preference or os.environ.get("MEMORIA_REDUCE_MOTION")
                        or _windows_animations_off())
    return _reduced


def set_reduced(value: bool) -> None:
    global _reduced
    from . import theme
    theme.settings().setValue("reduce_motion", bool(value))
    _reduced = None


def enabled() -> bool:
    app = QApplication.instance()
    if app is None or reduced():
        return False
    # Offscreen/minimal platforms (tests, screenshots, remote tools) render frames on demand.
    return QApplication.platformName() not in ("offscreen", "minimal")


def _start(owner: QObject, animation: QPropertyAnimation, done=None) -> None:
    previous = getattr(owner, _ANIMATION, None)
    if previous is not None:
        try:
            previous.stop()
        except RuntimeError:
            pass
    setattr(owner, _ANIMATION, animation)

    def finished():
        if getattr(owner, _ANIMATION, None) is animation:
            setattr(owner, _ANIMATION, None)
        if done is not None:
            done()
    animation.finished.connect(finished)
    animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


def fade_in(widget: QWidget, duration: int = NORMAL) -> None:
    """Fade a child widget in. The temporary opacity effect is removed afterwards for full-speed painting."""
    if not enabled() or widget is None or not widget.isVisible():
        return
    if widget.graphicsEffect() is not None and not isinstance(widget.graphicsEffect(), QGraphicsOpacityEffect):
        return  # Never replace a widget's own effect.
    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(0.0)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", effect)
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def clear():
        try:
            if widget.graphicsEffect() is effect:
                widget.setGraphicsEffect(None)
        except RuntimeError:
            pass
    _start(widget, animation, clear)


def slide_in(widget: QWidget, target: QPoint, offset: int = 14, duration: int = NORMAL) -> None:
    """Move a floating child widget to ``target``, gliding up from just below it when motion is on."""
    if not enabled():
        widget.move(target)
        return
    widget.move(target + QPoint(0, offset))
    animation = QPropertyAnimation(widget, b"pos", widget)
    animation.setDuration(duration)
    animation.setStartValue(target + QPoint(0, offset))
    animation.setEndValue(target)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    _start(widget, animation, lambda: widget.move(target))


def fade_window(window: QWidget, duration: int = FAST) -> None:
    if not enabled() or not window.isWindow():
        return
    window.setWindowOpacity(0.0)
    animation = QPropertyAnimation(window, b"windowOpacity", window)
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    _start(window, animation, lambda: window.setWindowOpacity(1.0))


class Dialog(QDialog):
    """Base for Memoria dialogs: fades in on first show; otherwise a plain QDialog."""

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if not self.property("_memoria_shown"):
            self.setProperty("_memoria_shown", True)
            fade_window(self)


def install(app: QApplication) -> None:
    if app is not None:
        app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, enabled())
        app.setEffectEnabled(Qt.UIEffect.UI_AnimateMenu, enabled())
        app.setEffectEnabled(Qt.UIEffect.UI_FadeMenu, enabled())
        app.setEffectEnabled(Qt.UIEffect.UI_AnimateTooltip, enabled())
        app.setEffectEnabled(Qt.UIEffect.UI_FadeTooltip, enabled())
