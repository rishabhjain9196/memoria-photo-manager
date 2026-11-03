# Double-click (or run) to start Memoria without a console window.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memoria.ui.app import main  # noqa: E402

sys.exit(main())
