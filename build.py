"""PyInstaller build script for SniperText.

Run on Windows after installing dependencies:
    pip install -r requirements.txt pyinstaller
    python build.py
"""
import os
import shutil
import sys
from pathlib import Path
from subprocess import run as run_cmd


def find_tesseract() -> str | None:
    """Try to find the Tesseract binary on the system."""
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in common_paths:
        if os.path.isfile(path):
            return path
    return shutil.which("tesseract")


def build():
    project_root = Path(__file__).parent
    main_script = project_root / "src" / "main.py"
    icon_path = project_root / "assets" / "icon.png"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "SniperText",
        f"--add-data={icon_path}{os.pathsep}assets",
    ]

    tesseract_path = find_tesseract()
    if tesseract_path:
        tesseract_dir = str(Path(tesseract_path).parent)
        cmd.append(f"--add-binary={tesseract_dir}{os.pathsep}tesseract")
        print(f"Bundling Tesseract from: {tesseract_dir}")
    else:
        print("WARNING: Tesseract not found on this system.")
        print("The .exe will require Tesseract installed separately.")

    cmd.append(str(main_script))

    print(f"Running PyInstaller...")
    run_cmd(cmd, check=True)
    print("\nBuild complete! Output: dist/SniperText.exe")


if __name__ == "__main__":
    build()
