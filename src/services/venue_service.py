from services.base_service import BaseService
from core.models.venue import Venue
from repository.venue_repo import VenueRepository
from utils.validations import validate_email_format

from typing import Optional

REQUIRED_FIELDS = {
    "venue_name": "Nome do local de Estágio",
    "supervisor_name": "Nome do Supervisor",
}


class VenueService(BaseService[Venue]):
    """
    Service class responsible for business logic related to internship venues.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: VenueRepository):
        """
        Initializes the VenueService with the specified repository.

        Args:
            repo (VenueRepository): Repository for venue persistence.
        """
        super().__init__(repo)

    def add_new_venue(self, venue: Venue):
        """
        Validates and adds a new venue to the system.

        Args:
            venue (Venue): The venue instance to be added.

        Returns:
            int: The ID of the newly created venue.
        """
        self._validate_required_fields(venue)
        validate_email_format(str(venue.supervisor_email))
        return self.repo.save(venue)

    def get_by_name(self, name: str) -> Optional[Venue]:
        """Busca um local pelo nome (encapsulando o repositório)."""
        return self.repo.get_by_name(name)

    def update_venue(self, venue: Venue):
        """
        Updates an existing venue after ensuring it has a valid ID.

        Args:
            venue (Venue): The venue instance to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        self._ensure_has_id(venue, "venue")
        return self.repo.update(venue)

    def delete_venue(self, venue: Venue):
        """
        Removes a venue from the system using the base service logic.

        Args:
            venue (Venue): The venue instance to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.delete(venue, "venue")
