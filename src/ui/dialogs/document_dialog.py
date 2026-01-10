from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QCheckBox,
    QInputDialog,
)
from PySide6.QtCore import Qt
from core.models.intern import Intern
from core.models.document import Document
from services.document_service import DocumentService


class DocumentDialog(QDialog):
    """
    Checklist de documentos do estagiário.
    """

    def __init__(self, parent, intern: Intern, service: DocumentService):
        super().__init__(parent)
        self.intern = intern
        self.service = service

        self.setWindowTitle(f"Documentos: {self.intern.name}")
        self.resize(600, 450)

        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # --- Tabela ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nome do Documento", "Entregue?"])

        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.doubleClicked.connect(self.toggle_status)

        layout.addWidget(self.table)

        # --- Botões ---
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("➕ Novo Doc")
        self.btn_gen = QPushButton("🔄 Gerar Padrão")
        self.btn_del = QPushButton("🗑️ Excluir")

        self.btn_add.clicked.connect(self.add_document)
        self.btn_gen.clicked.connect(self.generate_defaults)
        self.btn_del.clicked.connect(self.delete_document)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_gen)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_del)

        layout.addLayout(btn_layout)

    def load_data(self):
        # Guard Clause
        if self.intern.intern_id is None:
            return

        docs = self.service.repo.get_by_intern_id(self.intern.intern_id)

        self.table.setRowCount(0)
        self.btn_gen.setVisible(len(docs) == 0)

        for row, doc in enumerate(docs):
            self.table.insertRow(row)

            # ID
            item_id = QTableWidgetItem(str(doc.document_id))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Nome
            item_name = QTableWidgetItem(doc.document_name)

            # Status (Checkbox visual)
            status_text = "✅ Sim" if doc.is_completed else "❌ Pendente"
            item_status = QTableWidgetItem(status_text)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Corzinha pra ficar bonito
            if doc.is_completed:
                item_status.setForeground(Qt.GlobalColor.green)
            else:
                item_status.setForeground(Qt.GlobalColor.red)

            self.table.setItem(row, 0, item_id)
            self.table.setItem(row, 1, item_name)
            self.table.setItem(row, 2, item_status)

    def toggle_status(self):
        """Alterna entre Entregue/Pendente ao clicar."""
        row = self.table.currentRow()
        if row < 0:
            return

        # --- CORREÇÃO PYLANCE ---
        item_id = self.table.item(row, 0)
        if not item_id:  # Se a célula estiver vazia/inválida, aborta
            return

        doc_id = int(item_id.text())
        # ------------------------

        doc = self.service.repo.get_by_id(doc_id)

        if doc:
            doc.is_completed = not doc.is_completed
            self.service.update_document(doc)
            self.load_data()

    def add_document(self):
        name, ok = QInputDialog.getText(self, "Novo Documento", "Nome do documento:")
        if ok and name:
            new_doc = Document(
                intern_id=self.intern.intern_id,  # type: ignore
                document_name=name,
                is_completed=False,
            )
            self.service.add_new_document(new_doc)
            self.load_data()

    def generate_defaults(self):
        """Gera o kit inicial de documentos."""
        if self.intern.intern_id:
            self.service.create_initial_documents_batch(self.intern.intern_id)
            self.load_data()

    def delete_document(self):
        row = self.table.currentRow()
        if row < 0:
            return

        item_id = self.table.item(row, 0)
        if not item_id:
            return

        doc_id = int(item_id.text())

        doc = self.service.repo.get_by_id(doc_id)

        if doc:
            self.service.delete_document(doc)
            self.load_data()
