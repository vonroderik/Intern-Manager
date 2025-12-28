from typing import List
from services.base_service import BaseService
from core.models.grade import Grade
from repository.grade_repo import GradeRepository
from utils.validations import validate_required_fields

REQUIRED_FIELDS = {
    "intern_id": "Estagiário",
    "criteria_id": "Critério de Avaliação",
    "value": "Nota (Valor)",
}


class GradeService(BaseService[Grade]):
    """
    Service class responsible for business logic related to grades.
    """

    def __init__(self, repo: GradeRepository):
        super().__init__(repo)

    def _validate_grade_value(self, grade: Grade):
        """
        Ensures the grade value is not negative.
        """
        if grade.value < 0:
            raise ValueError("A nota não pode ser negativa.")

    def get_intern_grades(self, intern_id: int) -> List[Grade]:
        """
        Retrieves all grades associated with a specific intern.
        """
        return self.repo.get_by_intern_id(intern_id)

    def add_new_grade(self, grade: Grade) -> int:
        """
        Validates and adds a new grade to the system.
        """

        validate_required_fields(grade, REQUIRED_FIELDS)

        self._validate_grade_value(grade)

        return self.repo.save(grade)

    def update_grade(self, grade: Grade) -> bool:
        """
        Updates an existing grade.
        """
        self._ensure_has_id(grade, "grade")

        validate_required_fields(grade, REQUIRED_FIELDS)
        self._validate_grade_value(grade)

        return self.repo.update(grade)

    def delete_grade(self, grade: Grade) -> bool:
        return self.delete(grade, "grade")
