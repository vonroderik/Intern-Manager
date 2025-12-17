from data.database import DatabaseConnector
from core.models.comment import Comment
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class CommentRepository:
    """
    Repository responsible for persistence and retrieval of Comment entities.

    This class implements the Repository pattern, encapsulating all direct
    database access related to the `Comment` domain model.

    It relies on a DatabaseConnector instance to manage the SQLite connection
    and cursor.

    Responsibilities:
        - Insert new comments.
        - Retrieve comments (all or by ID).
        - Update existing comments.
        - Delete comments.

    Notes:
        - All write operations commit transactions internally.
        - Business validation rules must be handled by the service layer.
    """

    def __init__(self, db: DatabaseConnector):
        """
        Initializes the CommentRepository with an active database connection.

        Args:
            db (DatabaseConnector): Database connector providing an open
                SQLite connection and cursor.
        """
        self.db = db
        self.conn = db.conn
        self.cursor = db.cursor

    def get_all(self) -> List[Comment]:
        """
        Retrieves all comments stored in the database.

        Comments are returned ordered by the last update timestamp
        in descending order.

        Returns:
            List[Comment]: A list of Comment objects. Returns an empty list
            if no records are found.
        """
        sql_query = """
        SELECT comment_id, intern_id, comment, last_update
        FROM comments
        ORDER BY last_update DESC
        """

        self.cursor.execute(sql_query)
        results = self.cursor.fetchall()

        comments: List[Comment] = []

        for row in results:
            comments.append(
                Comment(
                    comment_id=row[0],
                    intern_id=row[1],
                    comment=row[2],
                    last_update=row[3],
                )
            )

        return comments

    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """
        Retrieves a comment by its unique database identifier.

        Args:
            comment_id (int): Unique identifier of the comment.

        Returns:
            Optional[Comment]: The Comment object if found, or None otherwise.
        """
        sql_query = """
        SELECT comment_id, intern_id, comment, last_update
        FROM comments
        WHERE comment_id = ?
        """

        self.cursor.execute(sql_query, (comment_id,))
        row = self.cursor.fetchone()

        if row is None:
            return None

        return Comment(
            comment_id=row[0],
            intern_id=row[1],
            comment=row[2],
            last_update=row[3],
        )

    def save(self, comment: Comment) -> Optional[int]:
        """
        Persists a new Comment entity in the database.

        If the Comment already has a `comment_id`, the method assumes it
        is already persisted and aborts the operation.

        Args:
            comment (Comment): Comment entity to be persisted.

        Returns:
            Optional[int]: The generated database ID of the new comment,
            or None if the comment already has an ID.
        """
        if comment.comment_id is not None:
            return None

        sql_query = """
        INSERT INTO comments (comment, intern_id)
        VALUES (?, ?)
        """

        data = (
            comment.comment,
            comment.intern_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        return self.cursor.lastrowid

    def update(self, comment: Comment) -> bool:
        """
        Updates an existing Comment record in the database.

        The method updates the comment text and refreshes the
        `last_update` timestamp using the local time.

        Args:
            comment (Comment): Comment entity with updated data.

        Returns:
            bool: True if the update affected at least one row,
            False otherwise.
        """
        if comment.comment_id is None:
            return False

        sql_query = """
        UPDATE comments SET
            comment = ?,
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE comment_id = ?
        """

        data = (
            comment.comment,
            comment.comment_id,
        )

        try:
            self.cursor.execute(sql_query, data)
            self.conn.commit()
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(
                f"Falha ao atualizar Comentário (ID: {comment.comment_id}). Erro: {e}"
            )
            return False

    def delete(self, comment: Comment) -> bool:
        """
        Deletes a Comment record from the database.

        Args:
            comment (Comment): Comment entity to be deleted.

        Returns:
            bool: True if the record was deleted, False otherwise.
        """
        if comment.comment_id is None:
            return False

        sql_query = """
        DELETE FROM comments
        WHERE comment_id = ?
        """

        try:
            self.cursor.execute(sql_query, (comment.comment_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(
                f"Falha ao deletar Comentário (ID: {comment.comment_id}). Erro: {e}"
            )
            return False
