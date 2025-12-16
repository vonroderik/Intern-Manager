from core.models.intern import Intern
from repository.intern_repo import InternRepository
import logging
from typing import List, Optional
from utils.validations import (
    validate_required_fields,
    validate_email_format,
    validate_date_range,
)

DATE_FORMAT = "%d/%m/%Y"

logger = logging.getLogger(__name__)


class InternService:
    def __init__(self, intern_repo: InternRepository):
        self.repo = intern_repo

    def get_all_interns(self) -> List[Intern]:
        return self.repo.get_all()

    def get_intern_details(self, intern_id) -> Optional[Intern]:
        return self.repo.get_by_id(intern_id)

    def get_intern_by_registration(self, registration_number: int) -> Optional[Intern]:
        return self.repo.get_by_registration_number(registration_number)

    def get_intern_by_name(self, name: str) -> Optional[Intern]:
        return self.repo.get_by_name(name)

    def add_new_intern(self, intern_data: Intern) -> Optional[int]:
        # Validate that required fields are present.
        required_fields = {
            "name": "Nome do Aluno",
            "registration_number": "RA",
            "term": "Semestre",
            "email": "E-mail",
            "start_date": "Data de Início",
            "end_date": "Data de Encerramento",
        }

        try:
            validate_required_fields(intern_data, required_fields)

        except ValueError as e:
            logger.error(f"Campos obrigatórios ausentes: {e}")

        # Validate that e-mail is present and in the correct format
        try:
            email = intern_data.email
            validate_email_format(str(email))
        except ValueError as e:
            logger.error(f"E-mail ausente ou incorreto: {e}")

        # Validate that the end date is later than the start date
        start_date_str = str(intern_data.start_date)
        end_date_str = str(intern_data.end_date)

        try:
            validate_date_range(start_date_str, end_date_str)
        except ValueError as e:
            logger.error(
                f"A data de encerramento de estágio não pode ser anterior a data de início: {e}"
            )

        return self.repo.save(intern_data)

    def update_intern(self, intern_data: Intern) -> Optional[bool]:
        ...
        # TODO
