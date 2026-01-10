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
    QFrame,  # Importei para fazer linhas divisórias bonitas
)
from PySide6.QtCore import Qt

# Services
from services.intern_service import InternService
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.grade_service import GradeService
from services.venue_service import VenueService
from services.observation_service import ObservationService
from services.document_service import DocumentService
from services.meeting_service import MeetingService

# Models
from core.models.intern import Intern
from core.models.evaluation_criteria import EvaluationCriteria

# Dialogs
from ui.dialogs.intern_dialog import InternDialog
from ui.dialogs.grade_dialog import GradeDialog
from ui.dialogs.report_dialog import ReportDialog
from ui.dialogs.criteria_dialog import CriteriaDialog
from ui.dialogs.observation_dialog import ObservationDialog
from ui.dialogs.criteria_manager_dialog import CriteriaManagerDialog
from ui.dialogs.venue_manager_dialog import VenueManagerDialog
from ui.dialogs.document_dialog import DocumentDialog
from ui.dialogs.meeting_dialog import MeetingDialog


class MainWindow(QMainWindow):
    """
    Main application window for the Intern Manager system.
    """

    def __init__(
        self,
        intern_service: InternService,
        criteria_service: EvaluationCriteriaService,
        grade_service: GradeService,
        observation_service: ObservationService,
        venue_service: VenueService,
        document_service: DocumentService,
        meeting_service: MeetingService,
    ):
        super().__init__()

        self.service = intern_service
        self.criteria_service = criteria_service
        self.grade_service = grade_service
        self.obs_service = observation_service
        self.venue_service = venue_service
        self.doc_service = document_service
        self.meeting_service = meeting_service

        self.setWindowTitle("Intern Manager 2026")
        self.setMinimumSize(1000, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.setup_ui()
        self.load_data()

        # --- MUDANÇA 1: Iniciar maximizado ---
        self.showMaximized()

    def setup_ui(self):
        """
        Configures the visual elements, buttons and table.
        """
        
        # --- 1. Título (Linha exclusiva no topo) ---
        self.lbl_titulo = QLabel("Estagiários Cadastrados")
        self.lbl_titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #333; margin: 10px 0;"
        )
        self.main_layout.addWidget(self.lbl_titulo)

        # --- Styles CSS (QSS) ---
        btn_style_base = """
            QPushButton {
                background-color: #f8f9fa; 
                border: 1px solid #ddd; 
                border-radius: 6px; 
                padding: 8px 12px; 
                font-size: 13px;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e2e6ea;
                border-color: #adb5bd;
            }
        """

        btn_style_primary = """
            QPushButton {
                background-color: #0078D7; 
                color: white; 
                border: none; 
                border-radius: 6px; 
                padding: 8px 15px; 
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #0063b1; }
        """

        btn_style_danger = """
            QPushButton {
                background-color: #fff; 
                color: #dc3545; 
                border: 1px solid #dc3545; 
                border-radius: 6px; 
                padding: 8px 12px;
            }
            QPushButton:hover { 
                background-color: #dc3545; 
                color: white; 
            }
        """

        # --- 2. Barra de Ferramentas (Actions Layout) ---
        actions_layout = QHBoxLayout()
        
        # Grupo A: Gestão Principal
        self.btn_add = QPushButton("➕ Novo Aluno")
        self.btn_add.setStyleSheet(btn_style_primary)
        
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_edit.setStyleSheet(btn_style_base)
        
        self.btn_delete = QPushButton("🗑️ Excluir")
        self.btn_delete.setStyleSheet(btn_style_danger)

        # Grupo B: Acadêmico
        self.btn_grades = QPushButton("📊 Notas")
        self.btn_report = QPushButton("📄 Boletim")
        self.btn_criteria = QPushButton("⚙️ Critérios")
        
        for btn in [self.btn_grades, self.btn_report, self.btn_criteria]:
            btn.setStyleSheet(btn_style_base)

        # Grupo C: Acompanhamento
        self.btn_obs = QPushButton("👁️ Obs")
        self.btn_venues = QPushButton("🏥 Locais")
        self.btn_docs = QPushButton("📋 Docs")
        self.btn_meetings = QPushButton("📅 Supervisão")
        
        for btn in [self.btn_obs, self.btn_venues, self.btn_docs, self.btn_meetings]:
            btn.setStyleSheet(btn_style_base)

        # Adicionando ao layout com espaçamento inteligente
        
        # Esquerda: Ações Críticas
        actions_layout.addWidget(self.btn_add)
        actions_layout.addWidget(self.btn_edit)
        actions_layout.addWidget(self.btn_delete)
        
        # Separador
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.VLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        actions_layout.addWidget(line1)
        
        # Meio: Acadêmico
        actions_layout.addWidget(self.btn_grades)
        actions_layout.addWidget(self.btn_report)
        actions_layout.addWidget(self.btn_criteria)
        
        # Separador
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.VLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        actions_layout.addWidget(line2)

        # Direita: Rotina
        actions_layout.addWidget(self.btn_venues)
        actions_layout.addWidget(self.btn_docs)
        actions_layout.addWidget(self.btn_meetings)
        actions_layout.addWidget(self.btn_obs)
        
        actions_layout.addStretch() # Empurra tudo para a esquerda (ou remova para centralizar)

        self.main_layout.addLayout(actions_layout)

        # --- 3. Tabela ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "RA", "Status"])

        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 6px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget {
                gridline-color: #e9ecef;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True) # Fica mais fácil de ler

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.main_layout.addWidget(self.table)

        # --- Conexões ---
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_edit.clicked.connect(self.open_edit_dialog)
        self.btn_delete.clicked.connect(self.delete_intern)
        
        self.btn_grades.clicked.connect(self.open_grades_dialog)
        self.btn_report.clicked.connect(self.open_report)
        self.btn_criteria.clicked.connect(self.open_criteria_manager)
        
        self.btn_venues.clicked.connect(self.open_venue_manager)
        self.btn_obs.clicked.connect(self.open_observations)
        self.btn_docs.clicked.connect(self.open_documents)
        self.btn_meetings.clicked.connect(self.open_meetings)

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
            
            # Status simples
            status_text = intern.status if hasattr(intern, 'status') else "Ativo"
            cell_status = QTableWidgetItem(status_text)

            cell_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_ra.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row_idx, 0, cell_id)
            self.table.setItem(row_idx, 1, cell_name)
            self.table.setItem(row_idx, 2, cell_ra)
            self.table.setItem(row_idx, 3, cell_status)

    def get_selected_intern(self) -> Intern | None:
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
            QMessageBox.critical(
                self, "Erro", "Aluno não encontrado no banco de dados."
            )
            return None

        return intern

    # --- Action Methods ---

    def open_add_dialog(self):
        dialog = InternDialog(self, self.venue_service)
        if dialog.exec():
            try:
                new_intern = dialog.get_data()
                self.service.add_new_intern(new_intern)
                self.load_data()
                QMessageBox.information(self, "Sucesso", "Aluno cadastrado com sucesso!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível salvar: {e}")

    def open_edit_dialog(self):
        intern_obj = self.get_selected_intern()
        if not intern_obj: return

        dialog = InternDialog(self, self.venue_service, intern=intern_obj)
        if dialog.exec():
            updated_data = dialog.get_data()
            try:
                # Atualiza campos básicos
                intern_obj.name = updated_data.name
                intern_obj.email = updated_data.email
                intern_obj.term = updated_data.term
                intern_obj.start_date = updated_data.start_date
                intern_obj.end_date = updated_data.end_date
                intern_obj.venue_id = updated_data.venue_id # Importante atualizar venue

                self.service.update_intern(intern_obj)
                self.load_data()
                QMessageBox.information(self, "Sucesso", "Dados atualizados!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao atualizar: {e}")

    def delete_intern(self):
        intern_obj = self.get_selected_intern()
        if not intern_obj: return

        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir '{intern_obj.name}'?\nIsso apagará notas, docs e histórico.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_intern(intern_obj)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao excluir: {e}")

    def open_grades_dialog(self):
        intern_obj = self.get_selected_intern()
        if not intern_obj: return
        GradeDialog(self, intern_obj, self.criteria_service, self.grade_service).exec()

    def open_report(self):
        intern = self.get_selected_intern()
        if not intern: return
        ReportDialog(self, intern, self.grade_service, self.criteria_service).exec()

    def open_venue_manager(self):
        VenueManagerDialog(self, self.venue_service).exec()

    def open_criteria_manager(self):
        CriteriaManagerDialog(self, self.criteria_service).exec()

    def open_observations(self):
        intern = self.get_selected_intern()
        if not intern: return
        ObservationDialog(self, intern, self.obs_service).exec()

    def open_documents(self):
        intern = self.get_selected_intern()
        if not intern: return
        DocumentDialog(self, intern, self.doc_service).exec()

    def open_meetings(self):
        intern = self.get_selected_intern()
        if not intern: return
        MeetingDialog(self, intern, self.meeting_service).exec()