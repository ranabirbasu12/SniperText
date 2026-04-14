import json
from pathlib import Path

from src.config import Config


def test_default_values():
    """Config should have sensible defaults without a config file."""
    config = Config.__new__(Config)
    config._data = {}
    config._path = Path("/nonexistent/config.json")
    assert config.hotkey == "ctrl+shift+t"
    assert config.ocr_engine == "tesseract"
    assert config.notifications is True
    assert config.start_on_login is False


def test_load_from_file(tmp_path):
    """Config should load values from a JSON file."""
    config_file = tmp_path / ".snipertext" / "config.json"
    config_file.parent.mkdir(parents=True)
    config_file.write_text(json.dumps({
        "hotkey": "ctrl+alt+s",
        "ocr_engine": "tesseract",
        "notifications": False,
        "start_on_login": True,
    }))
    config = Config(config_dir=tmp_path / ".snipertext")
    assert config.hotkey == "ctrl+alt+s"
    assert config.notifications is False
    assert config.start_on_login is True


def test_save_to_file(tmp_path):
    """Config.save() should persist current values to disk."""
    config_dir = tmp_path / ".snipertext"
    config = Config(config_dir=config_dir)
    config.hotkey = "ctrl+shift+x"
    config.save()

    raw = json.loads((config_dir / "config.json").read_text())
    assert raw["hotkey"] == "ctrl+shift+x"


def test_creates_config_dir_if_missing(tmp_path):
    """Config should create its directory on save if it doesn't exist."""
    config_dir = tmp_path / ".snipertext"
    assert not config_dir.exists()
    config = Config(config_dir=config_dir)
    config.save()
    assert config_dir.exists()
    assert (config_dir / "config.json").exists()


def test_malformed_json_falls_back_to_defaults(tmp_path):
    """Config should use defaults if the config file contains invalid JSON."""
    config_dir = tmp_path / ".snipertext"
    config_dir.mkdir(parents=True)
    (config_dir / "config.json").write_text("NOT JSON{{{")
    config = Config(config_dir=config_dir)
    assert config.hotkey == "ctrl+shift+t"
