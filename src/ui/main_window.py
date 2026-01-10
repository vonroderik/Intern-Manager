from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QPushButton,
    QMessageBox,
    QAbstractItemView,
    QInputDialog,
)
from PySide6.QtCore import Qt

# Services
from services.intern_service import InternService
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.grade_service import GradeService

# Models
from core.models.intern import Intern
from core.models.evaluation_criteria import EvaluationCriteria


# Dialogs
from ui.dialogs.intern_dialog import InternDialog
from ui.dialogs.grade_dialog import GradeDialog
from ui.dialogs.report_dialog import ReportDialog
from ui.dialogs.criteria_dialog import CriteriaDialog
from ui.dialogs.observation_dialog import ObservationDialog
from services.observation_service import ObservationService
from ui.dialogs.criteria_manager_dialog import CriteriaManagerDialog


class MainWindow(QMainWindow):
    """
    Main application window for the Intern Manager system.
    """

    def __init__(
        self,
        intern_service: InternService,
        criteria_service: EvaluationCriteriaService,
        grade_service: GradeService,
        observation_service: ObservationService
    ):
        super().__init__()

        self.service = intern_service
        self.criteria_service = criteria_service
        self.grade_service = grade_service
        self.obs_service = observation_service

        self.setWindowTitle("Intern Manager 2026")
        self.setMinimumSize(1000, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.setup_ui()
        self.load_data()


    def setup_ui(self):
        """
        Configures the visual elements, buttons and table.
        """
        top_layout = QHBoxLayout()

        self.lbl_titulo = QLabel("Estagiários Cadastrados")

        self.lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px;")

        # --- Styles CSS (QSS) ---
        # Standard button (light blue)
        btn_style_base = """
            QPushButton {
                background-color: #f0f0f0; 
                border: 1px solid #ccc; 
                border-radius: 5px; 
                padding: 8px 15px; 
                font-size: 13px;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #bbb;
            }
        """
        
        # Primary action button (Add/Save - Green or strong blue)
        btn_style_primary = """
            QPushButton {
                background-color: #0078D7; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                padding: 8px 15px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0063b1; }
        """

        # Danger button (Delete - Red)
        btn_style_danger = """
            QPushButton {
                background-color: #fff; 
                color: #d9534f; 
                border: 1px solid #d9534f; 
                border-radius: 5px; 
                padding: 8px 15px;
            }
            QPushButton:hover { 
                background-color: #d9534f; 
                color: white; 
            }
        """

        # --- Buttons ---
        self.btn_add = QPushButton("➕ Novo Aluno")
        self.btn_add.setStyleSheet(btn_style_primary) # Destaque para a ação principal
        
        self.btn_grades = QPushButton("📊 Lançar Notas")
        self.btn_grades.setStyleSheet(btn_style_base)

        self.btn_report = QPushButton("📄 Boletim")
        self.btn_report.setStyleSheet(btn_style_base)
        
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_edit.setStyleSheet(btn_style_base)

        self.btn_obs = QPushButton("👁️ Observações")
        self.btn_obs.setStyleSheet(btn_style_base) # Use aquele estilo que definimos antes
        self.btn_obs.clicked.connect(self.open_observations)

        self.btn_criteria = QPushButton("⚙️ Critérios")
        self.btn_criteria.setStyleSheet(btn_style_base)

        self.btn_delete = QPushButton("🗑️ Excluir")
        self.btn_delete.setStyleSheet(btn_style_danger)


        top_layout.addWidget(self.lbl_titulo)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_add)
        
        # Agrupamento visual de ações secundárias
        top_layout.addWidget(self.btn_grades)
        top_layout.addWidget(self.btn_report)
        top_layout.addWidget(self.btn_obs)
        
        # Separador visual (espaço)
        top_layout.addSpacing(20) 
        
        top_layout.addWidget(self.btn_criteria)
        top_layout.addWidget(self.btn_edit)
        top_layout.addWidget(self.btn_delete)

        self.main_layout.addLayout(top_layout)

        # --- Tabela ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "RA", "Status"])
        
        # Estilo da Tabela para combinar
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 4px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
            QTableWidget {
                gridline-color: #dee2e6;
            }
        """)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.main_layout.addWidget(self.table)

        # --- Conexões ---
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_edit.clicked.connect(self.open_edit_dialog)
        self.btn_grades.clicked.connect(self.open_grades_dialog)
        self.btn_report.clicked.connect(self.open_report)
        self.btn_criteria.clicked.connect(self.open_criteria_manager)
        self.btn_delete.clicked.connect(self.delete_intern)

        self.table.doubleClicked.connect(self.open_edit_dialog)

    def load_data(self):
        """
        Fetches data and repopulates the table.
        """
        interns = self.service.get_all_interns()
        self.table.setRowCount(0)

        for row_idx, intern in enumerate(interns):
            self.table.insertRow(row_idx)

            cell_id = QTableWidgetItem(str(intern.intern_id))
            cell_name = QTableWidgetItem(str(intern.name or ""))
            cell_ra = QTableWidgetItem(str(intern.registration_number or ""))
            cell_status = QTableWidgetItem(intern.status)

            cell_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_ra.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row_idx, 0, cell_id)
            self.table.setItem(row_idx, 1, cell_name)
            self.table.setItem(row_idx, 2, cell_ra)
            self.table.setItem(row_idx, 3, cell_status)

    def get_selected_intern(self) -> Intern | None:
        """
        Helper method to get the currently selected Intern object.
        Returns None if no row is selected.
        """
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno na tabela.")
            return None

        row_index = selected_rows[0].row()
        item_id = self.table.item(row_index, 0)
        
        if not item_id:
            return None

        intern_id = int(item_id.text())
        intern = self.service.get_by_id(intern_id)
        
        if not intern:
            QMessageBox.critical(self, "Erro", "Aluno não encontrado no banco de dados.")
            return None
            
        return intern

    def open_add_dialog(self):
        """Register a new intern."""
        dialog = InternDialog(self)

        if dialog.exec():
            try:
                new_intern = dialog.get_data()
                self.service.add_new_intern(new_intern)
                self.load_data()
                QMessageBox.information(
                    self, "Sucesso", "Aluno cadastrado com sucesso!"
                )
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível salvar: {e}")

    def open_edit_dialog(self):
        """Edit the selected intern."""
        intern_obj = self.get_selected_intern()
        if not intern_obj:
            return

        dialog = InternDialog(self, intern=intern_obj)

        if dialog.exec():
            updated_data = dialog.get_data()
            try:

                intern_obj.name = updated_data.name
                intern_obj.email = updated_data.email
                intern_obj.term = updated_data.term
                intern_obj.start_date = updated_data.start_date
                intern_obj.end_date = updated_data.end_date

                self.service.update_intern(intern_obj)
                self.load_data()
                QMessageBox.information(self, "Sucesso", "Dados atualizados!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao atualizar: {e}")

    def delete_intern(self):
        """Delete the selected intern."""
        intern_obj = self.get_selected_intern()
        if not intern_obj:
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o aluno '{intern_obj.name}'?\nIsso não pode ser desfeito.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_intern(intern_obj)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao excluir: {e}")

    def open_grades_dialog(self):
        """Open grading interface."""
        intern_obj = self.get_selected_intern()
        if not intern_obj:
            return

        dialog = GradeDialog(
            parent=self,
            intern=intern_obj,
            criteria_service=self.criteria_service,
            grade_service=self.grade_service,
        )
        dialog.exec()

    def open_report(self):
        """Open the Report Card (Boletim)."""
        intern = self.get_selected_intern()
        if not intern:
            return

        dialog = ReportDialog(
            self, 
            intern, 
            self.grade_service, 
            self.criteria_service
        )
        dialog.exec()

    def open_criteria_manager(self):
            """
            Opens the dedicated Criteria Management Dashboard.
            """
            dialog = CriteriaManagerDialog(self, self.criteria_service)
            dialog.exec()
    
    def open_observations(self):
        intern = self.get_selected_intern()
        if not intern:
            return

        dialog = ObservationDialog(self, intern, self.obs_service)
        dialog.exec()