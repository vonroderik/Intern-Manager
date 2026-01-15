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
    QLabel,
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from services.evaluation_criteria_service import EvaluationCriteriaService
from ui.dialogs.criteria_dialog import CriteriaDialog
from ui.styles import COLORS


class CriteriaManagerDialog(QDialog):
    """
    Dialogo para gerenciar (Listar, Criar, Editar, Excluir) critérios de avaliação.
    """

    def __init__(self, parent, service: EvaluationCriteriaService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Gerenciar Critérios de Avaliação")
        self.resize(700, 500)

        # Estilo Global
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["light"]}; }}
            QTableWidget {{ 
                background-color: {COLORS["white"]}; 
                border-radius: 8px; 
                border: 1px solid {COLORS["border"]};
                gridline-color: {COLORS["light"]};
            }}
            QHeaderView::section {{
                background-color: {COLORS["white"]};
                color: {COLORS["medium"]};
                padding: 8px;
                border: none;
                border-bottom: 2px solid {COLORS["light"]};
                font-weight: bold;
                text-transform: uppercase;
                font-size: 11px;
            }}
        """)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- Cabeçalho ---
        header = QHBoxLayout()

        icon_lbl = QLabel()
        icon_lbl.setPixmap(
            qta.icon("fa5s.tasks", color=COLORS["primary"]).pixmap(QSize(32, 32))
        )
        header.addWidget(icon_lbl)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("Critérios de Avaliação")
        lbl_title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {COLORS['dark']};"
        )
        lbl_sub = QLabel(
            "Defina os pesos e critérios para calcular as notas dos estagiários."
        )
        lbl_sub.setStyleSheet(f"font-size: 12px; color: {COLORS['secondary']};")

        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        # --- Barra de Ferramentas ---
        toolbar = QHBoxLayout()

        self.btn_add = QPushButton(" Novo Critério")
        self.btn_add.setIcon(qta.icon("fa5s.plus", color="white"))
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none; 
                padding: 8px 15px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_add.clicked.connect(self.open_add_dialog)

        self.btn_edit = QPushButton(" Editar")
        self.btn_edit.setIcon(qta.icon("fa5s.pen", color=COLORS["dark"]))
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["white"]}; color: {COLORS["dark"]}; border: 1px solid {COLORS["border"]}; 
                padding: 8px 15px; border-radius: 6px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {COLORS["light"]}; }}
        """)
        self.btn_edit.clicked.connect(self.edit_selected)

        self.btn_del = QPushButton(" Excluir")
        self.btn_del.setIcon(qta.icon("fa5s.trash-alt", color=COLORS["danger"]))
        self.btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["white"]}; color: {COLORS["danger"]}; border: 1px solid {COLORS["border"]}; 
                padding: 8px 15px; border-radius: 6px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #F8D7DA; border: 1px solid #F5C6CB; }}
        """)
        self.btn_del.clicked.connect(self.delete_selected)

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_del)
        layout.addLayout(toolbar)

        # --- Tabela ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # ID, Nome, Peso, Descrição
        self.table.setHorizontalHeaderLabels(
            ["ID", "Critério", "Peso (Pts)", "Descrição"]
        )
        self.table.setColumnHidden(0, True)  # Oculta ID

        # Configuração visual da tabela
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.edit_selected)

        layout.addWidget(self.table)

        # Botão Fechar Inferior
        btn_close = QPushButton("Fechar Gerenciador")
        btn_close.setStyleSheet(
            f"color: {COLORS['secondary']}; background: transparent; border: none;"
        )
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

    def load_data(self):
        criteria_list = self.service.list_active_criteria()
        self.table.setRowCount(0)

        for row, c in enumerate(criteria_list):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 45)

            self.table.setItem(row, 0, QTableWidgetItem(str(c.criteria_id)))

            # Nome em Negrito
            item_name = QTableWidgetItem(c.name)
            font = item_name.font()
            font.setBold(True)
            item_name.setFont(font)
            self.table.setItem(row, 1, item_name)

            # Peso centralizado
            item_weight = QTableWidgetItem(str(c.weight))
            item_weight.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item_weight)

            # Descrição (cortada se longa)
            desc = c.description or "-"
            self.table.setItem(row, 3, QTableWidgetItem(desc))

    def get_selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None

        # Verificação de segurança (Corrige o erro 'NoneType has no attribute text')
        item = self.table.item(rows[0].row(), 0)
        if not item:
            return None

        return int(item.text())

    def open_add_dialog(self):
        dialog = CriteriaDialog(self)
        if dialog.exec():
            new_data = dialog.get_data()
            try:
                # CORREÇÃO: Usa 'add_new_criteria' (nome correto no service)
                self.service.add_new_criteria(new_data)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao criar: {e}")

    def edit_selected(self):
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
            "Excluir",
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
