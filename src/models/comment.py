from typing import Optional


class Comment:
    def __init__(self, intern_id: int, comment: str, comment_id: Optional[int] = None):
        self.intern_id = intern_id
        self.comment = comment
        self.comment_id = comment_id
