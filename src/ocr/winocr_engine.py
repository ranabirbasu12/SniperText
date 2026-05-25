from winocr import recognize_pil_sync
from PIL import Image

from src.ocr.base import OCREngine


class WindowsOCREngine(OCREngine):
    def __init__(self, lang: str = "en"):
        self._lang = lang

    def extract_text(self, image: Image.Image) -> str:
        if image.mode != "RGB":
            image = image.convert("RGB")
        result = recognize_pil_sync(image, self._lang)
        lines = [line["text"].rstrip() for line in result.get("lines", [])]
        return "\n".join(lines).strip()

    def name(self) -> str:
        return "Windows OCR"
