from services.base_service import BaseService
from core.models.document import Document
from repository.document_repo import DocumentRepository

REQUIRED_FIELDS = {
    "document_name": "Nome do Documento",
    "intern_id": "ID do Estagiário",
}


class DocumentService(BaseService[Document]):
    """
    Service class responsible for business logic related to documents.

    This service handles validation, lifecycle management (CRUD), and the
    automatic generation of required documentation for interns.

    Attributes:
        repo (DocumentRepository): The repository for document persistence.
        REQUIRED_FIELDS (Dict[str, str]): Mapping of required fields for validation.
    """

    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: DocumentRepository):
        """
        Initializes the DocumentService with the specified repository.

        Args:
            repo (DocumentRepository): Repository for document persistence.
        """
        super().__init__(repo)

    def add_new_document(self, document: Document):
        """
        Validates and adds a new document to the system.

        Args:
            document (Document): The document instance to be added.

        Returns:
            int: The ID of the newly created document.

        Raises:
            ValueError: If validation fails (missing fields).
        """
        self._validate_required_fields(document)
        return self.repo.save(document)

    def update_document(self, document: Document):
        """
        Updates an existing document after ensuring it has a valid ID.

        Args:
            document (Document): The document instance to be updated.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ValueError: If the document has no ID or validation fails.
        """
        self._ensure_has_id(document, "document")
        self._validate_required_fields(document)
        return self.repo.update(document)

    def delete_document(self, document: Document):
        """
        Removes a document from the system using the base service logic.

        Args:
            document (Document): The document instance to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.delete(document, "document")

    def create_initial_documents_batch(self, intern_id: int):
        """
        Generates and saves the standard set of documents for a new intern.

        This method creates a predefined list of documents (e.g., Contract,
        Attendance Sheet, Field Diary) and persists them in a single batch
        transaction to ensure atomicity.

        Args:
            intern_id (int): The identifier of the intern receiving the documents.
        """
        default_docs_names = [
            "Contrato de Estágio",
            "Ficha de Frequência",
            "Diário de Campo",
            "Projeto de Intervenção",
            "Avaliação do Supervisor Local - Física",
            "Avaliação do Supervisor Local - Carreiras",
        ]

        docs_to_create = []
        for name in default_docs_names:
            docs_to_create.append(
                Document(intern_id=intern_id, document_name=name, is_completed=False)
            )

        self.repo.create_batch(docs_to_create)
