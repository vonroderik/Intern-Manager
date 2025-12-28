# src/services/grade_service.py

from typing import List
from services.base_service import BaseService
from core.models.grade import Grade
from repository.grade_repo import GradeRepository
from repository.evaluation_criteria_repo import EvaluationCriteriaRepository
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

    def __init__(
        self, repo: GradeRepository, criteria_repo: EvaluationCriteriaRepository
    ):
        super().__init__(repo)
        self.criteria_repo = criteria_repo

    def _validate_grade_value(self, grade: Grade):
        """
        Ensures the grade value is positive and DOES NOT EXCEED the criteria limit.
        """

        if grade.value < 0:
            raise ValueError("A nota não pode ser negativa.")

        criteria = self.criteria_repo.get_by_id(grade.criteria_id)

        if not criteria:
            raise ValueError(
                f"Critério de avaliação {grade.criteria_id} não encontrado."
            )

        if grade.value > criteria.weight:
            raise ValueError(
                f"A nota ({grade.value}) não pode ser maior que o valor máximo deste critério "
                f"({criteria.name}: Max {criteria.weight})."
            )

    def get_intern_grades(self, intern_id: int) -> List[Grade]:
        return self.repo.get_by_intern_id(intern_id)

    def add_new_grade(self, grade: Grade) -> int:
        validate_required_fields(grade, REQUIRED_FIELDS)
        self._validate_grade_value(grade)
        return self.repo.save(grade)

    def update_grade(self, grade: Grade) -> bool:
        self._ensure_has_id(grade, "grade")
        validate_required_fields(grade, REQUIRED_FIELDS)
        self._validate_grade_value(grade)
        return self.repo.update(grade)

    def delete_grade(self, grade: Grade) -> bool:
        return self.delete(grade, "grade")
