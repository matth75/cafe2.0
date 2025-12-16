# Ensure the project root (the one that contains `backend/`) is on sys.path

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # /home/tazz/cafe2.0/cafe2.0
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
