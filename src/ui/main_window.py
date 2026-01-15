# src/ui/main_window.py
import shutil
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QLineEdit, QFrame, QMessageBox, QFileDialog,
    QStackedWidget, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QAction

import qtawesome as qta
from config import DB_PATH

# Models & Services
from core.models.intern import Intern
# ... (Mantenha seus imports de Services aqui) ...
from services.intern_service import InternService
from services.document_service import DocumentService
from services.meeting_service import MeetingService
from services.venue_service import VenueService
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.grade_service import GradeService
from services.import_service import ImportService
from services.observation_service import ObservationService
from services.report_service import ReportService

# Dialogs
# ... (Mantenha seus imports de Dialogs aqui) ...
from ui.dialogs.intern_dialog import InternDialog
from ui.dialogs.document_dialog import DocumentDialog
from ui.dialogs.venue_manager_dialog import VenueManagerDialog
from ui.dialogs.criteria_manager_dialog import CriteriaManagerDialog
from ui.dialogs.grade_dialog import GradeDialog
from ui.dialogs.meeting_dialog import MeetingDialog
from ui.dialogs.observation_dialog import ObservationDialog
from ui.dialogs.report_dialog import ReportDialog
from ui.dialogs.settings_dialog import SettingsDialog

# Novos Componentes
from ui.styles import COLORS
from ui.dashboard_view import DashboardView
from ui.delegates import StatusDelegate

