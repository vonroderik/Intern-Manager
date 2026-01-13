import sys
import os
from pathlib import Path

def get_app_paths():
    """
    Define os caminhos de execução e de dados do usuário.
    Compatível com PyInstaller moderno (pasta _internal).
    """
    # 1. Local do código/resources? (READ-ONLY)
    if getattr(sys, "frozen", False):

        if hasattr(sys, '_MEIPASS'):
            app_root = Path(sys._MEIPASS) # type:ignore
        else:
            app_root = Path(sys.executable).parent
    else:
        # Modo Desenvolvimento
        app_root = Path(__file__).resolve().parent.parent

    # 2. Local do banco de dados (WRITABLE)
    if getattr(sys, "frozen", False):

        base_path = os.getenv('APPDATA') or os.path.expanduser("~")
        user_data_root = Path(base_path) / "InternManager"
    else:
        user_data_root = app_root / "data"

    return app_root, user_data_root

# --- Configuração Global ---
APP_ROOT, USER_DATA_ROOT = get_app_paths()

# Recursos estáticos (SQL, Imagens) - Ficam dentro de _internal no EXE
RESOURCES_DIR = APP_ROOT / "resources"
SQL_PATH = RESOURCES_DIR / "create_db.sql"

# Dados dinâmicos (Banco de Dados) - Ficam no AppData do usuário
DB_DIR = USER_DATA_ROOT
DB_PATH = DB_DIR / "interns.db"

# --- Debug Crítico ---

#if getattr(sys, "frozen", False):
#    print(f"DEBUG: Rodando Congelado (Frozen)")
#    print(f"DEBUG: App Root (_internal): {APP_ROOT}")
#    print(f"DEBUG: Resources esperados: {RESOURCES_DIR}")
#    print(f"DEBUG: SQL esperado: {SQL_PATH}")

# Garante a criação da pasta de DADOS (não a de resources)
DB_DIR.mkdir(parents=True, exist_ok=True)