from data.database import DatabaseConnector
from core.models.observation import Observation
from typing import Optional, List


class ObservationRepository:
    """
    Repository responsible for persistence and retrieval of Observation entities.
    """

    def __init__(self, db: DatabaseConnector):
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def get_all(self) -> List[Observation]:
        """
        Retrieves all observations stored in the database.
        """
        sql_query = """
        SELECT observation_id, intern_id, observation, last_update
        FROM observations
        ORDER BY last_update DESC
        """

        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        observations: List[Observation] = []

        for row in results:
            observations.append(
                Observation(
                    observation_id=row["observation_id"],
                    intern_id=row["intern_id"],
                    observation=row["observation"],
                    last_update=row["last_update"],
                )
            )

        return observations

    def get_by_id(self, observation_id: int) -> Optional[Observation]:
        """
        Retrieves a observation by its unique database identifier.
        """
        # CORREÇÃO: Nome da tabela padronizado para 'observations' (plural)
        sql_query = """
        SELECT observation_id, intern_id, observation, last_update
        FROM observations 
        WHERE observation_id = ?
        """

        self.cursor.execute(sql_query, (observation_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Observation(
            observation_id=row["observation_id"],
            intern_id=row["intern_id"],
            observation=row["observation"],
            last_update=row["last_update"],
        )

    def save(self, observation: Observation) -> int:
        """
        Persists a new Observation entity in the database.
        """
        # CORREÇÃO LÓGICA: Se JÁ TEM ID, não podemos salvar (deveria ser update).
        if observation.observation_id is not None:
            raise ValueError(
                "Cannot save an observation that already has an ID. Use update instead."
            )

        # CORREÇÃO: Nome da tabela 'observations'
        sql_query = """
        INSERT INTO observations (observation, intern_id)
        VALUES (?, ?)
        """

        data = (
            observation.observation,
            observation.intern_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError(
                "Database failed to generate an ID for the new observation."
            )

        return self.cursor.lastrowid

    def update(self, observation: Observation) -> bool:
        """
        Updates an existing Observation record in the database.
        """
        # CORREÇÃO LÓGICA: Aqui sim, se NÃO TEM ID, erro.
        if observation.observation_id is None:
            raise ValueError("Cannot update an observation without an ID.")

        sql_query = """
        UPDATE observations SET
            observation = ?,
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE observation_id = ?
        """

        data = (
            observation.observation,
            observation.observation_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, observation: Observation) -> bool:
        """
        Deletes a Observation record from the database.
        """
        if observation.observation_id is None:
            raise ValueError("Cannot delete an observation without an ID.")

        sql_query = """
        DELETE FROM observations
        WHERE observation_id = ?
        """

        self.cursor.execute(sql_query, (observation.observation_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
