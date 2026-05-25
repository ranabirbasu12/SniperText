"""Manage start-on-login via the user's Startup folder (no admin needed)."""
import sys
from pathlib import Path


def _get_exe_path() -> Path:
    """Get the path to the running executable."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable)
    return Path(sys.executable)


def _get_startup_folder() -> Path:
    """Get the user's Windows Startup folder."""
    import os
    appdata = os.environ.get("APPDATA", "")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _shortcut_path() -> Path:
    return _get_startup_folder() / "SniperText.vbs"


def enable_startup():
    """Add SniperText to the user's Startup folder via a VBS launcher."""
    startup_dir = _get_startup_folder()
    if not startup_dir.exists():
        return

    project_dir = str(Path(__file__).parent.parent)
    if getattr(sys, "frozen", False):
        exe = str(_get_exe_path())
        script = f'CreateObject("WScript.Shell").Run """{exe}""", 0, False\n'
    else:
        pythonw = str(Path(sys.executable).parent / "pythonw.exe")
        pyw = str(Path(project_dir) / "run.pyw")
        script = (
            f'CreateObject("WScript.Shell").Run '
            f'""""{pythonw}"" ""{pyw}""""", 0, False\n'
        )

    _shortcut_path().write_text(script, encoding="utf-8")


def disable_startup():
    """Remove SniperText from the user's Startup folder."""
    shortcut = _shortcut_path()
    if shortcut.exists():
        shortcut.unlink()


def is_startup_enabled() -> bool:
    """Check if SniperText is in the Startup folder."""
    return _shortcut_path().exists()


def sync_startup(enabled: bool):
    """Enable or disable startup based on config value."""
    if enabled:
        enable_startup()
    else:
        disable_startup()
