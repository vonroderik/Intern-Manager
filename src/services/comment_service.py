from services.base_service import BaseService
from core.models.comment import Comment
from repository.comment_repo import CommentRepository

REQUIRED_FIELDS = {
    "comment": "Comentário",
    "intern_id": "ID do Estagiário",
}


class CommentService(BaseService[Comment]):
    """
    Service class responsible for business logic related to intern comments.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: CommentRepository):
        """
        Initializes the CommentService with the specified repository.

        Args:
            repo (CommentRepository): Repository for comment persistence.
        """
        super().__init__(repo)

    def add_new_comment(self, comment: Comment):
        """
        Validates and adds a new comment to the system.

        Args:
            comment (Comment): The comment instance to be added.

        Returns:
            int: The ID of the newly created comment.
        """
        self._validate_required_fields(comment)
        return self.repo.save(comment)

    def update_comment(self, comment: Comment):
        """
        Updates an existing comment after ensuring it has a valid ID.

        Args:
            comment (Comment): The comment instance to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        self._ensure_has_id(comment, "comment")
        self._validate_required_fields(comment)
        return self.repo.update(comment)

    def delete_comment(self, comment: Comment):
        """
        Removes a comment from the system using the base service logic.

        Args:
            comment (Comment): The comment instance to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.delete(comment, "comment")
