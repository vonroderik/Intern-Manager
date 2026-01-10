import sqlite3
from sqlite3 import Connection, Cursor
from typing import Optional
from config import DB_PATH, SQL_PATH


class DatabaseConnector:
    """
    Handles the SQLite database connection and schema initialization.

    This class manages the lifecycle of the SQLite connection, including
    configuration (foreign keys, row factory) and initial schema execution
    from an external SQL file.

    Attributes:
        db_path (Path): Path to the SQLite database file.
        conn (Optional[Connection]): Active SQLite connection object.
        cursor (Optional[Cursor]): Active SQLite cursor object.
        _closed (bool): Internal flag to track connection status.
    """

    def __init__(self):
        """
        Initializes the DatabaseConnector and establishes the connection immediately.
        """
        self.db_path = DB_PATH
        self.conn: Optional[Connection] = None
        self.cursor: Optional[Cursor] = None
        self._closed = False

        self.connect()

    def connect(self):
        """
        Establish connection to the database and configure PRAGMA settings.

        Sets the row_factory to sqlite3.Row for dictionary-like access and
        enables foreign key constraints. Also triggers table creation.
        """
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self._create_tables()

    def _create_tables(self):
        """
        Reads the SQL script from disk and executes it to initialize the schema.

        Raises:
            FileNotFoundError: If the SQL file at SQL_PATH does not exist.
            RuntimeError: If the database connection or cursor is not active.
        """
        if not SQL_PATH.exists():
            raise FileNotFoundError(
                f"CRITICAL: Arquivo SQL não encontrado em: {SQL_PATH}"
            )

        if not self.cursor or not self.conn:
            raise RuntimeError("Database connection not established.")

        with open(SQL_PATH, "r", encoding="utf-8") as f:
            sql_file = f.read()

        self.cursor.executescript(sql_file)
        self.conn.commit()

    def rollback(self):
        """
        Rolls back the current transaction safely.
        Ignores sqlite3.Error if the connection is already in a bad state.
        """
        if self.conn:
            try:
                self.conn.rollback()
            except sqlite3.Error:
                pass

    def close(self):
        """
        Closes the cursor and connection, releasing resources.

        This method is idempotent and handles exceptions silently during closure
        to ensure the program doesn't crash while trying to exit.
        """
        if getattr(self, "_closed", False):
            return

        self.rollback()

        if self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass

        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass

        self._closed = True
