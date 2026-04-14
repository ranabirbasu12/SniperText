from src.ocr.base import OCREngine
from src.ocr.tesseract import TesseractEngine

ENGINE_REGISTRY: dict[str, type[OCREngine]] = {
    "tesseract": TesseractEngine,
}


def get_engine(name: str) -> OCREngine:
    """Instantiate an OCR engine by its config name."""
    engine_cls = ENGINE_REGISTRY.get(name)
    if engine_cls is None:
        raise ValueError(f"Unknown OCR engine: {name!r}. Available: {list(ENGINE_REGISTRY)}")
    return engine_cls()


__all__ = ["OCREngine", "TesseractEngine", "get_engine", "ENGINE_REGISTRY"]
