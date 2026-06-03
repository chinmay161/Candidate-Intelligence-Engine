"""Entry point script for generation of submission."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from submission.cli import main

if __name__ == "__main__":
    main()
