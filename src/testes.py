from repository.intern_repo import InternRepository
from data.database import DatabaseConnector
from core.models.intern import Intern

db_connector = DatabaseConnector()

repo = InternRepository(db_connector)


interns = repo.get_all()
for _ in interns:
    print(_)
