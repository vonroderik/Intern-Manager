from typing import Optional


class Comment:
    """
    Domain model representing a comment associated with an intern.

    Each Comment stores a textual annotation linked to a specific Intern.
    An intern may have multiple comments, typically used for notes,
    observations, or administrative records.

    This class mirrors the structure of the `comments` table in the database.

    Attributes:
        comment_id (Optional[int]): Unique database identifier. None if the
            comment has not yet been persisted.
        intern_id (int): Identifier of the associated intern.
        comment (str): Textual content of the comment.
    """

    def __init__(
        self,
        intern_id: int,
        meeting_date: str,
        meeting_id,
        is_intern_present: Optional[int] = None,
    ):
        """
        Initializes a Comment instance.

        Args:
            intern_id (int): Identifier of the associated intern.
            comment (str): Text content of the comment.
            comment_id (Optional[int]): Database identifier. None if not persisted.
        """

        self.intern_id = intern_id
        self.meeting_date = meeting_date
        self.meeting_id = meeting_id
        self.is_intern_present = is_intern_present

    def __repr__(self) -> str:
        return (
            f"Comment("
            f"intern_id={self.intern_id}"
            f"meeting_date={self.meeting_date}"
            f"meeting_id={self.meeting_id}"
            f"is_intern_present={self.is_intern_present}"
            f")"
        )
