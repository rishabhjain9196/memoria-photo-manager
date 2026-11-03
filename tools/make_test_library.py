"""CLI wrapper: generate the test library. See memoria/samplelib.py for what it contains."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memoria.samplelib import build, main  # noqa: E402,F401

if __name__ == "__main__":
    main()
