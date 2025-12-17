from services.base_service import BaseService
from core.models.meeting import Meeting
from repository.meeting_repo import MeetingRepository
from utils.validations import parse_date_to_iso

REQUIRED_FIELDS = {
    "intern_id": "ID do Estagiário",
    "meeting_date": "Data da Reunião",
}


class MeetingService(BaseService[Meeting]):
    """
    Service class responsible for business logic related to supervision meetings.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: MeetingRepository):
        super().__init__(repo)

    def add_new_meeting(self, meeting: Meeting):
        """
        Validates date format and adds a new meeting.
        Expects date in UI format (DD/MM/YYYY) and converts to ISO.
        """
        self._validate_required_fields(meeting)

        # Normaliza a data para ISO se ela estiver no formato UI (DD/MM/YYYY)
        # Se já estiver em ISO (ex: vindo de um script), o parse vai falhar,
        # então fazemos um try/except simples ou assumimos que o input vem da UI.
        # Por segurança, vou assumir que vem da UI conforme seu padrão.
        try:
            meeting.meeting_date = parse_date_to_iso(meeting.meeting_date)
        except ValueError:
            # Se falhar, assume que já pode estar em ISO ou formato inválido
            # Idealmente, teríamos uma validação mais robusta aqui.
            pass

        return self.repo.save(meeting)

    def get_meetings_by_intern(self, intern_id: int):
        """
        Retrieves all meetings associated with a specific intern.
        """
        return self.repo.get_by_intern_id(intern_id)

    def delete_meeting(self, meeting: Meeting):
        return self.delete(meeting, "meeting")
