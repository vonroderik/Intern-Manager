from data.database import DatabaseConnector
from core.models.venue import Venue
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class VenueRepository:
    """
    Repository responsible for persistence and retrieval of Venue entities.

    This class implements the Repository pattern, abstracting all direct
    database access related to the `Venue` model. It uses a
    `DatabaseConnector` instance to interact with a SQLite database.

    Responsibilities:
        - Insert new venues into the database.
        - Retrieve venues using different query criteria.

    Notes:
        - This repository does not handle update or delete operations.
        - Database transactions for write operations are committed internally.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the VenueRepository with an active database connection.

        Args:
            db (DatabaseConnector): Database connector providing an open
                connection and cursor.
        """

        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def get_all(self) -> List[Venue]:
        """
        Retrieves all venues stored in the database.

        Returns:
            List[Venue]: A list of Venue objects. Returns an empty list
            if no records are found.
        """

        sql_query = """
SELECT venue_id, venue_name, address, supervisor_name, email, phone FROM venues 
ORDER BY name COLLATE NOCASE ASC
"""
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        venues = []

        for row in results:
            venue = Venue(
                venue_id=row[0],
                venue_name=row[1],
                venue_address=row[2],
                supervisor_name=row[3],
                supervisor_email=row[4],
                supervisor_phone=row[5],
            )

            venues.append(venue)

        return venues

    def get_by_id(self, venue_id: int) -> Optional[Venue]:
        """
        Retrieves a venue by its unique database identifier.

        Args:
            venue_id (int): Unique identifier of the venue.

        Returns:
            Optional[Venue]: The Venue object if found, or None otherwise.
        """

        sql_query = """
SELECT venue_id, venue_name, address, supervisor_name, email, phone FROM venues WHERE venue_id = ?
"""

        self.cursor.execute(sql_query, (venue_id,))

        row = self.cursor.fetchone()

        if row is None:
            return None

        venue = Venue(
            venue_id=row[0],
            venue_name=row[1],
            venue_address=row[2],
            supervisor_name=row[3],
            supervisor_email=row[4],
            supervisor_phone=row[5],
        )

        return venue

    def get_by_name(self, name: str) -> Optional[Venue]:
        """
        Retrieves the first venue whose name partially matches the given value.

        The search is case-sensitive and uses a SQL LIKE expression.
        If multiple venues match, only the first result is returned.

        Args:
            name (str): Partial or full name of the venue.

        Returns:
            Optional[Venue]: The first matching Venue object, or None
            if no match is found.
        """

        sql_query = """
SELECT venue_id, venue_name, address, supervisor_name, email, phone FROM venues WHERE venue_name LIKE ?
ORDER BY name COLLATE NOCASE ASC
"""

        self.cursor.execute(sql_query, (f"%{name}%",))

        row = self.cursor.fetchone()

        if row is None:
            return None

        venue = Venue(
            venue_id=row[0],
            venue_name=row[1],
            venue_address=row[2],
            supervisor_name=row[3],
            supervisor_email=row[4],
            supervisor_phone=row[5],
        )

        return venue

    def save(self, venue: Venue) -> Optional[int]:
        """
        Persists a new Venue entity in the database.

        The method inserts a new record into the `venues` table and commits
        the transaction. If the Venue already has an `venue_id`, the method
        assumes it is already persisted and aborts the operation.

        Args:
            venue (Venue): Venue entity to be persisted.

        Returns:
            Optional[int]: The generated database ID of the new venue,
            or None if the venue already has an ID.
        """

        if venue.venue_id is not None:
            return None

        sql_query = """
INSERT INTO venues (venue_name, address, supervisor_name, email, phone) 
VALUES (?, ?, ?, ?, ?)
"""
        data = (
            venue.venue_name,
            venue.venue_address,
            venue.supervisor_name,
            venue.supervisor_email,
            venue.supervisor_phone,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        return self.cursor.lastrowid

    def update(self, venue: Venue) -> bool:
        sql_query = """
UPDATE venues SET
venue_name = ?, address = ?, supervisor_name = ?, email = ?, 
    phone = ?, 
    last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
WHERE venue_id = ?
"""

        data = (
            venue.venue_name,
            venue.venue_address,
            venue.supervisor_name,
            venue.supervisor_email,
            venue.supervisor_phone,
            venue.venue_id,
        )

        try:
            self.cursor.execute(sql_query, data)
            self.conn.commit()

            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(
                f"Falha ao atualizar Local de Estágio '{venue.venue_name}' (ID: {venue.venue_id}). Erro: {e}"
            )
            return False

    def delete(self, venue: Venue) -> bool:
        if venue.venue_id is None:
            return False

        sql_query = """
DELETE FROM venues WHERE
venue_id = ?
"""

        data = venue.venue_id

        try:
            self.cursor.execute(sql_query, (data,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            logger.error(
                f"Falha ao deletar Local de Estágio '{venue.venue_name}' (ID: {venue.venue_id}). Erro: {e}"
            )
            return False
