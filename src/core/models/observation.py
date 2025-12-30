from typing import Optional


class Observation:
    """
    Domain model representing a observation associated with an intern.

    Each Observation stores a textual annotation linked to a specific Intern.
    An intern may have multiple observations, typically used for notes,
    observations, or administrative records.

    This class mirrors the structure of the `observations` table in the database.

    Attributes:
        observation_id (Optional[int]): Unique database identifier. None if the
            observation has not yet been persisted.
        intern_id (int): Identifier of the associated intern.
        observation (str): Textual content of the observation.
        last_update (Optional[str]): Date string representing the last modification.
    """

    def __init__(
        self,
        intern_id: int,
        observation: str,
        observation_id: Optional[int] = None,
        last_update: Optional[str] = None,
    ):
        """
        Initializes a Observation instance.

        Args:
            intern_id (int): Identifier of the associated intern.
            observation (str): Text content of the observation.
            observation_id (Optional[int]): Database identifier. None if not persisted.
            last_update (Optional[str]): Date/time of the last update.
        """

        self.intern_id = intern_id
        self.observation = observation
        self.observation_id = observation_id
        self.last_update = last_update

    def __repr__(self) -> str:
        return (
            f"Observation("
            f"intern_id={self.intern_id}"
            f"observation={self.observation}"
            f"observation={self.observation_id}"
            f"last_update={self.last_update}"
            f")"
        )
