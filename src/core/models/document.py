from typing import Optional
from dataclasses import dataclass


@dataclass
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
        status (Optional[str]): Completion status of the document.
        feedback Optional[str]: Feedback provided to the intern.
    """

    intern_id: int
    document_name: str
    status: Optional[str] = None
    feedback: Optional[str] = None
    last_update: Optional[str] = None
    document_id: Optional[int] = None
