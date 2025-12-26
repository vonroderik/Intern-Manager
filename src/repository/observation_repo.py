# TODO - Change try-except for Raise (update, save, delete)

from data.database import DatabaseConnector
from core.models.observation import Observation
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class ObservationRepository:
    """
    Repository responsible for persistence and retrieval of Observation entities.

    This class implements the Repository pattern, encapsulating all direct
    database access related to the `Observation` domain model.

    It relies on a DatabaseConnector instance to manage the SQLite connection
    and cursor.

    Responsibilities:
        - Insert new obersvations.
        - Retrieve obersvations (all or by ID).
        - Update existing obersvations.
        - Delete obersvations.

    Notes:
        - All write operations commit transactions internally.
        - Business validation rules must be handled by the service layer.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the ObservationRepository with an active database connection.

        Args:
            db (DatabaseConnector): Database connector providing an open
                SQLite connection and cursor.
        """
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def get_all(self) -> List[Observation]:
        """
        Retrieves all obersvations stored in the database.

        Observations are returned ordered by the last update timestamp
        in descending order.

        Returns:
            List[OBservation]: A list of Observation objects. Returns an empty list
            if no records are found.
        """
        sql_query = """
        SELECT obersvation_id, intern_id, obersvation, last_update
        FROM obersvations
        ORDER BY last_update DESC
        """

        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        obersvations: List[Observation] = []

        for row in results:
            obersvations.append(
                Observation(
                    obersvation_id=row[0],
                    intern_id=row[1],
                    obersvation=row[2],
                    last_update=row[3],
                )
            )

        return obersvations

    def get_by_id(self, obersvation_id: int) -> Optional[Observation]:
        """
        Retrieves a obersvation by its unique database identifier.

        Args:
            obersvation_id (int): Unique identifier of the obersvation.

        Returns:
            Optional[Observation]: The Observation object if found, or None otherwise.
        """
        sql_query = """
        SELECT obersvation_id, intern_id, obersvation, last_update
        FROM obersvations
        WHERE obersvation_id = ?
        """

        self.cursor.execute(sql_query, (obersvation_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Observation(
            obersvation_id=row[0],
            intern_id=row[1],
            obersvation=row[2],
            last_update=row[3],
        )

    def save(self, obersvation: Observation) -> Optional[int]:
        """
        Persists a new Observtion entity in the database.

        If the Observation already has a `obersvation_id`, the method assumes it
        is already persisted and aborts the operation.

        Args:
            obersvation (Observation): Observation entity to be persisted.

        Returns:
            Optional[int]: The generated database ID of the new obersvation,
            or None if the obersvation already has an ID.
        """
        if obersvation.obersvation_id is not None:
            return None

        sql_query = """
        INSERT INTO obersvations (obersvation, intern_id)
        VALUES (?, ?)
        """

        data = (
            obersvation.obersvation,
            obersvation.intern_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        return self.cursor.lastrowid

    def update(self, obersvation: Observation) -> bool:
        """
        Updates an existing Observation record in the database.

        The method updates the obersvation text and refreshes the
        `last_update` timestamp using the local time.

        Args:
            obersvation (Observation): Observation entity with updated data.

        Returns:
            bool: True if the update affected at least one row,
            False otherwise.
        """
        if obersvation.obersvation_id is None:
            return False

        sql_query = """
        UPDATE obersvations SET
            obersvation = ?,
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE obersvation_id = ?
        """

        data = (
            obersvation.obersvation,
            obersvation.obersvation_id,
        )

        try:
            self.cursor.execute(sql_query, data)
            self.conn.commit()
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(
                f"Falha ao atualizar Comentário (ID: {obersvation.obersvation_id}). Erro: {e}"
            )
            return False

    def delete(self, obersvation: Observation) -> bool:
        """
        Deletes a Observation record from the database.

        Args:
            obersvation (Observation): Observation entity to be deleted.

        Returns:
            bool: True if the record was deleted, False otherwise.
        """
        if obersvation.obersvation_id is None:
            return False

        sql_query = """
        DELETE FROM obersvations
        WHERE obersvation_id = ?
        """

        try:
            self.cursor.execute(sql_query, (obersvation.obersvation_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(
                f"Falha ao deletar Comentário (ID: {obersvation.obersvation_id}). Erro: {e}"
            )
            return False
