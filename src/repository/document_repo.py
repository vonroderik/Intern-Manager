from sqlite3 import Connection, Cursor
from data.database import DatabaseConnector
from core.models.document import Document
from typing import List, Optional


class DocumentRepository:
    """
    Repository responsible for persistence and retrieval of Document entities.

    This class encapsulates all SQL queries related to the `documents` table,
    providing an abstraction layer over raw database operations.

    Attributes:
        db (DatabaseConnector): The database connector instance.
        conn (Connection): Active SQLite connection.
        cursor (Cursor): Active SQLite cursor.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the repository with an active database connection.

        Args:
            db (DatabaseConnector): An initialized connector with an open connection.

        Raises:
            RuntimeError: If the connector does not hold a valid connection or cursor.
        """
        self.db = db

        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )

        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

    def get_by_intern_id(self, intern_id: int) -> List[Document]:
        """
        Retrieves all documents associated with a specific intern.

        Args:
            intern_id (int): The unique identifier of the intern.

        Returns:
            List[Document]: A list of Document objects. Returns an empty list
            if no documents are found.
        """
        sql_query = """
        SELECT document_id, intern_id, name, is_completed
        FROM documents
        WHERE intern_id = ?
        """
        self.cursor.execute(sql_query, (intern_id,))
        results = self.cursor.fetchall()

        return [
            Document(
                document_id=row["document_id"],
                intern_id=row["intern_id"],
                document_name=row["name"],
                is_completed=bool(row["is_completed"]),
            )
            for row in results
        ]

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """
        Retrieves a single document by its unique database ID.

        Args:
            document_id (int): The unique identifier of the document.

        Returns:
            Optional[Document]: The Document object if found, otherwise None.
        """
        sql_query = """
        SELECT document_id, intern_id, name, is_completed
        FROM documents
        WHERE document_id = ?
        """
        self.cursor.execute(sql_query, (document_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Document(
            document_id=row["document_id"],
            intern_id=row["intern_id"],
            document_name=row["name"],
            is_completed=bool(row["is_completed"]),
        )

    def save(self, document: Document) -> int:
        """
        Persists a new document into the database.

        Args:
            document (Document): The document entity to save. Must not have an ID yet.

        Returns:
            int: The unique identifier (primary key) of the newly created record.

        Raises:
            ValueError: If the document object already has an assigned ID.
            RuntimeError: If the database fails to return the last row ID.
        """
        if document.document_id is not None:
            raise ValueError("Cannot save a document that already has an ID.")

        sql_query = """
        INSERT INTO documents (intern_id, name, is_completed)
        VALUES (?, ?, ?)
        """
        data = (document.intern_id, document.document_name, document.is_completed)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID.")

        return self.cursor.lastrowid

    def update(self, document: Document) -> bool:
        """
        Updates an existing document's name and completion status.

        Args:
            document (Document): The document entity with updated data. Must have an ID.

        Returns:
            bool: True if the update was successful (row modified), False otherwise.

        Raises:
            ValueError: If the document object does not have an ID.
        """
        if document.document_id is None:
            raise ValueError("Cannot update a document without an ID.")

        sql_query = """
        UPDATE documents SET
            name = ?,
            is_completed = ?
        WHERE document_id = ?
        """
        data = (document.document_name, document.is_completed, document.document_id)

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, document: Document) -> bool:
        """
        Permanently removes a document from the database.

        Args:
            document (Document): The document entity to remove. Must have an ID.

        Returns:
            bool: True if the deletion was successful, False otherwise.

        Raises:
            ValueError: If the document object does not have an ID.
        """
        if document.document_id is None:
            raise ValueError("Cannot delete a document without an ID.")

        sql_query = "DELETE FROM documents WHERE document_id = ?"

        self.cursor.execute(sql_query, (document.document_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def create_batch(self, documents: List[Document]):
        """
        Persists a list of documents in a single transaction (Bulk Insert).

        Uses `executemany` for performance optimization. If any insertion fails,
        the entire transaction is rolled back.

        Args:
            documents (List[Document]): List of Document entities to be saved.

        Raises:
            Exception: Propagates any database error after performing a rollback.
        """
        query = "INSERT INTO documents (intern_id, name, is_completed) VALUES (?, ?, ?)"

        data = [
            (doc.intern_id, doc.document_name, doc.is_completed) for doc in documents
        ]

        try:
            self.cursor.executemany(query, data)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
