from services.base_service import BaseService
from core.models.venue import Venue
from repository.venue_repo import VenueRepository
from utils.validations import validate_email_format

REQUIRED_FIELDS = {
    "venue_name": "Nome do local de Estágio",
    "supervisor_name": "Nome do Supervisor",
}


class VenueService(BaseService[Venue]):
    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: VenueRepository):
        super().__init__(repo)

    def add_new_venue(self, venue: Venue):
        self._validate_required_fields(venue)
        validate_email_format(str(venue.supervisor_email))
        return self.repo.save(venue)

    def update_venue(self, venue: Venue):
        self._ensure_has_id(venue, "venue")
        return self.repo.update(venue)

    def delete_venue(self, venue: Venue):
        return self.delete(venue, "venue")
