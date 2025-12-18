from data.database import DatabaseConnector

from repository.venue_repo import VenueRepository
from repository.intern_repo import InternRepository
# from repository.meeting_repo import MeetingRepository
# from repository.document_repo import DocumentRepository
# from repository.comment_repo import CommentRepository

from services.venue_service import VenueService
from services.intern_service import InternService
# from services.meeting_service import MeetingService
# from services.document_service import DocumentService
# from services.comment_service import CommentService

from services.import_service import ImportService

from pathlib import Path


def main():
    print("\nINITIALIZING DATABASE CONNECTION\n")
    try:
        db = DatabaseConnector()
        print("     Connection successful\n")
    except Exception as e:
        print(f"Failed to connect to database. Details: {e}\n")

    print("INITIALIZING SERVICES\n")
    try:
        v_service = VenueService(VenueRepository(db))
        i_service = InternService(InternRepository(db))
        # m_service = MeetingService(MeetingRepository(db))
        # d_service = DocumentService(DocumentRepository(db))
        # c_service = CommentService(CommentRepository(db))
        imp_service = ImportService(i_service, v_service)
        print("     Services initialized successfuly\n")
    except Exception as e:
        print(f"Failed to initialize services. Details: {e}\n")

    print("READING CSV FILE AND ADDING INTERNS AND VENUES")

    try:
        imp_service.read_file(get_csv_path())
    except Exception as e:
        print(f"Failed to read file and add interns and venues. Details: {e}\n")


def get_csv_path():
    try:
        imports_dir = Path(__file__).resolve().parent.parent / "data" / "imports"

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

    return csv_file


if __name__ == "__main__":
    main()
