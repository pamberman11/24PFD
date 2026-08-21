import sys
from pathlib import Path

# Make the 24PFD package directory (parent of tests/) importable as top-level
# modules (main, config, back_front_ws), matching how the app runs in prod.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
