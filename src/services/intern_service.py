from core.models.intern import Intern
from repository.intern_repo import InternRepository
import logging
import re
from typing import List, Optional
from datetime import datetime

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
        # Checks if name, registrarion number and term are present
        if not intern_data.registration_number:
            logger.error("RA não informado")
            raise ValueError("É necessário incluir o RA")

        if not intern_data.name:
            logger.error("Nome não informado")
            raise ValueError("É necessário incluir o nome do Aluno")

        if not intern_data.term:
            logger.error("Semestre não informado")
            raise ValueError("É necessário incluir o semestre")

        # Checks if user (name or registration number) already exists
        existing_registration_number = self.repo.get_by_registration_number(
            intern_data.registration_number
        )

        if existing_registration_number:
            logger.error(
                f"Estagiário {intern_data.name} (ID: {existing_registration_number.intern_id}) já está cadastrado"
            )
            raise ValueError(
                f"Matrícula já está cadastrada para o estagiário {existing_registration_number.name} (ID: {existing_registration_number.intern_id})"
            )

        # Validates e-mail
        email = intern_data.email
        if not email:  # validates e-mail
            raise ValueError("E-mail é obrigatório")
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValueError("Verifique o e-mail")

        # Checks if end date is after start date.
        try:
            start_date = intern_data.start_date
            end_date = intern_data.end_date

            dt_start = datetime.strptime(start_date, DATE_FORMAT)
            dt_end = datetime.strptime(end_date, DATE_FORMAT)

            if dt_end <= dt_start:
                raise ValueError(
                    "A data de encerramento deve ser posterior à data de início"
                )

            intern_data.start_date = dt_start.strftime("%Y-%m-%d")
            intern_data.end_date = dt_end.strftime("%Y-%m-%d")
        except ValueError as e:
            raise ValueError(
                f"Erro no formato da data. Use o formato DD/MM/AAAA. Detalhe: {e}"
            )
        return self.repo.save(intern_data)

        # TODO

    def update_intern(self, intern_data: Intern) -> Optional[bool]:
        ...
        # TODO
