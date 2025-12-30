from data.database import DatabaseConnector
from core.models.evaluation_criteria import EvaluationCriteria
from typing import Optional, List


class EvaluationCriteriaRepository:
    """
    Repository responsible for persistence and retrieval of EvaluationCriteria entities.
    """

    def __init__(self, db: DatabaseConnector):
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def get_all(self) -> List[EvaluationCriteria]:
        """
        Retrieves all evaluation criteria stored in the database.
        """
        sql_query = """
        SELECT criteria_id, name, description, weight
        FROM evaluation_criteria
        ORDER BY name ASC
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        return [
            EvaluationCriteria(
                criteria_id=row["criteria_id"],
                name=row["name"],
                description=row["description"],
                weight=row["weight"],
            )
            for row in results
        ]

    def get_by_id(self, criteria_id: int) -> Optional[EvaluationCriteria]:
        """
        Retrieves a criteria by its unique database identifier.
        """
        sql_query = """
        SELECT criteria_id, name, description, weight
        FROM evaluation_criteria
        WHERE criteria_id = ?
        """
        self.cursor.execute(sql_query, (criteria_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return EvaluationCriteria(
            criteria_id=row["criteria_id"],
            name=row["name"],
            description=row["description"],
            weight=row["weight"],
        )

    def save(self, criteria: EvaluationCriteria) -> int:
        """
        Persists a new EvaluationCriteria entity.
        """
        if criteria.criteria_id is not None:
            raise ValueError(
                "Cannot save a criteria that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO evaluation_criteria (name, description, weight)
        VALUES (?, ?, ?)
        """
        data = (criteria.name, criteria.description, criteria.weight)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError(
                "Database failed to generate an ID for the new criteria."
            )

        return self.cursor.lastrowid

    def update(self, criteria: EvaluationCriteria) -> bool:
        """
        Updates an existing EvaluationCriteria record.
        """
        if criteria.criteria_id is None:
            raise ValueError("Cannot update a criteria without an ID.")

        sql_query = """
        UPDATE evaluation_criteria SET
            name = ?, description = ?, weight = ?
        WHERE criteria_id = ?
        """
        data = (
            criteria.name,
            criteria.description,
            criteria.weight,
            criteria.criteria_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, criteria: EvaluationCriteria) -> bool:
        """
        Deletes a EvaluationCriteria record.
        """
        if criteria.criteria_id is None:
            raise ValueError("Cannot delete a criteria without an ID.")

        sql_query = "DELETE FROM evaluation_criteria WHERE criteria_id = ?"

        self.cursor.execute(sql_query, (criteria.criteria_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
