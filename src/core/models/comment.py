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
        comment: str,
        comment_id: Optional[int] = None,
        last_update: Optional[str] = None,
    ):
        """
        Initializes a Comment instance.

        Args:
            intern_id (int): Identifier of the associated intern.
            comment (str): Text content of the comment.
            comment_id (Optional[int]): Database identifier. None if not persisted.
        """

        self.intern_id = intern_id
        self.comment = comment
        self.comment_id = comment_id
        self.last_update = last_update

    def __repr__(self) -> str:
        return (
            f"Comment("
            f"intern_id={self.intern_id}"
            f"comment={self.comment}"
            f"comment_id={self.comment_id}"
            f"last_update={self.last_update}"
            f")"
        )
