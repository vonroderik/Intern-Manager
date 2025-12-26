from services.base_service import BaseService
from core.models.observation import Observation
from repository.observation_repo import ObservationRepository

REQUIRED_FIELDS = {
    "obersvation": "Comentário",
    "intern_id": "ID do Estagiário",
}


class ObservationService(BaseService[Observation]):
    """
    Service class responsible for business logic related to intern obersvations.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: ObservationRepository):
        """
        Initializes the ObservationService with the specified repository.

        Args:
            repo (ObservationRepository): Repository for obersvation persistence.
        """
        super().__init__(repo)

    def add_new_obersvation(self, obersvation: Observation):
        """
        Validates and adds a new obersvation to the system.

        Args:
            obersvation (Observation): The obersvation instance to be added.

        Returns:
            int: The ID of the newly created obersvation.
        """
        self._validate_required_fields(obersvation)
        return self.repo.save(obersvation)

    def update_obersvation(self, obersvation: Observation):
        """
        Updates an existing obersvation after ensuring it has a valid ID.

        Args:
            obersvation (Observation): The obersvation instance to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        self._ensure_has_id(obersvation, "obersvation")
        self._validate_required_fields(obersvation)
        return self.repo.update(obersvation)

    def delete_obersvation(self, obersvation: Observation):
        """
        Removes a obersvation from the system using the base service logic.

        Args:
            obersvation (Observation): The obersvation instance to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.delete(obersvation, "obersvation")
