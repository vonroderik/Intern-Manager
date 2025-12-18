from data.database import DatabaseConnector
from core.models.venue import Venue
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class VenueRepository:
    """
    Repository responsible for persistence and retrieval of Venue entities.

    This class implements the Repository pattern, encapsulating all direct
    database access related to the `Venue` domain model.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the VenueRepository with an active database connection.

        Args:
            db (DatabaseConnector): Database connector providing an open
                SQLite connection and cursor.
        """
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def get_all(self) -> List[Venue]:
        """
        Retrieves all venues stored in the database.

        Returns:
            List[Venue]: A list of Venue objects ordered by name.
        """
        # ✅ Correção: mudado de 'name' para 'venue_name'
        sql_query = """
        SELECT venue_id, venue_name, address, supervisor_name, supervisor_email, supervisor_phone 
        FROM venues 
        ORDER BY venue_name COLLATE NOCASE ASC
        """
        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        venues = []
        for row in results:
            venues.append(
                Venue(
                    venue_id=row[0],
                    venue_name=row[1],
                    venue_address=row[2],
                    supervisor_name=row[3],
                    supervisor_email=row[4],
                    supervisor_phone=row[5],
                )
            )
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
        SELECT venue_id, venue_name, address, supervisor_name, supervisor_email, supervisor_phone 
        FROM venues WHERE venue_id = ?
        """
        self.cursor.execute(sql_query, (venue_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Venue(
            venue_id=row[0],
            venue_name=row[1],
            venue_address=row[2],
            supervisor_name=row[3],
            supervisor_email=row[4],
            supervisor_phone=row[5],
        )

    def get_by_name(self, name: str) -> Optional[Venue]:
        """
        Retrieves the first venue whose name partially matches the given value.

        Args:
            name (str): Partial or full name of the venue.

        Returns:
            Optional[Venue]: The first matching Venue object, or None.
        """
        # ✅ Correção: mudado de 'name' para 'venue_name' no ORDER BY
        sql_query = """
        SELECT venue_id, venue_name, address, supervisor_name, supervisor_email, supervisor_phone 
        FROM venues WHERE venue_name LIKE ?
        ORDER BY venue_name COLLATE NOCASE ASC
        """
        self.cursor.execute(sql_query, (f"%{name}%",))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Venue(
            venue_id=row[0],
            venue_name=row[1],
            venue_address=row[2],
            supervisor_name=row[3],
            supervisor_email=row[4],
            supervisor_phone=row[5],
        )

    def save(self, venue: Venue) -> Optional[int]:
        """
        Persists a new Venue entity in the database.

        Args:
            venue (Venue): Venue entity to be persisted.

        Returns:
            Optional[int]: The generated database ID, or None if it already has one.
        """
        if venue.venue_id is not None:
            return None

        sql_query = """
        INSERT INTO venues (venue_name, address, supervisor_name, supervisor_email, supervisor_phone) 
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
        """
        Updates an existing Venue record.

        Args:
            venue (Venue): Venue entity with updated data.

        Returns:
            bool: True if the update was successful.
        """
        sql_query = """
        UPDATE venues SET
            venue_name = ?, address = ?, supervisor_name = ?, supervisor_email = ?, 
            supervisor_phone = ?, 
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
            logger.error(f"Erro ao atualizar Venue {venue.venue_id}: {e}")
            return False

    def delete(self, venue: Venue) -> bool:
        """
        Deletes a Venue record.

        Args:
            venue (Venue): Venue entity to be deleted.

        Returns:
            bool: True if the record was deleted.
        """
        if venue.venue_id is None:
            return False

        sql_query = "DELETE FROM venues WHERE venue_id = ?"
        try:
            self.cursor.execute(sql_query, (venue.venue_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Erro ao deletar Venue {venue.venue_id}: {e}")
            return False
