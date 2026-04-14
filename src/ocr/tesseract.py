import pytesseract
from PIL import Image, ImageFilter

from src.ocr.base import OCREngine


class TesseractEngine(OCREngine):
    def extract_text(self, image: Image.Image) -> str:
        processed = self._preprocess(image)
        raw_text = pytesseract.image_to_string(processed)
        return self._clean_text(raw_text)

    def name(self) -> str:
        return "Tesseract"

    def _preprocess(self, image: Image.Image) -> Image.Image:
        grayscale = image.convert("L")
        sharpened = grayscale.filter(ImageFilter.SHARPEN)
        return sharpened

    def _clean_text(self, text: str) -> str:
        lines = text.strip().splitlines()
        cleaned_lines = [line.rstrip() for line in lines]
        result = "\n".join(cleaned_lines).strip()
        return result
