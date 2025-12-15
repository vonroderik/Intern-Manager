from repository.intern_repo import InternRepository
from data.database import DatabaseConnector
from core.models.intern import Intern

db_connector = DatabaseConnector()

repo = InternRepository(db_connector)

intern = repo.get_by_id(1)
if intern:
    print(f"✅ Estagiário ID 1 encontrado!")
    print(f"Nome: {intern.name}")
    print(f"Matrícula: {intern.registration_number}")
    print(f"Termo: {intern.term}")
else:
    print("❌ Estagiário ID 1 não encontrado.")
