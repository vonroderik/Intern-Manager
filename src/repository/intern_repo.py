from data.database import DatabaseConnector
from core.models.intern import Intern
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class InternRepository:
    """
    Repository responsible for persistence and retrieval of Intern entities.

    This class implements the Repository pattern, abstracting all direct
    database access related to the `Intern` model. It uses a
    `DatabaseConnector` instance to interact with a SQLite database.

    Responsibilities:
        - Insert new interns into the database.
        - Retrieve interns using different query criteria.

    Notes:
        - This repository does not handle update or delete operations.
        - Database transactions for write operations are committed internally.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the InternRepository with an active database connection.

        Args:
            db (DatabaseConnector): Database connector providing an open
                connection and cursor.
        """

        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def save(self, intern: Intern) -> Optional[int]:
        """
        Persists a new Intern entity in the database.

        The method inserts a new record into the `interns` table and commits
        the transaction. If the Intern already has an `intern_id`, the method
        assumes it is already persisted and aborts the operation.

        Args:
            intern (Intern): Intern entity to be persisted.

        Returns:
            Optional[int]: The generated database ID of the new intern,
            or None if the intern already has an ID.
        """

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

    def get_all(self) -> List[Intern]:
        """
        Retrieves all interns stored in the database.

        Returns:
            List[Intern]: A list of Intern objects. Returns an empty list
            if no records are found.
        """

        sql_query = """
SELECT intern_id, name, registration_number, term, email, start_date, end_date, 
working_days, working_hours, venue_id FROM interns
"""
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        interns = []

        for row in results:
            intern = Intern(
                intern_id=row[0],
                name=row[1],
                registration_number=row[2],
                term=row[3],
                email=row[4],
                start_date=row[5],
                end_date=row[6],
                working_days=row[7],
                working_hours=row[8],
                venue_id=row[9],
            )

            interns.append(intern)

        return interns

    def get_by_id(self, intern_id: int) -> Optional[Intern]:
        """
        Retrieves an intern by its unique database identifier.

        Args:
            intern_id (int): Unique identifier of the intern.

        Returns:
            Optional[Intern]: The Intern object if found, or None otherwise.
        """

        sql_query = """
SELECT intern_id, name, registration_number, term, email, start_date, end_date, 
working_days, working_hours, venue_id FROM interns WHERE intern_id = ?
"""

        self.cursor.execute(sql_query, (intern_id,))

        row = self.cursor.fetchone()

        if row is None:
            return None

        intern = Intern(
            intern_id=row[0],
            name=row[1],
            registration_number=row[2],
            term=row[3],
            email=row[4],
            start_date=row[5],
            end_date=row[6],
            working_days=row[7],
            working_hours=row[8],
            venue_id=row[9],
        )

        return intern

    def get_by_registration_number(self, registration_number: int) -> Optional[Intern]:
        """
        Retrieves an intern by registration number.

        Args:
            registration_number (int): Registration number associated
                with the intern.

        Returns:
            Optional[Intern]: The Intern object if found, or None otherwise.
        """

        sql_query = """
SELECT intern_id, name, registration_number, term, email, start_date, end_date, 
working_days, working_hours, venue_id FROM interns WHERE registration_number = ?
"""

        self.cursor.execute(sql_query, (registration_number,))

        row = self.cursor.fetchone()

        if row is None:
            return None

        intern = Intern(
            intern_id=row[0],
            name=row[1],
            registration_number=row[2],
            term=row[3],
            email=row[4],
            start_date=row[5],
            end_date=row[6],
            working_days=row[7],
            working_hours=row[8],
            venue_id=row[9],
        )

        return intern

    def get_by_name(self, name: str) -> Optional[Intern]:
        """
        Retrieves the first intern whose name partially matches the given value.

        The search is case-sensitive and uses a SQL LIKE expression.
        If multiple interns match, only the first result is returned.

        Args:
            name (str): Partial or full name of the intern.

        Returns:
            Optional[Intern]: The first matching Intern object, or None
            if no match is found.
        """

        sql_query = """
SELECT intern_id, name, registration_number, term, email, start_date, end_date, 
working_days, working_hours, venue_id FROM interns WHERE name LIKE ?
LIMIT 1
"""

        self.cursor.execute(sql_query, (f"%{name}%",))

        row = self.cursor.fetchone()

        if row is None:
            return None

        intern = Intern(
            intern_id=row[0],
            name=row[1],
            registration_number=row[2],
            term=row[3],
            email=row[4],
            start_date=row[5],
            end_date=row[6],
            working_days=row[7],
            working_hours=row[8],
            venue_id=row[9],
        )

        return intern

    def update(self, intern: Intern) -> bool:
        sql_query = """
UPDATE interns SET
name = ?, registration_number = ?, term = ?, email = ?, 
    start_date = ?, end_date = ?, working_days = ?, working_hours = ?, 
    venue_id = ?, 
    last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
WHERE intern_id = ?
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
            intern.intern_id,
        )
        try:
            self.cursor.execute(sql_query, data)
            self.conn.commit()

            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(
                f"Falha ao atualizar estagiário '{intern.name}' (ID: {intern.intern_id}). Erro: {e}"
            )
            return False

    def delete(self, intern: Intern) -> bool:
        if intern.intern_id is None:
            return False

        sql_query = """
DELETE FROM interns WHERE
intern_id = ?
"""

        data = intern.intern_id

        try:
            self.cursor.execute(sql_query, (data,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            logger.error(
                f"Falha ao deletar estagiário '{intern.name}' (ID: {intern.intern_id}). Erro: {e}"
            )
            return False
