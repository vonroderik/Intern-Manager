from data.database import DatabaseConnector
from core.models.venue import Venue
from core.models.intern import Intern

# ... (seus imports continuam iguais) ...
from repository.venue_repo import VenueRepository
from repository.intern_repo import InternRepository
from repository.observation_repo import ObservationRepository
from repository.document_repo import DocumentRepository

from services.venue_service import VenueService
from services.intern_service import InternService
from services.observation_service import ObservationService
from services.document_service import DocumentService

from services.import_service import ImportService

from pathlib import Path
from typing import Optional


def main():
    print("\nINITIALIZING DATABASE CONNECTION\n")
    try:
        db = DatabaseConnector()
        print("     Connection successful\n")
    except Exception as e:
        print(f"Failed to connect to database. Details: {e}\n")
        return  # <--- AQUI! Se falhar, para o programa. O Pylance fica feliz.

    print("INITIALIZING SERVICES\n")
    try:
        # Repositórios
        repo_venue = VenueRepository(db)
        repo_intern = InternRepository(db)
        repo_observation = ObservationRepository(db)
        repo_doc = DocumentRepository(db)

        # Services
        v_service = VenueService(repo_venue)
        i_service = InternService(repo_intern)
        o_service = ObservationService(repo_observation)
        d_service = DocumentService(repo_doc)

        # Import Service
        imp_service = ImportService(
            intern_service=i_service,
            venue_service=v_service,
        )
        print("     Services initialized successfuly\n")
    except Exception as e:
        print(f"Failed to initialize services. Details: {e}\n")
        return  # <--- Se não tem serviço, não tem programa. Tchau.

    print("READING CSV FILE AND ADDING INTERNS AND VENUES")

    # Pegamos o caminho. Se vier None, aborta.
    csv_path = get_csv_path()
    if not csv_path:
        print("Import aborted due to missing CSV file.")
        return

    try:
        imp_service.read_file(csv_path)
    except Exception as e:
        print(f"Failed to read file and add interns and venues. Details: {e}\n")


def get_csv_path() -> Optional[Path]:  # <--- Tipagem ajuda o Pylance
    csv_file = None  # Inicializamos com None para garantir que a variável existe

    try:
        # Ajuste de caminho para subir até a raiz e descer em data/imports
        # Assumindo que main.py está em src/utils/main.py ou src/main.py
        # Vamos usar a lógica de 3 parents igual ao database.py se estiver em src/utils
        # Se estiver em src/, são 2 parents. Vou usar resolve para garantir.

        current_file = Path(__file__).resolve()

        # Se main.py está em src/main.py:
        project_root = current_file.parent.parent

        # Se main.py estiver em src/utils/main.py (como parece na sua estrutura):
        if current_file.parent.name == "utils":
            project_root = current_file.parent.parent.parent

        imports_dir = project_root / "data" / "imports"

        if not imports_dir.exists():
            raise FileNotFoundError(f"Imports directory not found: {imports_dir}")

        csv_files = list(imports_dir.glob("*.csv"))

        if not csv_files:
            raise FileNotFoundError("No CSV file found in imports directory")

        if len(csv_files) > 1:
            raise RuntimeError(f"Multiple CSV files found: {csv_files}")

        csv_file = csv_files[0]
        print(f"CSV file found: {csv_file}\n")

    except (FileNotFoundError, RuntimeError) as e:
        print(f"Failed to locate CSV file. Details: {e}\n")
        return None  # Retorna None explicitamente se der erro

    return csv_file


if __name__ == "__main__":
    main()
