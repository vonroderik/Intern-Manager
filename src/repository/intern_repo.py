from data.database import DatabaseConnector
from core.models.intern import Intern
from typing import Optional, List
from sqlite3 import Connection, Cursor


class InternRepository:
    """
    Repository responsible for persistence and retrieval of Intern entities.

    This class implements the Repository pattern, abstracting all direct
    database access related to the `Intern` model. It uses a
    `DatabaseConnector` instance to interact with a SQLite database.

    Responsibilities:
        - Insert new interns into the database.
        - Retrieve interns using different query criteria (ID, RA, Name).
        - Update existing intern records.
        - Delete intern records.

    Attributes:
        db (DatabaseConnector): The database connector instance.
        conn (Connection): Active SQLite connection.
        cursor (Cursor): Active SQLite cursor.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the InternRepository with an active database connection.

        Args:
            db (DatabaseConnector): Database connector providing an open
                connection and cursor.

        Raises:
            RuntimeError: If the connector does not hold a valid connection.
        """
        self.db = db
        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )
        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

    def get_all(self) -> List[Intern]:
        """
        Retrieves all interns stored in the database.

        Returns:
            List[Intern]: A list of Intern objects ordered alphabetically by name.
        """
        sql_query = """
        SELECT intern_id, name, registration_number, term, email, start_date, end_date, 
        working_days, working_hours, venue_id FROM interns ORDER BY name COLLATE NOCASE ASC
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        interns = []
        for row in results:
            interns.append(
                Intern(
                    intern_id=row["intern_id"],
                    name=row["name"],
                    registration_number=row["registration_number"],
                    term=row["term"],
                    email=row["email"],
                    start_date=row["start_date"],
                    end_date=row["end_date"],
                    working_days=row["working_days"],
                    working_hours=row["working_hours"],
                    venue_id=row["venue_id"],
                )
            )
        return interns

    def get_by_id(self, intern_id: int) -> Optional[Intern]:
        """
        Retrieves a single intern by its unique database identifier.

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

        return Intern(
            intern_id=row["intern_id"],
            name=row["name"],
            registration_number=row["registration_number"],
            term=row["term"],
            email=row["email"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            working_days=row["working_days"],
            working_hours=row["working_hours"],
            venue_id=row["venue_id"],
        )

    def get_by_registration_number(self, registration_number: str) -> Optional[Intern]:
        """
        Retrieves an intern by their academic registration number (RA).

        Args:
            registration_number (str): Registration number of the intern.

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

        return Intern(
            intern_id=row["intern_id"],
            name=row["name"],
            registration_number=row["registration_number"],
            term=row["term"],
            email=row["email"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            working_days=row["working_days"],
            working_hours=row["working_hours"],
            venue_id=row["venue_id"],
        )

    def get_by_name(self, name: str) -> Optional[Intern]:
        """
        Retrieves the first intern whose name partially matches the given query.

        Note: This method returns only the first match found.

        Args:
            name (str): Partial or full name of the intern.

        Returns:
            Optional[Intern]: The first matching Intern object, or None.
        """
        sql_query = """
        SELECT intern_id, name, registration_number, term, email, start_date, end_date, 
        working_days, working_hours, venue_id FROM interns WHERE name LIKE ?
        ORDER BY name COLLATE NOCASE ASC
        """
        self.cursor.execute(sql_query, (f"%{name}%",))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Intern(
            intern_id=row["intern_id"],
            name=row["name"],
            registration_number=row["registration_number"],
            term=row["term"],
            email=row["email"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            working_days=row["working_days"],
            working_hours=row["working_hours"],
            venue_id=row["venue_id"],
        )

    def save(self, intern: Intern) -> Optional[int]:
        """
        Persists a new Intern entity in the database.

        Args:
            intern (Intern): Intern entity to be persisted. Must not have an ID.

        Returns:
            Optional[int]: The generated database ID.

        Raises:
            ValueError: If the intern object already has an ID.
            RuntimeError: If the database fails to return the new ID.
        """
        if intern.intern_id is not None:
            raise ValueError(
                "Cannot save a intern that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO interns (
        name, registration_number, term, email, start_date, end_date, 
        working_days, working_hours, venue_id) 
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
        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID for the new intern.")
        return self.cursor.lastrowid

    def update(self, intern: Intern) -> bool:
        """
        Updates an existing Intern record.

        Also automatically updates the `last_update` timestamp field.

        Args:
            intern (Intern): Intern entity with updated data. Must have an ID.

        Returns:
            bool: True if the update affected at least one row, False otherwise.

        Raises:
            ValueError: If the intern object does not have an ID.
        """

        if intern.intern_id is None:
            raise ValueError("Cannot update an intern without an ID.")

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

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, intern: Intern) -> bool:
        """
        Permanently deletes an Intern record.

        Args:
            intern (Intern): Intern entity to be deleted. Must have an ID.

        Returns:
            bool: True if the record was successfully deleted.

        Raises:
            ValueError: If the intern object does not have an ID.
        """
        if intern.intern_id is None:
            raise ValueError("Cannot delete an intern without an ID.")

        sql_query = "DELETE FROM interns WHERE intern_id = ?"

        self.cursor.execute(sql_query, (intern.intern_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
