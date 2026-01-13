import os
import shutil
from datetime import datetime

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Config
from config import DB_PATH

# Models
from core.models.intern import Intern

# Services
from services.document_service import DocumentService
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.grade_service import GradeService
from services.import_service import ImportService
from services.intern_service import InternService
from services.meeting_service import MeetingService
from services.observation_service import ObservationService
from services.report_service import ReportService
from services.venue_service import VenueService

# Views
from ui.dashboard_view import DashboardView

# Dialogs
from ui.dialogs.criteria_manager_dialog import CriteriaManagerDialog
from ui.dialogs.document_dialog import DocumentDialog
from ui.dialogs.grade_dialog import GradeDialog
from ui.dialogs.intern_dialog import InternDialog
from ui.dialogs.meeting_dialog import MeetingDialog
from ui.dialogs.observation_dialog import ObservationDialog
from ui.dialogs.report_dialog import ReportDialog
from ui.dialogs.venue_manager_dialog import VenueManagerDialog
from ui.dialogs.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """
    Janela Principal da aplicação Intern Manager 2026.
    Gerencia a navegação entre Dashboard e Lista de Estagiários.
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
        report_service: ReportService,
        import_service: ImportService,
    ):
        super().__init__()

        # Injeção de Dependências
        self.service = intern_service
        self.criteria_service = criteria_service
        self.grade_service = grade_service
        self.obs_service = observation_service
        self.venue_service = venue_service
        self.doc_service = document_service
        self.meeting_service = meeting_service
        self.report_service = report_service
        self.import_service = import_service

        self._setup_window()
        self._setup_ui()

        # Carrega dados iniciais
        self.load_data()

    def _setup_window(self):
        self.setWindowTitle("Intern Manager 2026")
        self.setMinimumSize(1100, 700)
        self.showMaximized()

    def _setup_ui(self):
        """Configura a interface gráfica completa."""

        # 1. Menu Superior
        self._create_menu_bar()

        # 2. Widget Central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 3. Abas
        self.tabs = QTabWidget()
        self._style_tabs()

        # Aba 1: Dashboard
        self.tab_dashboard = DashboardView(
            self.service, self.doc_service, self.meeting_service, self.venue_service
        )
        self.tabs.addTab(self.tab_dashboard, "📊 Visão Geral")

        # Aba 2: Lista de Estagiários
        self.tab_list = QWidget()
        self._setup_list_tab()
        self.tabs.addTab(self.tab_list, "👥 Gerenciar Estagiários")

        # Eventos
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.main_layout.addWidget(self.tabs)

    def _style_tabs(self):
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #ddd; top: -1px; }
            QTabBar::tab {
                background: #f0f0f0; 
                padding: 10px 20px; 
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected { 
                background: white; 
                font-weight: bold; 
                border-top: 2px solid #0078D7; 
            }
        """)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        # --- Menu Arquivo ---
        file_menu = menu_bar.addMenu("Arquivo")

        act_import = QAction("📂 Importar CSV...", self)
        act_import.setShortcut("Ctrl+I")
        act_import.triggered.connect(self.import_csv_dialog)
        file_menu.addAction(act_import)

        act_backup = QAction("💾 Fazer Backup...", self)
        act_backup.setShortcut("Ctrl+B")
        act_backup.triggered.connect(self.backup_database)
        file_menu.addAction(act_backup)

        file_menu.addSeparator()

        # --- Menu Configurações ---
        act_settings = QAction("⚙️ Configurações", self)
        act_settings.triggered.connect(self.open_settings)
        file_menu.addAction(act_settings)

        file_menu.addSeparator()

        act_exit = QAction("Sair", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # --- Menu Ajuda ---
        help_menu = menu_bar.addMenu("Ajuda")
        act_open_help = QAction("❓ Abrir Manual", self)
        act_open_help.setShortcut("F1")
        act_open_help.triggered.connect(self.open_help)
        help_menu.addAction(act_open_help)

    def _setup_list_tab(self):
        """Configura o conteúdo da aba de lista de estagiários."""
        layout = QVBoxLayout(self.tab_list)

        # Header da Aba
        header_layout = QHBoxLayout()
        lbl_titulo = QLabel("Estagiários Cadastrados")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Buscar por Nome ou RA...")
        self.txt_search.setFixedWidth(300)
        self.txt_search.setStyleSheet("""
            QLineEdit { border: 1px solid #ccc; border-radius: 15px; padding: 5px 15px; }
            QLineEdit:focus { border: 1px solid #0078D7; background-color: #fff; }
        """)
        self.txt_search.textChanged.connect(self.filter_table)

        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()
        header_layout.addWidget(self.txt_search)
        layout.addLayout(header_layout)

        # Barra de Botões
        self._setup_action_buttons(layout)

        # Tabela
        self._setup_table(layout)

    def _setup_action_buttons(self, layout):
        actions_layout = QHBoxLayout()

        # Estilos
        btn_pri = "QPushButton { background-color: #0078D7; color: white; border-radius: 5px; padding: 8px 15px; font-weight: bold; }"
        btn_sec = "QPushButton { background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; padding: 8px 12px; }"
        btn_dang = "QPushButton { background-color: white; color: #dc3545; border: 1px solid #dc3545; border-radius: 5px; padding: 8px 12px; }"

        # Grupo 1: CRUD Estagiário
        self.btn_add = QPushButton("➕ Novo Aluno")
        self.btn_add.setStyleSheet(btn_pri)
        self.btn_add.clicked.connect(self.open_add_dialog)

        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_edit.setStyleSheet(btn_sec)
        self.btn_edit.clicked.connect(self.open_edit_dialog)

        self.btn_delete = QPushButton("🗑️ Excluir")
        self.btn_delete.setStyleSheet(btn_dang)
        self.btn_delete.clicked.connect(self.delete_intern)

        actions_layout.addWidget(self.btn_add)
        actions_layout.addWidget(self.btn_edit)
        actions_layout.addWidget(self.btn_delete)
        actions_layout.addWidget(self._create_v_line())

        # Grupo 2: Acadêmico
        self.btn_criteria = QPushButton("⚙️ Critérios de Avaliação")
        self.btn_grades = QPushButton("📊 Notas")
        self.btn_report = QPushButton("📄 Boletim Completo")

        for b in [self.btn_grades, self.btn_report, self.btn_criteria]:
            b.setStyleSheet(btn_sec)

        self.btn_criteria.clicked.connect(self.open_criteria_manager)
        self.btn_grades.clicked.connect(self.open_grades_dialog)
        self.btn_report.clicked.connect(self.open_report)

        actions_layout.addWidget(self.btn_criteria)
        actions_layout.addWidget(self.btn_grades)
        actions_layout.addWidget(self._create_v_line())
        actions_layout.addWidget(self.btn_report)

        actions_layout.addWidget(self._create_v_line())

        # Grupo 3: Acompanhamento
        self.btn_docs = QPushButton("📋 Documentos")
        self.btn_meetings = QPushButton("📅 Reuniões")
        self.btn_obs = QPushButton("👁️ Observações")
        self.btn_venues = QPushButton("🏥 Locais")

        for b in [self.btn_venues, self.btn_docs, self.btn_meetings, self.btn_obs]:
            b.setStyleSheet(btn_sec)

        self.btn_venues.clicked.connect(self.open_venue_manager)
        self.btn_docs.clicked.connect(self.open_documents)
        self.btn_meetings.clicked.connect(self.open_meetings)
        self.btn_obs.clicked.connect(self.open_observations)

        actions_layout.addWidget(self.btn_docs)
        actions_layout.addWidget(self.btn_meetings)
        actions_layout.addWidget(self.btn_obs)
        actions_layout.addWidget(self._create_v_line())
        actions_layout.addWidget(self.btn_venues)
        actions_layout.addStretch()

        layout.addLayout(actions_layout)

    def _setup_table(self, layout):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Local", "RA", "Status"])
        self.table.setColumnHidden(0, True)
        self.table.setStyleSheet("""
            QHeaderView::section { background-color: #f8f9fa; padding: 6px; border: 1px solid #dee2e6; font-weight: bold; }
            QTableWidget { 
                gridline-color: #e9ecef;
                selection-background-color: #607D8B;
                selection-color: white; 
            }
            QTableWidget::item { padding: 5px; }
        """)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.table.doubleClicked.connect(self.open_edit_dialog)
        layout.addWidget(self.table)

    def _create_v_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def on_tab_changed(self, index):
        if index == 0:
            self.tab_dashboard.refresh_data()
        elif index == 1:
            self.load_data()

    # --- Lógica de Dados ---

    def load_data(self):
        interns = self.service.get_all_interns()
        all_venues = self.venue_service.get_all()
        venue_map = {v.venue_id: v.venue_name for v in all_venues}
        self.table.setRowCount(0)
        for row, intern in enumerate(interns):
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(intern.intern_id)))
            # Nome
            self.table.setItem(row, 1, QTableWidgetItem(str(intern.name or "")))
            # Local
            venue_name = "-"
            if intern.venue_id:
                # Busca no dicionário pelo ID.
                venue_name = venue_map.get(intern.venue_id, "-")

            self.table.setItem(row, 2, QTableWidgetItem(venue_name))
            # RA
            ra_display = str(intern.registration_number or "")
            self.table.setItem(row, 3, QTableWidgetItem(ra_display))
            # Status
            real_status = intern.status
            cell_status = QTableWidgetItem(real_status)
            cell_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if real_status == "Concluído":
                cell_status.setForeground(Qt.GlobalColor.blue)

            self.table.setItem(row, 4, cell_status)

        if self.txt_search.text():
            self.filter_table(self.txt_search.text())

    def filter_table(self, text):
        search_text = text.lower().strip()
        for row in range(self.table.rowCount()):
            item_name = self.table.item(row, 1)
            item_ra = self.table.item(row, 2)

            # Proteção contra None
            name_val = item_name.text().lower() if item_name else ""
            ra_val = item_ra.text().lower() if item_ra else ""

            match = search_text in name_val or search_text in ra_val
            self.table.setRowHidden(row, not match)

    def get_selected_intern(self) -> Intern | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno na tabela.")
            return None

        item_id = self.table.item(rows[0].row(), 0)
        if not item_id:
            return None

        i_id = int(item_id.text())
        return self.service.get_by_id(i_id)

    # --- Actions (Dialogs) ---

    def open_add_dialog(self):
        d = InternDialog(self, self.venue_service)
        if d.exec():
            try:
                new_intern = d.get_data()
                new_id = self.service.add_new_intern(new_intern)

                if new_id:
                    self.doc_service.create_initial_documents_batch(new_id)

                self.load_data()
                if hasattr(self, "tab_dashboard"):
                    self.tab_dashboard.refresh_data()

                QMessageBox.information(self, "Sucesso", "Aluno cadastrado!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao salvar: {str(e)}")

    def open_edit_dialog(self):
        i = self.get_selected_intern()
        if not i:
            return

        d = InternDialog(self, self.venue_service, intern=i)
        if d.exec():
            try:
                new_data = d.get_data()
                # Atualizando campos
                i.name = new_data.name
                i.venue_id = new_data.venue_id
                i.registration_number = new_data.registration_number
                i.email = new_data.email
                i.term = new_data.term
                i.start_date = new_data.start_date
                i.end_date = new_data.end_date

                self.service.update_intern(i)
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Erro", str(e))

    def delete_intern(self):
        i = self.get_selected_intern()
        if not i:
            return

        confirm = QMessageBox.question(
            self,
            "Excluir",
            f"Tem certeza que deseja apagar o aluno {i.name}?\nIsso apagará TODAS as notas e documentos dele!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_intern(i)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao excluir: {e}")

    def open_grades_dialog(self):
        i = self.get_selected_intern()
        if i:
            GradeDialog(self, i, self.criteria_service, self.grade_service).exec()

    def open_report(self):
        i = self.get_selected_intern()
        if i:
            ReportDialog(
                self,
                intern=i,
                grade_service=self.grade_service,
                criteria_service=self.criteria_service,
                report_service=self.report_service,
                venue_service=self.venue_service,
                document_service=self.doc_service,
                meeting_service=self.meeting_service,
                observation_service=self.obs_service,
            ).exec()

    def open_venue_manager(self):
        VenueManagerDialog(self, self.venue_service).exec()

    def open_criteria_manager(self):
        CriteriaManagerDialog(self, self.criteria_service).exec()

    def open_observations(self):
        i = self.get_selected_intern()
        if i:
            ObservationDialog(self, i, self.obs_service).exec()

    def open_documents(self):
        i = self.get_selected_intern()
        if i:
            DocumentDialog(self, i, self.doc_service).exec()

    def open_meetings(self):
        i = self.get_selected_intern()
        if i:
            MeetingDialog(self, i, self.meeting_service).exec()

    def open_settings(self):
        SettingsDialog(self).exec()

    def backup_database(self):
        filename = f"backup_interns_{datetime.now():%Y-%m-%d_%H%M}.db"
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Backup", filename, "SQLite DB (*.db)"
        )
        if path:
            try:
                shutil.copy(DB_PATH, path)
                QMessageBox.information(
                    self, "Backup", "Cópia de segurança realizada com sucesso!"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha no backup: {e}")

    def import_csv_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar CSV", "", "CSV Files (*.csv)"
        )
        if path:
            try:
                self.import_service.read_file(path)
                self.load_data()
                self.tab_dashboard.refresh_data()
                QMessageBox.information(
                    self, "Importação", "Dados importados com sucesso!"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro na Importação", str(e))

    def open_help(self):
        pdf_filename = "help.pdf"
        path = os.path.join(os.getcwd(), "resources", pdf_filename)

        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.warning(
                self,
                "Manual não encontrado",
                f"O arquivo '{pdf_filename}' não foi encontrado em:\n{path}",
            )
