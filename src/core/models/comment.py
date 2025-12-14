from typing import Optional


class Comment:
    """Comments associated with an Intern. Each Intern can have many Comments"""

    def __init__(self, intern_id: int, comment: str, comment_id: Optional[int] = None):
        self.intern_id = intern_id
        self.comment = comment
        self.comment_id = comment_id
