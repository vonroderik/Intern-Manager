from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QAbstractItemView,
    QInputDialog,
    QMessageBox,
    QLabel,
    QComboBox,
    QTextEdit,
    QDialogButtonBox,
    QWidget,
)
from PySide6.QtCore import Qt
from core.models.intern import Intern
from core.models.document import Document
from services.document_service import DocumentService

# --- Dicionário de Broncas Padrão ---
STANDARD_FEEDBACKS = {
    "--- Selecione um motivo ---": "",
    "Assinatura Faltando": "Documento recusado. Motivo: Falta a assinatura do supervisor de campo ou do estagiário.",
    "Data Inválida": "Documento recusado. Motivo: As datas informadas não correspondem ao período do estágio cadastrado.",
    "Carimbo Ausente": "Documento recusado. Motivo: É obrigatório o carimbo e assinatura da instituição concedente.",
    "Documento Errado": "Documento recusado. Motivo: O arquivo enviado não corresponde ao modelo oficial da universidade.",
    "Rasuras": "Documento recusado. Motivo: O documento apresenta rasuras ou está ilegível.",
}


class AuditDialog(QDialog):
    """Janela Popup para Auditar (Aprovar/Reprovar) um documento."""

    def __init__(self, parent, document: Document):
        super().__init__(parent)
        self.doc = document
        self.setWindowTitle(f"Auditoria: {document.document_name}")
        self.resize(500, 400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Status
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Pendente", "Entregue", "Aprovado", "Reprovado"])
        current_status = self.doc.status or "Pendente"
        self.combo_status.setCurrentText(current_status)
        self.combo_status.currentTextChanged.connect(self._on_status_change)

        layout.addWidget(QLabel("Situação do Documento:"))
        layout.addWidget(self.combo_status)

        # Área de Reprovação (Container para esconder/mostrar)
        self.rejection_widget = QWidget()
        r_layout = QVBoxLayout(self.rejection_widget)
        r_layout.setContentsMargins(0, 10, 0, 0)

        # Combo de Motivos Prontos
        self.combo_reasons = QComboBox()
        self.combo_reasons.addItems(list(STANDARD_FEEDBACKS.keys()))
        self.combo_reasons.currentTextChanged.connect(self._fill_feedback)

        r_layout.addWidget(QLabel("Motivo da Recusa (Preenchimento Rápido):"))
        r_layout.addWidget(self.combo_reasons)

        r_layout.addWidget(QLabel("Texto do Feedback (Enviado ao aluno):"))
        self.txt_feedback = QTextEdit()
        self.txt_feedback.setPlaceholderText("Descreva o problema aqui...")
        self.txt_feedback.setText(self.doc.feedback or "")
        r_layout.addWidget(self.txt_feedback)

        layout.addWidget(self.rejection_widget)

        # Botões
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        # Estado inicial
        self._on_status_change(self.doc.status)

    def _on_status_change(self, text):
        """Só mostra a área de feedback se for Reprovado."""
        is_rejected = text == "Reprovado"
        self.rejection_widget.setVisible(is_rejected)

    def _fill_feedback(self, reason_key):
        """Preenche o texto automaticamente."""
        text = STANDARD_FEEDBACKS.get(reason_key, "")
        if text:
            self.txt_feedback.setText(text)

    def get_data(self):
        return {
            "status": self.combo_status.currentText(),
            "feedback": self.txt_feedback.toPlainText()
            if self.combo_status.currentText() == "Reprovado"
            else None,
        }


# --- Classe Principal ---
class DocumentDialog(QDialog):
    def __init__(self, parent, intern: Intern, service: DocumentService):
        super().__init__(parent)
        self.intern = intern
        self.service = service
        self.setWindowTitle(f"Documentos: {self.intern.name}")
        self.resize(700, 500)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # ID, Nome, Status, Feedback
        self.table.setHorizontalHeaderLabels(["ID", "Documento", "Status", "Feedback"])
        self.table.setColumnHidden(0, True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.audit_document)
        layout.addWidget(self.table)

        # Legenda
        # lbl_hint = QLabel("💡 Dica: Dê um duplo clique no documento para auditar (Aprovar/Reprovar).")
        # lbl_hint.setStyleSheet("color: #666; font-style: italic;")
        # layout.addWidget(lbl_hint)

        # Botões
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
        if self.intern.intern_id is None:
            return
        docs = self.service.repo.get_by_intern_id(self.intern.intern_id)

        self.table.setRowCount(0)
        self.btn_gen.setVisible(len(docs) == 0)

        for row, doc in enumerate(docs):
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(doc.document_id)))

            # Nome
            self.table.setItem(row, 1, QTableWidgetItem(doc.document_name))

            # Status Colorido
            item_status = QTableWidgetItem(doc.status)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_status.setFont(self.table.font())

            if doc.status == "Aprovado":
                item_status.setForeground(Qt.GlobalColor.green)
            elif doc.status == "Reprovado":
                item_status.setForeground(Qt.GlobalColor.red)
                item_status.setText(f"⛔ {doc.status}")
            else:
                item_status.setForeground(Qt.GlobalColor.darkYellow)

            self.table.setItem(row, 2, item_status)

            # Feedback (Resumo)
            feedback_text = doc.feedback if doc.feedback else "-"
            self.table.setItem(row, 3, QTableWidgetItem(feedback_text))

    def audit_document(self):
        """Abre a tela de auditoria."""
        row = self.table.currentRow()
        if row < 0:
            return

        item_id = self.table.item(row, 0)
        if not item_id:
            return
        doc_id = int(item_id.text())

        # Agora usamos o método correto do Service!
        doc = self.service.get_document_by_id(doc_id)

        if doc:
            audit = AuditDialog(self, doc)
            if audit.exec():
                data = audit.get_data()
                doc.status = data["status"]
                doc.feedback = data["feedback"]

                self.service.update_document(doc)
                self.load_data()

    def add_document(self):
        if self.intern.intern_id is None:
            QMessageBox.warning(
                self, "Erro", "Salve o aluno antes de adicionar documentos."
            )
            return
        name, ok = QInputDialog.getText(self, "Novo", "Nome do documento:")
        if ok and name:
            new_doc = Document(
                intern_id=self.intern.intern_id, document_name=name, status="Pendente"
            )
            self.service.add_new_document(new_doc)
            self.load_data()

    def generate_defaults(self):
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
        doc = self.service.get_document_by_id(doc_id)  # Usando service
        if doc:
            self.service.delete_document(doc)
            self.load_data()
