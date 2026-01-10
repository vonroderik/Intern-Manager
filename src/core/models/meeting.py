from typing import Optional
from dataclasses import dataclass

@dataclass
class Meeting:
    """
    Domain model representing a supervisory meeting with an intern.

    This class mirrors the structure of the `meetings` table in the database.
    It tracks whether the intern was present and when the meeting occurred.

    Attributes:
        meeting_id (Optional[int]): Unique database identifier.
        intern_id (int): Identifier of the associated intern.
        meeting_date (str): Date of the meeting (ISO format preferred for DB).
        is_intern_present (int): 1 if present, 0 if absent.
    """

    intern_id: int
    meeting_date: str
    is_intern_present: bool
    meeting_id: Optional[int] = None

