import sys
from pathlib import Path


def get_project_root() -> Path:
    """
    Determines the absolute root directory of the project.

    This utility ensures path compatibility across development (script-based)
    and production (executable-based) environments.

    - If running as a frozen executable (e.g., PyInstaller), returns the executable's directory.
    - If running from source, calculates the root based on this file's location.

    Returns:
        Path: The absolute path object pointing to the project root.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    # src/config.py -> parent (src) -> parent (root)
    return Path(__file__).resolve().parent.parent


# Global Constants
PROJECT_ROOT = get_project_root()
DATA_DIR = PROJECT_ROOT / "data"
RESOURCES_DIR = PROJECT_ROOT / "resources"
DB_PATH = RESOURCES_DIR / "interns.db"
SQL_PATH = RESOURCES_DIR / "create_db.sql"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)