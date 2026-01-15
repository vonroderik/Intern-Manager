from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Intern:
    name: str
    registration_number: str
    term: str

    intern_id: Optional[int] = None
    email: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    # Ordem igual ao create_db.sql para facilitar leitura, mas dataclass usa nome
    working_days: Optional[str] = None
    working_hours: Optional[str] = None

    venue_id: Optional[int] = None

    @property
    def status(self) -> str:
        if not self.end_date:
            return "Ativo"
        try:
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            return "Concluído" if end < datetime.now() else "Ativo"
        except ValueError:
            return "Ativo"

    @property
    def formatted_start_date(self) -> str:
        if not self.start_date:
            return "-"
        try:
            return datetime.strptime(self.start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return self.start_date

    @property
    def formatted_end_date(self) -> str:
        if not self.end_date:
            return "-"
        try:
            return datetime.strptime(self.end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return self.end_date
