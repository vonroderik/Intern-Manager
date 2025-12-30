from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,  # Layout horizontal para botões
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QPushButton,  # Botões
    QMessageBox,  # Caixas de Alerta
    QAbstractItemView,  # Para selecionar a linha inteira
)
from PySide6.QtCore import Qt

# Imports do Sistema
from services.intern_service import InternService
from core.models.intern import Intern
from ui.dialogs.intern_dialog import InternDialog  # Importa nosso formulário


class MainWindow(QMainWindow):
    def __init__(self, intern_service: InternService):
        super().__init__()
        self.service = intern_service

        self.setWindowTitle("Intern Manager 2026")
        self.setMinimumSize(1000, 600)

        # Widget Central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout Principal
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 1. Cabeçalho e Botões
        top_layout = QHBoxLayout()

        self.lbl_titulo = QLabel("Estagiários Cadastrados")
        self.lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold;")

        # Botões de Ação
        self.btn_add = QPushButton("➕ Novo Aluno")
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_delete = QPushButton("🗑️ Excluir")

        # Estilização básica dos botões
        self.btn_add.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 5px 15px;"
        )
        self.btn_edit.setStyleSheet("padding: 5px 15px;")
        self.btn_delete.setStyleSheet(
            "background-color: #f44336; color: white; padding: 5px 15px;"
        )

        # Adiciona ao layout do topo
        top_layout.addWidget(self.lbl_titulo)
        top_layout.addStretch()  # Empurra os botões para a direita
        top_layout.addWidget(self.btn_add)
        top_layout.addWidget(self.btn_edit)
        top_layout.addWidget(self.btn_delete)

        self.main_layout.addLayout(top_layout)

        # 2. Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "RA", "Status"])

        # Configurações de Comportamento da Tabela
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )  # Seleciona a linha toda
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )  # Só uma por vez
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )  # Não edita na célula direto

        # Cabeçalho
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.main_layout.addWidget(self.table)

        # 3. Conexões (Sinais e Slots)
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_edit.clicked.connect(self.open_edit_dialog)
        self.btn_delete.clicked.connect(self.delete_intern)
        # Clique duplo na tabela também edita
        self.table.doubleClicked.connect(self.open_edit_dialog)

    def load_data(self):
        """Recarrega a tabela do zero"""
        interns = self.service.get_all_interns()
        self.table.setRowCount(0)

        today = datetime.now().strftime("%Y-%m-%d")

        for row_idx, intern in enumerate(interns):
            self.table.insertRow(row_idx)

            cell_id = QTableWidgetItem(str(intern.intern_id))
            cell_name = QTableWidgetItem(str(intern.name or ""))
            cell_ra = QTableWidgetItem(str(intern.registration_number or ""))

            status_text = "Ativo"
            if intern.end_date and intern.end_date < today:
                status_text = "Concluído"

            cell_status = QTableWidgetItem(status_text)

            cell_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_ra.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row_idx, 0, cell_id)
            self.table.setItem(row_idx, 1, cell_name)
            self.table.setItem(row_idx, 2, cell_ra)
            self.table.setItem(row_idx, 3, cell_status)

    # --- LÓGICA DOS BOTÕES ---

    def open_add_dialog(self):
        """Abre o formulário vazio para criar novo"""
        dialog = InternDialog(self)  # Sem passar intern = Modo Criação

        # Se o usuário clicar em "Save" (dialog.exec() retorna True)
        if dialog.exec():
            data = dialog.get_data()
            try:
                # Converte o dict em Objeto Intern
                new_intern = Intern(**data)
                self.service.add_new_intern(new_intern)
                self.load_data()  # Recarrega a tabela
                QMessageBox.information(
                    self, "Sucesso", "Aluno cadastrado com sucesso!"
                )
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível salvar: {e}")

    def open_edit_dialog(self):
        """Abre o formulário preenchido para editar"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno para editar.")
            return

        row_index = selected_rows[0].row()

        # --- CORREÇÃO PYLANCE: Verificamos se o item existe antes de ler ---
        item_id = self.table.item(row_index, 0)
        if not item_id:
            return  # Se a célula for nula (impossível, mas o Pylance exige), aborta.

        intern_id = int(item_id.text())
        # -------------------------------------------------------------------

        intern_obj = self.service.get_by_id(intern_id)

        if not intern_obj:
            # --- CORREÇÃO PYLANCE: Mudamos de .error para .critical ---
            QMessageBox.critical(self, "Erro", "Aluno não encontrado no banco.")
            return

        dialog = InternDialog(self, intern=intern_obj)

        if dialog.exec():
            data = dialog.get_data()
            try:
                intern_obj.name = data["name"]
                intern_obj.email = data["email"]
                intern_obj.term = data["term"]
                intern_obj.start_date = data["start_date"]
                intern_obj.end_date = data["end_date"]

                self.service.update_intern(intern_obj)
                self.load_data()
                QMessageBox.information(self, "Sucesso", "Dados atualizados!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao atualizar: {e}")

    def delete_intern(self):
        """Exclui o registro"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno para excluir.")
            return

        row_index = selected_rows[0].row()

        # --- CORREÇÃO PYLANCE: Extraímos os itens e checamos se não são None ---
        item_id = self.table.item(row_index, 0)
        item_name = self.table.item(row_index, 1)

        # Se por algum milagre a linha existir mas as células estiverem vazias
        if not item_id or not item_name:
            return

        intern_id = int(item_id.text())
        intern_name = item_name.text()
        # -----------------------------------------------------------------------

        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o aluno '{intern_name}'?\nIsso não pode ser desfeito.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                intern_obj = self.service.get_by_id(intern_id)
                if intern_obj:
                    self.service.delete_intern(intern_obj)
                    self.load_data()
            except Exception as e:
                # Mudado para critical aqui também por consistência
                QMessageBox.critical(self, "Erro", f"Falha ao excluir: {e}")
