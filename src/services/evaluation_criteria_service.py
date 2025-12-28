from services.base_service import BaseService
from core.models.evaluation_criteria import EvaluationCriteria
from repository.evaluation_criteria_repo import EvaluationCriteriaRepository
from utils.validations import validate_required_fields

REQUIRED_FIELDS = {
    "name": "Nome do Critério",
    "weight": "Peso da Nota",
}


class EvaluationCriteriaService(BaseService[EvaluationCriteria]):
    """
    Service class responsible for business logic related to evaluation criteria.
    """

    def __init__(self, repo: EvaluationCriteriaRepository):
        super().__init__(repo)

    def _validate_weight(self, criteria: EvaluationCriteria):
        """
        Ensures the weight is a positive number.
        """
        if criteria.weight <= 0:
            raise ValueError("O peso do critério deve ser maior que zero.")

    def add_new_criteria(self, criteria: EvaluationCriteria) -> int:
        """
        Validates and adds a new evaluation criteria to the system.
        """

        validate_required_fields(criteria, REQUIRED_FIELDS)

        self._validate_weight(criteria)

        return self.repo.save(criteria)

    def update_criteria(self, criteria: EvaluationCriteria) -> bool:
        """
        Updates an existing criteria after ensuring it has a valid ID.
        """
        self._ensure_has_id(criteria, "evaluation criteria")

        validate_required_fields(criteria, REQUIRED_FIELDS)
        self._validate_weight(criteria)

        return self.repo.update(criteria)

    def delete_criteria(self, criteria: EvaluationCriteria) -> bool:
        return self.delete(criteria, "evaluation criteria")
