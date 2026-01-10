from typing import Optional
from dataclasses import dataclass


@dataclass
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

    intern_id: int
    observation: str
    observation_id: Optional[int] = None
    last_update: Optional[str] = None
