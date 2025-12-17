from typing import Optional


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

    def __init__(
        self,
        intern_id: int,
        meeting_date: str,
        is_intern_present: bool,
        meeting_id: Optional[int] = None,
    ):
        """
        Initializes a Meeting instance.

        Args:
            intern_id (int): Identifier of the associated intern.
            meeting_date (str): Date of the meeting.
            is_intern_present (bool): True if intern was present, False otherwise.
            meeting_id (Optional[int]): Database identifier. None if not persisted.
        """
        self.intern_id = intern_id
        self.meeting_date = meeting_date
        self.is_intern_present = 1 if is_intern_present else 0
        self.meeting_id = meeting_id

    def __repr__(self) -> str:
        return (
            f"Meeting("
            f"id={self.meeting_id}, "
            f"intern_id={self.intern_id}, "
            f"date='{self.meeting_date}', "
            f"present={self.is_intern_present}"
            f")"
        )
