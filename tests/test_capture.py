from unittest.mock import patch, MagicMock
from PIL import Image

from src.capture import capture_region


@patch("src.capture.mss")
def test_capture_region_returns_pil_image(mock_mss_module):
    """capture_region should return a PIL Image of the selected area."""
    mock_sct = MagicMock()
    mock_mss_module.mss.return_value.__enter__ = MagicMock(return_value=mock_sct)
    mock_mss_module.mss.return_value.__exit__ = MagicMock(return_value=False)

    fake_img = Image.new("RGB", (100, 50), "red")
    mock_grab = MagicMock()
    mock_grab.rgb = fake_img.tobytes()
    mock_grab.size = (100, 50)
    mock_sct.grab.return_value = mock_grab

    result = capture_region(10, 20, 110, 70)

    assert isinstance(result, Image.Image)
    assert result.size == (100, 50)
    mock_sct.grab.assert_called_once_with({"left": 10, "top": 20, "width": 100, "height": 50})


@patch("src.capture.mss")
def test_capture_region_clamps_negative_coords(mock_mss_module):
    """Negative coordinates should be clamped to 0."""
    mock_sct = MagicMock()
    mock_mss_module.mss.return_value.__enter__ = MagicMock(return_value=mock_sct)
    mock_mss_module.mss.return_value.__exit__ = MagicMock(return_value=False)

    fake_img = Image.new("RGB", (50, 50), "blue")
    mock_grab = MagicMock()
    mock_grab.rgb = fake_img.tobytes()
    mock_grab.size = (50, 50)
    mock_sct.grab.return_value = mock_grab

    capture_region(-10, -20, 40, 30)

    call_args = mock_sct.grab.call_args[0][0]
    assert call_args["left"] == 0
    assert call_args["top"] == 0


def test_capture_region_swaps_inverted_coords():
    """If user drags right-to-left or bottom-to-top, coords should be normalized."""
    from src.capture import _normalize_coords

    left, top, right, bottom = _normalize_coords(200, 300, 100, 150)
    assert left == 100
    assert top == 150
    assert right == 200
    assert bottom == 300
