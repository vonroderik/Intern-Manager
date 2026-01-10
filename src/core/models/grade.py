from typing import Optional
from dataclasses import dataclass


@dataclass
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

    intern_id: int
    criteria_id: int
    value: float
    grade_id: Optional[int] = None
    last_update: Optional[str] = None
