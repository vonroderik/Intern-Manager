from pathlib import Path
import sqlite3


def get_project_root() -> Path:
    """
    Returns the absolute path to a file inside the project resources directory.

    Args:
        filename (str): Name of the resource file.

    Returns:
        Path: Absolute path to the requested resource.
    """

    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent


def get_db_path() -> Path:
    """Returns the path to the SQLite database file."""

    root = get_project_root()
    db_path = root / "resources" / "interns.db"

    db_path.parent.mkdir(parents=True, exist_ok=True)

    return db_path


def get_sql_path() -> Path:
    """Returns the path to the SQL DDL file."""

    root = get_project_root()
    return root / "resources" / "create_db.sql"


class DatabaseConnector:
    """
    Handles the SQLite database connection and schema initialization.

    This class is responsible for:
        - Opening a connection to the SQLite database.
        - Enabling foreign key constraints.
        - Creating database tables from an external SQL DDL file.

    The database schema is automatically created (if not already present)
    during object initialization using the SQL script located at the path
    returned by `get_sql_path()`.

    Attributes:
        conn (sqlite3.Connection): Active SQLite database connection.
        cursor (sqlite3.Cursor): Cursor associated with the database connection.
    """

    def __init__(self):
        """
        Initializes the database connection and ensures the schema exists.

        This constructor:
            - Connects to the SQLite database defined by `get_db_path()`.
            - Creates a database cursor.
            - Enables foreign key constraint enforcement.
            - Creates database tables if they do not exist.

        Raises:
            sqlite3.Error: If the database connection fails.
        """
        self.db_path = get_db_path()

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self._closed = False

        self._create_tables()

    def _create_tables(self):
        """
        Creates database tables using an external SQL DDL script.

        The method reads a SQL file containing DDL statements and executes
        them using `executescript`. If the SQL file is not found, the method
        prints an error message and aborts the table creation process.

        The transaction is committed after successful execution.

        Notes:
            - This method assumes the SQL file is idempotent
              (i.e., uses IF NOT EXISTS).
            - Errors related to SQL execution are not explicitly handled.
        """

        sql_path = get_sql_path()

        if not sql_path.exists():
            raise FileNotFoundError(
                f"CRITICAL: ARquivo 'create_db.sql' não encontrado em: {sql_path}\n"
                f"Verifique se o arquivo esta na pasta 'resources' na raiz do projeto"
            )

        try:
            with open(sql_path, "r", encoding="utf-8") as f:
                sql_file = f.read()
            self.cursor.executescript(sql_file)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"CRITICAL: Erro de SQL ao criar tabelas: {e}")
            raise

    def rollback(self):
        try:
            self.conn.rollback()
        except Exception:
            pass

    def close(self):
        """
        Closes the database connection.
        """

        if getattr(self, "_closed", False):
            return

        try:
            self.rollback()
        finally:
            try:
                self.cursor.close()
            except Exception:
                pass
            try:
                self.conn.close()
            except Exception:
                pass
            finally:
                self._closed = True
