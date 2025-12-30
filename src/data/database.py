import sqlite3
from sqlite3 import Connection, Cursor
from typing import Optional
from config import DB_PATH, SQL_PATH

class DatabaseConnector:
    """
    Handles the SQLite database connection and schema initialization.
    """

    def __init__(self):
        self.db_path = DB_PATH
        self.conn: Optional[Connection] = None
        self.cursor: Optional[Cursor] = None
        self._closed = False
        
        self.connect()

    def connect(self):
        """Establish connection and configure PRAGMA."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        self._create_tables()

    def _create_tables(self):
        if not SQL_PATH.exists():
            raise FileNotFoundError(
                f"CRITICAL: Arquivo SQL não encontrado em: {SQL_PATH}"
            )
        
        # Pylance check: Garante que cursor existe antes de usar
        if not self.cursor or not self.conn:
            raise RuntimeError("Database connection not established.")

        with open(SQL_PATH, "r", encoding="utf-8") as f:
            sql_file = f.read()
        
        self.cursor.executescript(sql_file)
        self.conn.commit()

    def rollback(self):
        if self.conn:
            try:
                self.conn.rollback()
            except sqlite3.Error:
                pass

    def close(self):
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