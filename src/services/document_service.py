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
