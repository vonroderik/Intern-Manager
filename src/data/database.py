from pathlib import Path
import sqlite3

def get_db_path() -> Path:
    """Returns the path to the SQLite database file."""

    return get_resource_path("interns.db")

def get_resource_path(filename: str) -> Path:
    """
    Returns the absolute path to a file inside the project resources directory.

    Args:
        filename (str): Name of the resource file.

    Returns:
        Path: Absolute path to the requested resource.
    """

    script_path = Path(__file__).parent.absolute()
    project_folder = script_path.parent.parent
    return project_folder / "resources" / filename


def get_sql_path() -> Path:
    """Returns the path to the SQL DDL file."""

    return get_resource_path("create_db.sql")


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

        self.conn = sqlite3.connect(get_db_path())
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
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

        try:
            with open(sql_path, "r") as f:
                sql_file = f.read()
        except FileNotFoundError:
            print(f"ERRO: Arquivo DDL não encontrado em: {sql_path}")
            return

        self.cursor.executescript(sql_file)
        self.conn.commit()
