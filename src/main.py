from pathlib import Path
from typing import Optional

# Data Layer
from data.database import DatabaseConnector

# Models (Importados apenas se necessário para tipagem, mas o Python resolve em runtime)

# Repositories
from repository.venue_repo import VenueRepository
from repository.intern_repo import InternRepository
from repository.document_repo import DocumentRepository
from repository.observation_repo import ObservationRepository
from repository.evaluation_criteria_repo import EvaluationCriteriaRepository
from repository.grade_repo import GradeRepository

# Services
from services.venue_service import VenueService
from services.intern_service import InternService
from services.document_service import DocumentService
from services.observation_service import ObservationService
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.grade_service import GradeService
from services.import_service import ImportService

# Utils
from utils.seeder import seed_default_criteria


def main():
    print("\n=== SYSTEM STARTUP ===\n")

    # 1. DATABASE CONNECTION

    print("INITIALIZING DATABASE CONNECTION")
    try:
        db = DatabaseConnector()
        print("   -> Connection successful\n")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to connect to database. Details: {e}\n")
        return  # Fail Fast

    # 2. INITIALIZING SERVICES & REPOSITORIES

    print("INITIALIZING SERVICES")
    try:
        # Repositories
        repo_venue = VenueRepository(db)
        repo_intern = InternRepository(db)
        repo_doc = DocumentRepository(db)
        repo_obs = ObservationRepository(db)
        repo_criteria = EvaluationCriteriaRepository(db)
        repo_grade = GradeRepository(db)

        # Services
        v_service = VenueService(repo_venue)
        i_service = InternService(repo_intern)
        d_service = DocumentService(repo_doc)
        obs_service = ObservationService(repo_obs)

        # Criteria Service
        criteria_service = EvaluationCriteriaService(repo_criteria)

        # Grade Service
        # ATTENTION: Injecting repo_criteria to validate max grades values
        grade_service = GradeService(repo=repo_grade, criteria_repo=repo_criteria)

        # Import Service
        imp_service = ImportService(
            intern_service=i_service,
            venue_service=v_service,
            document_service=d_service,
        )
        print("   -> Services initialized successfully\n")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize services. Details: {e}\n")
        return  # Fail Fast

    # 3. DATA SEEDING
    # Makes sure evaluation criteria adds to 10 points
    try:
        seed_default_criteria(criteria_service)
    except Exception as e:
        print(f"WARNING: Failed to seed default criteria. Details: {e}\n")

    # 4. CSV IMPORT
    print("READING CSV FILE AND ADDING INTERNS")

    csv_path = get_csv_path()
    if not csv_path:
        print("Import aborted due to missing CSV file.")
        return

    try:
        imp_service.read_file(csv_path)
        print("\n=== SYSTEM READY ===")
    except Exception as e:
        print(f"ERROR: Failed to process import file. Details: {e}\n")


def get_csv_path() -> Optional[Path]:
    """
    Locates the CSV import file in the data/imports directory.
    Handles different execution contexts (src root vs utils).
    """
    csv_file = None

    try:
        current_file = Path(__file__).resolve()

        project_root = current_file.parent.parent

        imports_dir = project_root / "data" / "imports"

        if not imports_dir.exists():
            project_root = current_file.parent.parent.parent
            imports_dir = project_root / "data" / "imports"

            if not imports_dir.exists():
                raise FileNotFoundError(
                    f"Imports directory not found at: {imports_dir}"
                )

        csv_files = list(imports_dir.glob("*.csv"))

        if not csv_files:
            raise FileNotFoundError("No CSV file found in imports directory")

        if len(csv_files) > 1:
            raise RuntimeError(
                f"Multiple CSV files found: {[f.name for f in csv_files]}. Please keep only one."
            )

        csv_file = csv_files[0]
        print(f"CSV file found: {csv_file.name}\n")

    except (FileNotFoundError, RuntimeError) as e:
        print(f"Failed to locate CSV file. Details: {e}\n")
        return None

    return csv_file


if __name__ == "__main__":
    main()
