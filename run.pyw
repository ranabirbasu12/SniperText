"""Launch SniperText - double-click this file to start."""
import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import main
main()
