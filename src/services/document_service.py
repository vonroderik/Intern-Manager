from services.base_service import BaseService
from core.models.document import Document
from repository.document_repo import DocumentRepository
from core.constants import DEFAULT_DOCUMENTS_LIST

REQUIRED_FIELDS = {
    "document_name": "Nome do Documento",
    "intern_id": "ID do Estagiário",
}


class DocumentService(BaseService[Document]):
    REQUIRED_FIELDS = REQUIRED_FIELDS

    def __init__(self, repo: DocumentRepository):
        super().__init__(repo)

    def add_new_document(self, document: Document):
        self._validate_required_fields(document)
        return self.repo.save(document)

    def update_document(self, document: Document):
        self._ensure_has_id(document, "document")
        self._validate_required_fields(document)
        return self.repo.update(document)

    def delete_document(self, document: Document):
        return self.delete(document, "document")

    def create_initial_documents_batch(self, intern_id: int):
        """
        Gera o kit padrão de documentos para um novo estagiário.
        """

        existing = self.repo.get_by_intern_id(intern_id)
        if existing:
            return

        docs_to_create = []

        for name in DEFAULT_DOCUMENTS_LIST:
            docs_to_create.append(
                Document(intern_id=intern_id, document_name=name, is_completed=False)
            )

        self.repo.create_batch(docs_to_create)

    def count_total_pending(self) -> int:
        return self.repo.count_pending()
