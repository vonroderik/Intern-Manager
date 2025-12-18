from services.base_service import BaseService
from core.models.intern import Intern
from repository.intern_repo import InternRepository
from utils.validations import (
    validate_email_format,
    validate_date_range,
    parse_date_to_iso,
)
from typing import Optional

REQUIRED_FIELDS = {
    "name": "Nome do Aluno",
    "registration_number": "RA",
    "term": "Semestre",
    "start_date": "Data de Início",
    "end_date": "Data de Encerramento",
}


class InternService(BaseService[Intern]):
    """
    Service class responsible for business logic related to interns.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: InternRepository):
        """
        Initializes the InternService with the specified repository.

        Args:
            repo (InternRepository): Repository for intern persistence.
        """
        super().__init__(repo)

    def _validate_common_intern_data(self, intern: Intern) -> None:
        """
        Performs common validations for intern data (required fields, email, dates).

        Args:
            intern (Intern): The intern instance to be validated.
        """
        validate_date_range(str(intern.start_date), str(intern.end_date))
        self._validate_required_fields(intern)
        if intern.email:
            validate_email_format(str(intern.email))

    def _normalize_intern_dates(self, intern_data: Intern) -> None:
        """
        Converts date strings from UI format to ISO format for database storage.

        Args:
            intern_data (Intern): The intern instance containing dates to normalize.

        Raises:
            ValueError: If start or end dates are missing.
        """
        if intern_data.start_date is None or intern_data.end_date is None:
            raise ValueError("Datas não podem ser nulas neste ponto do fluxo.")

        assert intern_data.start_date is not None
        assert intern_data.end_date is not None

        intern_data.start_date = parse_date_to_iso(intern_data.start_date)
        intern_data.end_date = parse_date_to_iso(intern_data.end_date)

    def add_new_intern(self, intern: Intern):
        """
        Validates and adds a new intern to the system after checking for duplicate RA.

        Args:
            intern (Intern): The intern instance to be added.

        Returns:
            int: The ID of the newly created intern.
        """
        if self.repo.get_by_registration_number(intern.registration_number):
            raise ValueError("RA já cadastrado.")

        self._normalize_intern_dates(intern)
        self._validate_common_intern_data(intern)

        return self.repo.save(intern)

    def get_by_name(self, name: str) -> Optional[Intern]:
        """Busca um local pelo nome (encapsulando o repositório)."""
        return self.repo.get_by_name(name)

    def update_intern(self, intern: Intern):
        """
        Updates an existing intern record after validation and ID check.

        Args:
            intern (Intern): The intern instance to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        self._ensure_has_id(intern, "intern")
        existing = self.repo.get_by_registration_number(intern.registration_number)
        if existing and existing.intern_id != intern.intern_id:
            raise ValueError("Este RA pertence a outro estagiário.")
        self._validate_common_intern_data(intern)
        self._normalize_intern_dates(intern)

        return self.repo.update(intern)

    def delete_intern(self, intern: Intern):
        """
        Removes an intern from the system using the base service logic.

        Args:
            intern (Intern): The intern instance to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.delete(intern, "intern")