class MainWindow(QMainWindow):
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
        self.service = intern_service
        self.criteria_service = criteria_service
        self.grade_service = grade_service
        self.obs_service = observation_service
        self.venue_service = venue_service
        self.doc_service = document_service
        self.meeting_service = meeting_service
        self.report_service = report_service
        self.import_service = import_service

        self.setWindowTitle("InternManager Pro 2026")
        self.setMinimumSize(1200, 760)
        self.setWindowIcon(qta.icon('fa5s.notes-medical', color=COLORS["primary"]))
        
        # Estilo Global da Window
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COLORS['light']}; }}
            QTableWidget {{ 
                background-color: {COLORS['white']}; 
                border-radius: 8px; 
                border: 1px solid {COLORS['border']};
                gridline-color: transparent;
            }}
            QHeaderView::section {{
                background-color: {COLORS['white']};
                color: {COLORS['medium']};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {COLORS['light']};
                font-weight: bold;
                text-transform: uppercase;
            }}
            QLineEdit {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                padding: 8px;
                border-radius: 4px;
            }}
        """)

        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        # Container Principal (Horizontal: Sidebar + Conteúdo)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar
        self._setup_sidebar(main_layout)

        # 2. Conteúdo (Stack)
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # --- Páginas da Stack ---
        
        # Página 0: Dashboard
        self.page_dashboard = DashboardView(
            self.service, self.doc_service, self.meeting_service, self.venue_service
        )
        self.content_stack.addWidget(self.page_dashboard)

        # Página 1: Alunos (Lista)
        self.page_list = QWidget()
        self._setup_list_page()
        self.content_stack.addWidget(self.page_list)

        # Conectar Sidebar -> Stack
        self.sidebar_list.currentRowChanged.connect(self.on_sidebar_changed)
        
        # Seleciona primeira página
        self.sidebar_list.setCurrentRow(0)

    def _setup_sidebar(self, parent_layout):
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(240)
        sidebar_frame.setStyleSheet(f"""
            QFrame {{ background-color: {COLORS['sidebar_bg']}; border: none; }}
            QLabel {{ color: {COLORS['sidebar_text']}; }}
        """)
        
        slayout = QVBoxLayout(sidebar_frame)
        slayout.setContentsMargins(0, 0, 0, 20)
        slayout.setSpacing(10)

        # Logo / Título App
        app_title = QLabel("InternManager")
        app_title.setStyleSheet("font-size: 18px; font-weight: 900; padding: 20px 20px 5px 20px;")
        app_subtitle = QLabel("Pro 2026")
        app_subtitle.setStyleSheet(f"font-size: 12px; font-weight: normal; color: {COLORS['secondary']}; padding: 0 20px 20px 20px;")
        
        slayout.addWidget(app_title)
        slayout.addWidget(app_subtitle)

        # Lista de Navegação
        self.sidebar_list = QListWidget()
        self.sidebar_list.setFrameShape(QFrame.Shape.NoFrame)
        self.sidebar_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sidebar_list.setStyleSheet(f"""
            QListWidget {{ background-color: transparent; outline: none; }}
            QListWidget::item {{
                color: {COLORS['sidebar_text']};
                padding: 12px 20px;
                border-left: 4px solid transparent;
            }}
            QListWidget::item:selected {{
                background-color: #2D2C2B;
                border-left: 4px solid {COLORS['primary']};
                color: {COLORS['white']};
                font-weight: bold;
            }}
            QListWidget::item:hover {{
                background-color: #2D2C2B;
            }}
        """)

        # Itens do Menu
        item_dash = QListWidgetItem(qta.icon('fa5s.chart-pie', color="white"), " Dashboard")
        item_list = QListWidgetItem(qta.icon('fa5s.user-graduate', color="white"), " Alunos")
        item_venues = QListWidgetItem(qta.icon('fa5s.hospital', color="white"), " Locais")
        item_criteria = QListWidgetItem(qta.icon('fa5s.tasks', color="white"), " Critérios")

        self.sidebar_list.addItem(item_dash)
        self.sidebar_list.addItem(item_list)
        self.sidebar_list.addItem(item_venues)
        self.sidebar_list.addItem(item_criteria)
        
        slayout.addWidget(self.sidebar_list)
        slayout.addStretch()

        # Botões de Rodapé da Sidebar
        btn_settings = QPushButton(" Configurações")
        btn_settings.setIcon(qta.icon('fa5s.cog', color=COLORS['secondary']))
        btn_settings.setStyleSheet(f"text-align: left; padding: 15px 20px; background: transparent; color: {COLORS['secondary']}; border: none;")
        btn_settings.clicked.connect(self.open_settings)
        slayout.addWidget(btn_settings)

        parent_layout.addWidget(sidebar_frame)

    def _setup_list_page(self):
        layout = QVBoxLayout(self.page_list)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Header da Página
        header = QHBoxLayout()
        lbl = QLabel("Gerenciar Alunos")
        lbl.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['dark']};")
        header.addWidget(lbl)
        header.addStretch()
        
        self.btn_add = QPushButton(" Novo Aluno")
        self.btn_add.setIcon(qta.icon('fa5s.plus', color="white"))
        self.btn_add.setStyleSheet(f"background-color: {COLORS['primary']}; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        self.btn_add.clicked.connect(self.open_add_dialog)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        # Barra de Ações (Busca)
        actions = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Buscar por nome, RA ou local...")
        self.txt_search.setFixedWidth(400)
        self.txt_search.textChanged.connect(self.filter_table)
        actions.addWidget(self.txt_search)
        
        actions.addStretch()
        
        # Botões de Import/Export
        btn_import = QPushButton("Importar CSV")
        btn_import.setIcon(qta.icon('fa5s.file-import', color=COLORS['dark']))
        btn_import.clicked.connect(self.import_csv_dialog)
        actions.addWidget(btn_import)
        
        layout.addLayout(actions)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nome Completo", "Local de Estágio", "RA", "Status"])
        self.table.setColumnHidden(0, True) # ID Escondido
        
        # Configurações Tabela
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setRowHeight(0, 50) # Altura padrão linha
        
        # Aplica o Delegate (Pílulas) na coluna Status (índice 4)
        self.table.setItemDelegateForColumn(4, StatusDelegate(self.table))
        
        self.table.doubleClicked.connect(self.open_edit_dialog)
        layout.addWidget(self.table)

        # Botões de Ação na Seleção
        self._setup_action_buttons(layout)


    def _setup_action_buttons(self, parent_layout):
        container = QFrame()
        container.setStyleSheet(f"background-color: {COLORS['white']}; border-radius: 8px; border: 1px solid {COLORS['border']};")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        def add_btn(text, icon, func, color="primary"):
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon, color=COLORS['dark']))
            btn.setStyleSheet(f"""
                QPushButton {{ background: transparent; border: none; padding: 8px 15px; color: {COLORS['dark']}; font-weight: 600; text-align: left; }}
                QPushButton:hover {{ background-color: {COLORS['light']}; border-radius: 4px; }}
            """)
            btn.clicked.connect(func)
            layout.addWidget(btn)
            return btn

        # Grupo Principal
        add_btn("Editar", 'fa5s.pen', self.open_edit_dialog)
        
        # Separador visual (opcional)
        line = QFrame(); line.setFrameShape(QFrame.Shape.VLine); line.setStyleSheet(f"color: {COLORS['border']}")
        layout.addWidget(line)

        # Acadêmico
        add_btn("Notas", 'fa5s.star', self.open_grades_dialog)
        add_btn("Boletim", 'fa5s.file-pdf', self.open_report)      # <--- VOLTOU
        add_btn("Observações", 'fa5s.eye', self.open_observations) # <--- VOLTOU
        
        # Gestão
        add_btn("Documentos", 'fa5s.folder-open', self.open_documents)
        add_btn("Reuniões", 'fa5s.calendar-alt', self.open_meetings)
        
        layout.addStretch()
        
        btn_del = QPushButton("Excluir")
        btn_del.setIcon(qta.icon('fa5s.trash-alt', color=COLORS['danger']))
        btn_del.setStyleSheet(f"color: {COLORS['danger']}; background: transparent; border: none; font-weight: bold;")
        btn_del.clicked.connect(self.delete_intern)
        layout.addWidget(btn_del)

        parent_layout.addWidget(container)

    # --- LÓGICA DE DADOS (Mantida Igual) ---
    def load_data(self):
        interns = self.service.get_all_interns()
        all_venues = self.venue_service.get_all()
        venue_map = {v.venue_id: v.venue_name for v in all_venues}
        
        self.table.setRowCount(0)
        for row, intern in enumerate(interns):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 50)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(intern.intern_id)))
            
            # Nome
            item_name = QTableWidgetItem(intern.name)
            item_name.setFont(self._get_bold_font())
            self.table.setItem(row, 1, item_name)
            
            # Local
            venue_name = venue_map.get(intern.venue_id, "-")
            self.table.setItem(row, 2, QTableWidgetItem(venue_name))
            
            # RA
            self.table.setItem(row, 3, QTableWidgetItem(intern.registration_number or "-"))
            
            # Status (Texto simples aqui, o Delegate desenha a pílula)
            self.table.setItem(row, 4, QTableWidgetItem(intern.status))

        if self.txt_search.text():
            self.filter_table(self.txt_search.text())

    def _get_bold_font(self):
        f = self.font()
        f.setBold(True)
        return f


    def filter_table(self, text):
        search_text = text.lower().strip()
        for row in range(self.table.rowCount()):
            item_name = self.table.item(row, 1)
            item_ra = self.table.item(row, 3)
            item_venue = self.table.item(row, 2)
            
            match = False
            if item_name and search_text in item_name.text().lower(): match = True
            if item_ra and search_text in item_ra.text().lower(): match = True
            if item_venue and search_text in item_venue.text().lower(): match = True
            
            self.table.setRowHidden(row, not match)

    def get_selected_intern(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno na tabela.")
            return None
        
        # CORREÇÃO 3: Verificação de segurança
        item_id = self.table.item(rows[0].row(), 0)
        if not item_id: 
            return None
            
        return self.service.get_by_id(int(item_id.text()))

    # --- Wrappers para Dialogs (Ajuste onde chamava refresh) ---
    def open_add_dialog(self):
        d = InternDialog(self, self.venue_service)
        if d.exec():
            try:
                new_intern = d.get_data()
                new_id = self.service.add_new_intern(new_intern)
                if new_id: self.doc_service.create_initial_documents_batch(new_id)
                self.load_data()
                self.page_dashboard.refresh_data()
                QMessageBox.information(self, "Sucesso", "Aluno cadastrado!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro: {e}")

    def open_edit_dialog(self):
        i = self.get_selected_intern()
        if not i: return
        d = InternDialog(self, self.venue_service, intern=i)
        if d.exec():
            try:
                new_data = d.get_data()
                
                # Atualizando objeto
                i.name = new_data.name
                i.venue_id = new_data.venue_id
                i.registration_number = new_data.registration_number
                i.email = new_data.email
                i.term = new_data.term
                # As datas controlam o status automaticamente
                i.start_date = new_data.start_date
                i.end_date = new_data.end_date
                
                # CORREÇÃO 1: REMOVIDO 'i.status = new_data.status'
                # O status é read-only (calculado via @property) no seu modelo Intern.
                
                self.service.update_intern(i)
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Erro", str(e))

    def delete_intern(self):
        i = self.get_selected_intern()
        if not i: return
        
        # CORREÇÃO 2: Enum StandardButton correto
        confirm = QMessageBox.question(
            self, 
            "Excluir", 
            f"Apagar {i.name}?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.service.delete_intern(i)
            self.load_data()
            self.page_dashboard.refresh_data()

    # Outros métodos de abertura de dialogs
    def open_grades_dialog(self):
        i = self.get_selected_intern()
        if i: GradeDialog(self, i, self.criteria_service, self.grade_service).exec()
    
    def open_documents(self):
        i = self.get_selected_intern()
        if i: 
            DocumentDialog(self, i, self.doc_service).exec()
            self.page_dashboard.refresh_data()

    def open_meetings(self):
        i = self.get_selected_intern()
        if i: 
            MeetingDialog(self, i, self.meeting_service).exec()
            self.page_dashboard.refresh_data()

    def open_settings(self):
        SettingsDialog(self).exec()

    def import_csv_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar CSV", "", "CSV (*.csv)")
        if path:
            try:
                self.import_service.read_file(path)
                self.load_data()
                self.page_dashboard.refresh_data()
                QMessageBox.information(self, "Sucesso", "Importação concluída.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))


# --- Métodos Restaurados/Confirmados ---

    def open_venue_manager(self):
        VenueManagerDialog(self, self.venue_service).exec()
        # Se afetar contagem do dashboard, atualiza
        self.page_dashboard.refresh_data()

    def open_criteria_manager(self):
        CriteriaManagerDialog(self, self.criteria_service).exec()

    def open_report(self):
        i = self.get_selected_intern()
        # Precisa passar todos os services que o ReportDialog exige
        if i: 
            ReportDialog(
                self, i, self.grade_service, self.criteria_service, 
                self.report_service, self.venue_service, 
                self.doc_service, self.meeting_service, self.obs_service
            ).exec()

    def open_observations(self):
        i = self.get_selected_intern()
        if i: ObservationDialog(self, i, self.obs_service).exec()


    def on_sidebar_changed(self, row):
            """Gerencia a navegação da Sidebar."""
            
            # Se for um item que apenas abre um Dialog (sem página própria na stack)
            if row == 2: # Item 2 = Locais
                self.open_venue_manager()
                # Truque visual: Mantém a seleção na página atual (ex: Alunos) 
                # em vez de ficar preso no item "Locais"
                self.sidebar_list.blockSignals(True)
                self.sidebar_list.setCurrentRow(self.content_stack.currentIndex())
                self.sidebar_list.blockSignals(False)
                return
                
            if row == 3: # Item 3 = Critérios
                self.open_criteria_manager()
                self.sidebar_list.blockSignals(True)
                self.sidebar_list.setCurrentRow(self.content_stack.currentIndex())
                self.sidebar_list.blockSignals(False)
                return

            # Navegação padrão (Dashboard ou Lista de Alunos)
            # Verifica se a página existe antes de mudar
            if row < self.content_stack.count():
                self.content_stack.setCurrentIndex(row)
                
                # Atualiza dados ao trocar
                if row == 0:
                    self.page_dashboard.refresh_data()
                elif row == 1:
                    self.load_data()