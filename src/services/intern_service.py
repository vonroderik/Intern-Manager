from core.models.intern import Intern
from repository.intern_repo import InternRepository
import logging
import re
from typing import List, Optional

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
        if not intern_data.registration_number:
            logger.error("RA não informado")
            raise ValueError("É necessário incluir o RA")

        existing = self.repo.get_by_registration_number(intern_data.registration_number)

        if existing:
            logger.error(
                f"Estagiário {intern_data.name} (ID: {existing.intern_id}) já está cadastrado"
            )
            raise ValueError(
                f"Matrícula já está cadastrada para o estagiário {existing.name} (ID: {existing.intern_id})"
            )

        email = intern_data.email

        if not email:
            raise ValueError("E-mail é obrigatório")

        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValueError("Verifique o e-mail")

        return self.repo.save(intern_data)
    
        #TODO

    def update_intern(self, intern_data: Intern) -> Optional[bool]:
        ...
        #TODO