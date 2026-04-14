import json
from pathlib import Path

DEFAULTS = {
    "hotkey": "ctrl+shift+t",
    "ocr_engine": "tesseract",
    "notifications": True,
    "start_on_login": False,
}


class Config:
    def __init__(self, config_dir: Path | None = None):
        if config_dir is None:
            config_dir = Path.home() / ".snipertext"
        self._path = config_dir / "config.json"
        self._data: dict = {}
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._data = {}
        else:
            self._data = {}

    def save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "hotkey": self.hotkey,
            "ocr_engine": self.ocr_engine,
            "notifications": self.notifications,
            "start_on_login": self.start_on_login,
        }
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @property
    def hotkey(self) -> str:
        return self._data.get("hotkey", DEFAULTS["hotkey"])

    @hotkey.setter
    def hotkey(self, value: str):
        self._data["hotkey"] = value

    @property
    def ocr_engine(self) -> str:
        return self._data.get("ocr_engine", DEFAULTS["ocr_engine"])

    @ocr_engine.setter
    def ocr_engine(self, value: str):
        self._data["ocr_engine"] = value

    @property
    def notifications(self) -> bool:
        return self._data.get("notifications", DEFAULTS["notifications"])

    @notifications.setter
    def notifications(self, value: bool):
        self._data["notifications"] = value

    @property
    def start_on_login(self) -> bool:
        return self._data.get("start_on_login", DEFAULTS["start_on_login"])

    @start_on_login.setter
    def start_on_login(self, value: bool):
        self._data["start_on_login"] = value
