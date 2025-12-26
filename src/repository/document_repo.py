from data.database import DatabaseConnector
from core.models.document import Document
from typing import Optional, List


class DocumentRepository:
    """
    Repository responsible for persistence and retrieval of Document entities.
    """

    def __init__(self, db: DatabaseConnector):
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def get_all(self) -> List[Document]:
        """
        Retrieves all documents stored in the database.
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
                    is_completed=bool(row[3]),
                    last_update=row[4],
                )
            )

        return documents

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """
        Retrieves a document by its unique database identifier.
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
            is_completed=bool(row[3]),
            last_update=row[4],
        )

    def save(self, document: Document) -> Optional[int]:
        """
        Persists a new Document entity in the database.
        """
        if document.document_id is not None:
            raise ValueError(
                "Cannot save a document that already has an ID. Use update instead."
            )

        sql_query = """
        INSERT INTO documents (document_name, intern_id, is_completed)
        VALUES (?, ?, ?)
        """

        val_completed = 1 if document.is_completed else 0

        data = (document.document_name, document.intern_id, val_completed)

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError(
                "Database failed to generate an ID for the new document."
            )

        return self.cursor.lastrowid

    def update(self, document: Document) -> bool:
        """
        Updates an existing Document record in the database.
        """
        if document.document_id is None:
            raise ValueError("Cannot update a document without an ID.")

        val_completed = 1 if document.is_completed else 0

        sql_query = """
        UPDATE documents SET
            document_name = ?, is_completed = ?,
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE document_id = ?
        """

        data = (document.document_name, val_completed, document.document_id)

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete(self, document: Document) -> bool:
        """
        Deletes a Document record from the database.
        """
        if document.document_id is None:
            raise ValueError("Cannot delete a document without an ID.")

        sql_query = """
        DELETE FROM documents
        WHERE document_id = ?
        """

        self.cursor.execute(sql_query, (document.document_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
