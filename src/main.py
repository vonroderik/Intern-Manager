import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


from data.database import DatabaseConnector


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
    app = QApplication(sys.argv)

    print("\n=== SYSTEM STARTUP ===\n")

    print("INITIALIZING DATABASE CONNECTION")
    try:
        db = DatabaseConnector()
        print("   -> Connection successful\n")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to connect to database. Details: {e}\n")
        return

    app.aboutToQuit.connect(db.close)

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
        criteria_service = EvaluationCriteriaService(repo_criteria)

        # Grade Service
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
        return

    try:
        seed_default_criteria(criteria_service)
    except Exception as e:
        print(f"WARNING: Failed to seed default criteria. Details: {e}\n")

    print("CHECKING FOR CSV IMPORT...")
    csv_path = get_csv_path()

    if csv_path:
        try:
            imp_service.read_file(csv_path)
            print("   -> Import processed.\n")
        except Exception as e:
            print(f"ERROR: Failed to process import file. Details: {e}\n")
    else:
        print("   -> No CSV found or ignored. Starting with current database.\n")

    print("LAUNCHING GUI...")

    window = MainWindow(intern_service=i_service)

    window.show()

    print("\n=== SYSTEM RUNNING (GUI) ===")

    sys.exit(app.exec())


def get_csv_path() -> Optional[Path]:
    """
    Locates the CSV import file in the data/imports directory.
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
                return None

        csv_files = list(imports_dir.glob("*.csv"))

        if not csv_files:
            return None

        if len(csv_files) > 1:
            print(f"WARNING: Multiple CSV files found. Using {csv_files[0].name}")

        csv_file = csv_files[0]

    except Exception as e:
        print(f"Failed to locate CSV file. Details: {e}")
        return None

    return csv_file


if __name__ == "__main__":
    main()
