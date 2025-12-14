from data.database import DatabaseConnector
from core.models.intern import Intern
from typing import Optional, List


class InternRepository:
    def __init__(self, db: DatabaseConnector):
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def save(self, intern: Intern) -> Optional[int]:
        if intern.intern_id is not None:
            return None

        sql_query = """
INSERT INTO interns (
name, registration_number, term, email, start_date, end_date, working_days, working_hours, venue_id) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

        data = (
            intern.name,
            intern.registration_number,
            intern.term,
            intern.email,
            intern.start_date,
            intern.end_date,
            intern.working_days,
            intern.working_hours,
            intern.venue_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        return self.cursor.lastrowid

    def get_all(self) -> List[Intern]: ...
