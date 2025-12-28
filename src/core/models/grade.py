from typing import Optional


class Grade:
    """
    Domain model representing a grade assigned to an intern.

    Each Grade links a specific Intern to a specific EvaluationCriteria
    and stores the numerical value achieved. This is the intersection
    entity that effectively represents the student's report card.

    This class mirrors the structure of the `grades` table in the database.

    Attributes:
        grade_id (Optional[int]): Unique database identifier. None if the
            grade has not yet been persisted.
        intern_id (int): Identifier of the evaluated intern.
        criteria_id (int): Identifier of the evaluation criteria being applied.
        value (float): The numerical score achieved by the intern.
        last_update (Optional[str]): Timestamp of the last modification.
    """

    def __init__(
        self,
        intern_id: int,
        criteria_id: int,
        value: float,
        grade_id: Optional[int] = None,
        last_update: Optional[str] = None,
    ):
        """
        Initializes a Grade instance.

        Args:
            intern_id (int): Identifier of the associated intern.
            criteria_id (int): Identifier of the criteria being evaluated.
            value (float): The actual score/grade value (e.g., 9.5).
            grade_id (Optional[int]): Database identifier. None if not persisted.
            last_update (Optional[str]): ISO formatted timestamp of the last update.
        """
        self.intern_id = intern_id
        self.criteria_id = criteria_id
        self.value = value
        self.grade_id = grade_id
        self.last_update = last_update

    def __repr__(self) -> str:
        return (
            f"Grade("
            f"id={self.grade_id}, "
            f"intern_id={self.intern_id}, "
            f"criteria_id={self.criteria_id}, "
            f"value={self.value}, "
            f"last_update={self.last_update}"
            f")"
        )
