from typing import Generic, TypeVar, Optional, Dict, Any
from utils.validations import validate_required_fields

T = TypeVar("T")  # Domain model (Intern, Venue, etc)


class BaseService(Generic[T]):
    """
    Base service class providing common CRUD validations and behavior.

    Concrete services should extend this class and implement
    entity-specific validation rules.
    """

    REQUIRED_FIELDS: Dict[str, str] = {}

    def __init__(self, repo: Any):
        self.repo = repo

    def _validate_required_fields(self, data: T) -> None:
        """
        Validates required fields defined by the concrete service.
        """
        if self.REQUIRED_FIELDS:
            validate_required_fields(data, self.REQUIRED_FIELDS)

    def _ensure_has_id(self, data: T, entity_name: str) -> None:
        """
        Ensures the entity has an ID before update or delete operations.
        """
        entity_id = getattr(data, f"{entity_name}_id", None)
        if entity_id is None:
            raise ValueError(
                f"{entity_name.capitalize()} has no ID and cannot be updated or deleted."
            )

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, entity_id: int) -> Optional[T]:
        return self.repo.get_by_id(entity_id)

    def delete(self, data: T, entity_name: str) -> Optional[int]:
        self._ensure_has_id(data, entity_name)
        return self.repo.delete(data)
