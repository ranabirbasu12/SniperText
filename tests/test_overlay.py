"""Tests for overlay coordinate logic. UI rendering is tested manually."""
from src.overlay import CaptureOverlay


def test_selection_rect_none_before_drag(qtbot):
    """Before any mouse interaction, selection_rect should be None."""
    overlay = CaptureOverlay()
    qtbot.addWidget(overlay)
    assert overlay.selection_rect is None


def test_zero_size_selection_is_ignored(qtbot):
    """A click without drag should not produce a selection."""
    overlay = CaptureOverlay()
    qtbot.addWidget(overlay)
    overlay._start_pos = (100, 100)
    overlay._end_pos = (100, 100)
    assert overlay._is_valid_selection() is False


def test_valid_selection(qtbot):
    """A proper drag should be considered valid."""
    overlay = CaptureOverlay()
    qtbot.addWidget(overlay)
    overlay._start_pos = (100, 100)
    overlay._end_pos = (200, 250)
    assert overlay._is_valid_selection() is True


def test_small_selection_is_ignored(qtbot):
    """A drag smaller than 5px in either dimension should be ignored."""
    overlay = CaptureOverlay()
    qtbot.addWidget(overlay)
    overlay._start_pos = (100, 100)
    overlay._end_pos = (103, 102)
    assert overlay._is_valid_selection() is False
