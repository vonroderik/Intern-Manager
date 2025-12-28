from data.database import DatabaseConnector
from core.models.grade import Grade
from typing import Optional, List


class GradeRepository:
    """
    Repository responsible for persistence and retrieval of Grade entities.
    """

    def __init__(self, db: DatabaseConnector):
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def get_all(self) -> List[Grade]:
        """
        Retrieves all grades stored in the database.
        """
        sql_query = """
        SELECT grade_id, intern_id, criteria_id, value, last_update
        FROM grades
        ORDER BY last_update DESC
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        return [
            Grade(
                grade_id=row[0],
                intern_id=row[1],
                criteria_id=row[2],
                value=row[3],
                last_update=row[4],
            )
            for row in results
        ]

    def get_by_intern_id(self, intern_id: int) -> List[Grade]:
        """
        Retrieves all grades for a specific intern (The Report Card).
        """
        sql_query = """
        SELECT grade_id, intern_id, criteria_id, value, last_update
        FROM grades
        WHERE intern_id = ?
        ORDER BY criteria_id ASC
        """
        self.cursor.execute(sql_query, (intern_id,))
        results = self.cursor.fetchall()

        return [
            Grade(
                grade_id=row[0],
                intern_id=row[1],
                criteria_id=row[2],
                value=row[3],
                last_update=row[4],
            )
            for row in results
        ]

    def get_by_id(self, grade_id: int) -> Optional[Grade]:
        """
        Retrieves a grade by its unique database identifier.
        """
        sql_query = """
        SELECT grade_id, intern_id, criteria_id, value, last_update
        FROM grades
        WHERE grade_id = ?
        """
        self.cursor.execute(sql_query, (grade_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Grade(
            grade_id=row[0],
            intern_id=row[1],
            criteria_id=row[2],
            value=row[3],
            last_update=row[4],
        )

    def save(self, grade: Grade) -> int:
        """
        Persists a new Grade entity.
        Warning: Will raise IntegrityError if (intern_id, criteria_id) is duplicated.
        """
        if grade.grade_id is not None:
            raise ValueError(
                "Cannot save a grade that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO grades (intern_id, criteria_id, value)
        VALUES (?, ?, ?)
        """
        data = (grade.intern_id, grade.criteria_id, grade.value)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID for the new grade.")

        return self.cursor.lastrowid

    def update(self, grade: Grade) -> bool:
        """
        Updates an existing Grade record.
        """
        if grade.grade_id is None:
            raise ValueError("Cannot update a grade without an ID.")

        sql_query = """
        UPDATE grades SET
            value = ?,
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE grade_id = ?
        """

        data = (grade.value, grade.grade_id)

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, grade: Grade) -> bool:
        """
        Deletes a Grade record.
        """
        if grade.grade_id is None:
            raise ValueError("Cannot delete a grade without an ID.")

        sql_query = "DELETE FROM grades WHERE grade_id = ?"

        self.cursor.execute(sql_query, (grade.grade_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
