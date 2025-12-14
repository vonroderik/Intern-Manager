from pathlib import Path
import sqlite3


def get_db_path() -> Path:
    """Finds the path to the database"""

    script_path = Path(__file__).parent.absolute()
    src_folder = script_path.parent
    project_folder = src_folder.parent
    db_path = project_folder / "resources" / "interns.db"

    return db_path


def get_sql_path() -> Path:
    """Finds the path to create_db.sql file, which has the query to create the Database"""

    script_path = Path(__file__).parent.absolute()
    src_folder = script_path.parent
    project_folder = src_folder.parent
    sql_file_path = project_folder / "resources" / "create_db.sql"

    return sql_file_path


class DatabaseConnector:
    """Creates the connection with the SQL database"""

    def __init__(self):
        self.con = sqlite3.connect(get_db_path())
        self.cur = self.con.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self):
        """Creates the database tables if they don't exist"""

        sql_path = get_sql_path()

        try:
            with open(sql_path, "r") as f:
                sql_file = f.read()
        except FileNotFoundError:
            print(f"ERRO: Arquivo DDL não encontrado em: {sql_path}")
            return

        self.cur.executescript(sql_file)
        self.con.commit()
