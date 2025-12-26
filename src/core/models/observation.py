from typing import Optional


class Observation:
    """
    Domain model representing a obersvation associated with an intern.

    Each Obersvation stores a textual annotation linked to a specific Intern.
    An intern may have multiple obersvations, typically used for notes,
    observations, or administrative records.

    This class mirrors the structure of the `obersvations` table in the database.

    Attributes:
        obersvation_id (Optional[int]): Unique database identifier. None if the
            obersvation has not yet been persisted.
        intern_id (int): Identifier of the associated intern.
        obersvation (str): Textual content of the obersvation.
    """

    def __init__(
        self,
        intern_id: int,
        obersvation: str,
        obersvation_id: Optional[int] = None,
        last_update: Optional[str] = None,
    ):
        """
        Initializes a Obersvation instance.

        Args:
            intern_id (int): Identifier of the associated intern.
            obersvation (str): Text content of the obersvation.
            obersvation_id (Optional[int]): Database identifier. None if not persisted.
        """

        self.intern_id = intern_id
        self.obersvation = obersvation
        self.obersvation_id = obersvation_id
        self.last_update = last_update

    def __repr__(self) -> str:
        return (
            f"Obersvation("
            f"intern_id={self.intern_id}"
            f"obersvation={self.obersvation}"
            f"obersvation_id={self.obersvation_id}"
            f"last_update={self.last_update}"
            f")"
        )
