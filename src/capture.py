import mss
from PIL import Image


def _normalize_coords(x1: int, y1: int, x2: int, y2: int) -> tuple[int, int, int, int]:
    """Ensure left < right and top < bottom, clamp negatives to 0."""
    left = max(0, min(x1, x2))
    top = max(0, min(y1, y2))
    right = max(x1, x2)
    bottom = max(y1, y2)
    return left, top, right, bottom


def capture_region(x1: int, y1: int, x2: int, y2: int) -> Image.Image:
    """Capture a screenshot of the specified screen region.

    Args:
        x1, y1: Top-left corner (or any corner - coordinates are normalized).
        x2, y2: Bottom-right corner (or any corner).

    Returns:
        PIL Image of the captured region.
    """
    left, top, right, bottom = _normalize_coords(x1, y1, x2, y2)
    width = right - left
    height = bottom - top

    monitor = {"left": left, "top": top, "width": width, "height": height}

    with mss.mss() as sct:
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

    return img
