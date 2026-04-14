from abc import ABC, abstractmethod
from PIL import Image


class OCREngine(ABC):
    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        """Takes a PIL Image, returns extracted text string."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Returns human-readable engine name for settings UI."""
        pass
