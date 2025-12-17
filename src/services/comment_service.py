from services.base_service import BaseService
from core.models.comment import Comment
from repository.comment_repo import CommentRepository

REQUIRED_FIELDS = {
    "comment": "Comentário",
    "intern_id": "Nome do Estagiário",
}

class CommentService(BaseService[Comment]):
    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: CommentRepository):
        super().__init__(repo)

    def add_new_comment(self, comment: Comment):
        self._validate_required_fields(comment)
        return self.repo.save(comment)

    def update_comment(self, comment: Comment):
        self._ensure_has_id(comment, "comment")
        self._validate_required_fields(comment)
        return self.repo.update(comment)

    def delete_comment(self, comment: Comment):

        return self.delete(comment, "comment")