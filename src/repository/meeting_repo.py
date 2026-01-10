from data.database import DatabaseConnector
from core.models.meeting import Meeting
from typing import Optional, List
from sqlite3 import Connection, Cursor


class MeetingRepository:
    """
    Repository responsible for persistence and retrieval of Meeting entities.

    This class handles the database interactions for supervisory meetings,
    tracking attendance and dates. It maps directly to the `meetings` table.

    Attributes:
        db (DatabaseConnector): The database connector instance.
        conn (Connection): Active SQLite connection.
        cursor (Cursor): Active SQLite cursor.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the repository with an active database connection.

        Args:
            db (DatabaseConnector): An initialized connector with an open connection.

        Raises:
            RuntimeError: If the connector does not hold a valid connection or cursor.
        """
        self.db = db
        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )
        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

    def get_all(self) -> List[Meeting]:
        """
        Retrieves all meetings stored in the database.

        Results are ordered by date in descending order (newest first).

        Returns:
            List[Meeting]: A list of all recorded meetings.
        """
        sql_query = """
        SELECT meeting_id, intern_id, meeting_date, is_intern_present
        FROM meetings
        ORDER BY meeting_date DESC
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        return [
            Meeting(
                meeting_id=row["meeting_jd"],
                intern_id=row["intern_id"],
                meeting_date=row["meeting_date"],
                is_intern_present=bool(row["is_intern_present"]),
            )
            for row in results
        ]

    def get_by_intern_id(self, intern_id: int) -> List[Meeting]:
        """
        Retrieves all meetings associated with a specific intern.

        Args:
            intern_id (int): The unique identifier of the intern.

        Returns:
            List[Meeting]: A list of Meeting objects for that intern,
            ordered by date descending.
        """
        sql_query = """
        SELECT meeting_id, intern_id, meeting_date, is_intern_present
        FROM meetings
        WHERE intern_id = ?
        ORDER BY meeting_date DESC
        """
        self.cursor.execute(sql_query, (intern_id,))
        results = self.cursor.fetchall()

        return [
            Meeting(
                meeting_id=row["meeting_id"],
                intern_id=row["intern_id"],
                meeting_date=row["meeting_date"],
                is_intern_present=bool(row["is_intern_present"]),
            )
            for row in results
        ]

    def save(self, meeting: Meeting) -> Optional[int]:
        """
        Persists a new Meeting entity.

        Args:
            meeting (Meeting): The meeting entity to save. Must not have an ID.

        Returns:
            Optional[int]: The unique identifier (primary key) of the newly created record.

        Raises:
            ValueError: If the meeting object already has an assigned ID.
            RuntimeError: If the database fails to generate an ID.
        """
        if meeting.meeting_id is not None:
            raise ValueError(
                "Cannot save a meeting that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO meetings (intern_id, meeting_date, is_intern_present)
        VALUES (?, ?, ?)
        """
        data = (meeting.intern_id, meeting.meeting_date, meeting.is_intern_present)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID for the new meeting.")
        return self.cursor.lastrowid

    def delete(self, meeting_id: int) -> bool:
        """
        Permanently deletes a Meeting record.

        Args:
            meeting (Meeting): The meeting entity to delete. Must have an ID.

        Returns:
            bool: True if the deletion was successful, False otherwise.

        Raises:
            ValueError: If the meeting object does not have an ID.
        """

        if not meeting_id:
            raise ValueError("Cannot delete a meeting without a valid ID")

        sql_query = "DELETE FROM meetings WHERE meeting_id = ?"

        self.cursor.execute(sql_query, (meeting_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
