from data.database import DatabaseConnector
from core.models.document import Document
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class DocumentRepository:
    """
    Repository responsible for persistence and retrieval of Document entities.

    This class implements the Repository pattern, encapsulating all direct
    database access related to the `Document` domain model.

    It relies on a DatabaseConnector instance to manage the SQLite connection
    and cursor.

    Responsibilities:
        - Insert new documents.
        - Retrieve documents (all or by ID).
        - Update existing document status or names.
        - Delete documents.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the DocumentRepository with an active database connection.

        Args:
            db (DatabaseConnector): Database connector providing an open
                SQLite connection and cursor.
        """
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def get_all(self) -> List[Document]:
        """
        Retrieves all documents stored in the database.

        Documents are returned ordered by the last update timestamp
        in descending order.

        Returns:
            List[Document]: A list of Document objects. Returns an empty list
            if no records are found.
        """

        sql_query = """
        SELECT document_id, intern_id, document_name, is_completed, last_update
        FROM documents
        ORDER BY last_update DESC
        """

        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        documents: List[Document] = []

        for row in results:
            documents.append(
                Document(
                    document_id=row[0],
                    intern_id=row[1],
                    document_name=row[2],
                    is_completed=row[3],
                    last_update=row[4],
                )
            )

        return documents

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """
        Retrieves a document by its unique database identifier.

        Args:
            document_id (int): Unique identifier of the document.

        Returns:
            Optional[Document]: The Document object if found, or None otherwise.
        """

        sql_query = """
        SELECT document_id, intern_id, document_name, is_completed, last_update
        FROM documents
        WHERE document_id = ?
        """

        self.cursor.execute(sql_query, (document_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Document(
            document_id=row[0],
            intern_id=row[1],
            document_name=row[2],
            is_completed=row[3],
            last_update=row[4],
        )

    def save(self, document: Document) -> Optional[int]:
        """
        Persists a new Document entity in the database.

        Args:
            document (Document): Document entity to be persisted.

        Returns:
            Optional[int]: The generated database ID of the new document,
            or None if the document already has an ID.
        """

        if document.document_id is not None:
            return None

        sql_query = """
        INSERT INTO documents (document_name, intern_id)
        VALUES (?, ?)
        """

        data = (
            document.document_name,
            document.intern_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        return self.cursor.lastrowid

    def update(self, document: Document) -> bool:
        """
        Updates an existing Document record in the database.

        The method updates the document text and refreshes the
        `last_update` timestamp using the local time.

        Args:
            document (Document): document entity with updated data.

        Returns:
            bool: True if the update affected at least one row,
            False otherwise.
        """
        if document.document_id is None:
            return False

        sql_query = """
        UPDATE documents SET
            document_name = ?, is_completed = ?,
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE document_id = ?
        """

        data = (document.document_name, document.is_completed, document.document_id)

        try:
            self.cursor.execute(sql_query, data)
            self.conn.commit()
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(
                f"Falha ao atualizar Documento (ID: {document.document_id}). Erro: {e}"
            )
            return False

    def delete(self, document: Document) -> bool:
        """
        Deletes a Document record from the database.

        Args:
            document (Document): Document entity to be deleted.

        Returns:
            bool: True if the record was deleted, False otherwise.
        """
        if document.document_id is None:
            return False

        sql_query = """
        DELETE FROM documents
        WHERE document_id = ?
        """

        try:
            self.cursor.execute(sql_query, (document.document_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(
                f"Falha ao deletar Comentário (ID: {document.document_id}). Erro: {e}"
            )
            return False
