from services.base_service import BaseService
from core.models.intern import Intern
from repository.intern_repo import InternRepository
from utils.validations import (
    validate_email_format,
    validate_date_range,
    parse_date_to_iso,
)

REQUIRED_FIELDS = {
    "name": "Nome do Aluno",
    "registration_number": "RA",
    "term": "Semestre",
    "email": "E-mail",
    "start_date": "Data de Início",
    "end_date": "Data de Encerramento",
}


class InternService(BaseService[Intern]):
    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: InternRepository):
        super().__init__(repo)

    def _validate_common_intern_data(self, intern: Intern) -> None:
        self._validate_required_fields(intern)
        validate_email_format(str(intern.email))
        validate_date_range(str(intern.start_date), str(intern.end_date))

    def _normalize_intern_dates(self, intern_data: Intern) -> None:
        if intern_data.start_date is None or intern_data.end_date is None:
            raise ValueError("Datas não podem ser nulas neste ponto do fluxo.")

        assert intern_data.start_date is not None
        assert intern_data.end_date is not None

        intern_data.start_date = parse_date_to_iso(intern_data.start_date)
        intern_data.end_date = parse_date_to_iso(intern_data.end_date)

    def add_new_intern(self, intern: Intern):
        self._validate_common_intern_data(intern)
        existing = self.repo.get_by_registration_number(intern.registration_number)
        if existing:
            raise ValueError(f"RA {intern.registration_number} já está cadastrado.")
        self._normalize_intern_dates(intern)
        return self.repo.save(intern)

    def update_intern(self, intern: Intern):
        self._ensure_has_id(intern, "intern")
        existing = self.repo.get_by_registration_number(intern.registration_number)
        if existing and existing.intern_id != intern.intern_id:
            raise ValueError("Este RA pertence a outro estagiário.")
        self._validate_common_intern_data(intern)
        self._normalize_intern_dates(intern)

        return self.repo.update(intern)
