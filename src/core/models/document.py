from typing import Optional


class Document:
    """
    Domain model representing a document associated with an intern.

    Each Document represents a required or optional document linked to
    a specific Intern. An intern may have multiple associated documents.

    This class mirrors the structure of the `documents` table in the database.

    Attributes:
        document_id (Optional[int]): Unique database identifier. None if the
            document has not yet been persisted.
        intern_id (int): Identifier of the intern to whom this document belongs.
        document_name (str): Name or description of the document.
        is_completed (int): Completion status of the document.
            Typically uses 0 (not completed) or 1 (completed).
    """

    def __init__(
        self,
        intern_id: int,
        document_name: str,
        is_completed: bool,
        last_update: Optional[str] = None,
        document_id: Optional[int] = None,
    ):
        """
        Initializes a Document instance.

        Args:
            intern_id (int): Identifier of the associated intern.
            document_name (str): Name or description of the document.
            is_completed (int): Completion status (0 = not completed, 1 = completed).
            document_id (Optional[int]): Database identifier. None if not persisted.
        """

        self.intern_id = intern_id
        self.document_name = document_name
        self.is_completed = is_completed
        self.last_update = last_update
        self.document_id = document_id

    def __repr__(self) -> str:
        return (
            f"Document("
            f"intern_id={self.intern_id}"
            f"document_name={self.document_name}"
            f"is_completed={self.is_completed}"
            f"last_update={self.last_update}"
            f"document_id={self.document_id}"
            f")"
        )
