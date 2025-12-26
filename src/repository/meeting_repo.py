from data.database import DatabaseConnector
from core.models.meeting import Meeting
from typing import Optional, List


class MeetingRepository:
    """
    Repository responsible for persistence and retrieval of Meeting entities.
    """

    def __init__(self, db: DatabaseConnector):
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def get_all(self) -> List[Meeting]:
        """
        Retrieves all meetings stored in the database.
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
                meeting_id=row[0],
                intern_id=row[1],
                meeting_date=row[2],
                is_intern_present=bool(row[3]),
            )
            for row in results
        ]

    def get_by_intern_id(self, intern_id: int) -> List[Meeting]:
        """
        Retrieves all meetings for a specific intern.
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
                meeting_id=row[0],
                intern_id=row[1],
                meeting_date=row[2],
                is_intern_present=bool(row[3]),
            )
            for row in results
        ]

    def save(self, meeting: Meeting) -> Optional[int]:
        """
        Persists a new Meeting entity.
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

    def delete(self, meeting: Meeting) -> bool:
        """
        Deletes a Meeting record.
        """
        if meeting.meeting_id is None:
            raise ValueError("Cannot delete a meeting without an ID")

        sql_query = "DELETE FROM meetings WHERE meeting_id = ?"

        self.cursor.execute(sql_query, (meeting.meeting_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
