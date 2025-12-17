from data.database import DatabaseConnector
from core.models.meeting import Meeting
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


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
            return None

        sql_query = """
        INSERT INTO meetings (intern_id, meeting_date, is_intern_present)
        VALUES (?, ?, ?)
        """
        data = (meeting.intern_id, meeting.meeting_date, meeting.is_intern_present)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        return self.cursor.lastrowid

    def delete(self, meeting: Meeting) -> bool:
        """
        Deletes a Meeting record.
        """
        if meeting.meeting_id is None:
            return False

        sql_query = "DELETE FROM meetings WHERE meeting_id = ?"
        try:
            self.cursor.execute(sql_query, (meeting.meeting_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Erro ao deletar Meeting {meeting.meeting_id}: {e}")
            return False
