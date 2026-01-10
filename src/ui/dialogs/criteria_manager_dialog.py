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
)
from PySide6.QtCore import Qt
from services.evaluation_criteria_service import EvaluationCriteriaService
from ui.dialogs.criteria_dialog import CriteriaDialog


class CriteriaManagerDialog(QDialog):
    """
    Dialogo para gerenciar (Listar, Criar, Editar, Excluir) critérios de avaliação.
    """

    def __init__(self, parent, service: EvaluationCriteriaService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Gerenciar Critérios de Avaliação")
        self.resize(600, 400)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.layout_main = QVBoxLayout(self)

        # --- Tabela ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nome do Critério", "Peso"])

        # Configuração visual da tabela
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Ao dar dois cliques, abre edição
        self.table.doubleClicked.connect(self.edit_selected)

        self.layout_main.addWidget(self.table)

        # --- Botões de Ação ---
        self.layout_btns = QHBoxLayout()

        self.btn_new = QPushButton("➕ Novo Critério")
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_del = QPushButton("🗑️ Excluir")

        # Estilo rápido para diferenciar
        self.btn_new.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold;"
        )
        self.btn_del.setStyleSheet("color: #d9534f; border: 1px solid #d9534f;")

        self.layout_btns.addWidget(self.btn_new)
        self.layout_btns.addStretch()
        self.layout_btns.addWidget(self.btn_edit)
        self.layout_btns.addWidget(self.btn_del)

        self.layout_main.addLayout(self.layout_btns)

        # Conexões
        self.btn_new.clicked.connect(self.create_new)
        self.btn_edit.clicked.connect(self.edit_selected)
        self.btn_del.clicked.connect(self.delete_selected)

    def load_data(self):
        """Recarrega a lista do banco de dados."""
        criteria_list = self.service.list_active_criteria()
        self.table.setRowCount(0)

        for row, item in enumerate(criteria_list):
            self.table.insertRow(row)

            # ID
            cell_id = QTableWidgetItem(str(item.criteria_id))
            cell_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Nome
            cell_name = QTableWidgetItem(item.name)

            # Peso
            cell_weight = QTableWidgetItem(f"{item.weight:.1f}")
            cell_weight.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row, 0, cell_id)
            self.table.setItem(row, 1, cell_name)
            self.table.setItem(row, 2, cell_weight)

    def get_selected_id(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return None
        row = selected[0].row()
        item_id = self.table.item(row, 0)
        return int(item_id.text()) if item_id else None

    def create_new(self):
        """Abre o dialog de edição vazio."""
        dialog = CriteriaDialog(self)  # Sem passar objeto, cria novo
        if dialog.exec():
            new_criteria = dialog.get_data()
            try:
                self.service.add_new_criteria(new_criteria)
                self.load_data()  # Refresh
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao criar: {e}")

    def edit_selected(self):
        """Abre o dialog de edição com o objeto selecionado."""
        c_id = self.get_selected_id()
        if not c_id:
            QMessageBox.warning(self, "Atenção", "Selecione um critério para editar.")
            return

        all_criteria = self.service.list_active_criteria()
        target = next((c for c in all_criteria if c.criteria_id == c_id), None)

        if target:
            dialog = CriteriaDialog(self, criteria=target)
            if dialog.exec():
                updated_data = dialog.get_data()
                try:
                    self.service.update_criteria(updated_data)
                    self.load_data()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao atualizar: {e}")

    def delete_selected(self):
        c_id = self.get_selected_id()
        if not c_id:
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar",
            "Tem certeza? Isso pode afetar notas já lançadas!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            all_criteria = self.service.list_active_criteria()
            target = next((c for c in all_criteria if c.criteria_id == c_id), None)

            if target:
                try:
                    self.service.delete_criteria(target)
                    self.load_data()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao excluir: {e}")
