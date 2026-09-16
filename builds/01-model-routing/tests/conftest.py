import sys
from pathlib import Path

# Tests import the build's modules directly; src/ is the package root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
