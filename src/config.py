import sys
from pathlib import Path


def get_project_root() -> Path:
    """
    Retorna a raiz absoluta do projeto.
    Detecta se está rodando como script (.py) ou executável congelado (.exe).
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
