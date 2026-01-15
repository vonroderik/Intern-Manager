from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QLineEdit,
    QFrame,
    QMessageBox,
    QFileDialog,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
import qtawesome as qta

# Models & Services
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
from ui.dialogs.intern_dialog import InternDialog
from ui.dialogs.document_dialog import DocumentDialog

from ui.dialogs.grade_dialog import GradeDialog
from ui.dialogs.meeting_dialog import MeetingDialog
from ui.dialogs.observation_dialog import ObservationDialog
from ui.dialogs.report_dialog import ReportDialog
from ui.dialogs.settings_dialog import SettingsDialog

# Estilos e Componentes
from ui.styles import COLORS
from ui.dashboard_view import DashboardView
from ui.delegates import StatusDelegate
from ui.venue_view import VenueView
from ui.criteria_view import CriteriaView


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
        self.setMinimumSize(1280, 800)
        self.setWindowIcon(qta.icon("fa5s.notes-medical", color=COLORS["primary"]))

        # Estilo Global da Janela
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COLORS["light"]}; }}
            
            /* Tabela Estilizada */
            QTableWidget {{ 
                background-color: {COLORS["white"]}; 
                border-radius: 8px; 
                border: 1px solid {COLORS["border"]};
                gridline-color: transparent;
                outline: none;
                alternate-background-color: #FAFAFA;
            }}
            
            QHeaderView::section {{
                background-color: {COLORS["white"]};
                color: {COLORS["medium"]};
                padding: 12px;
                border: none;
                border-bottom: 2px solid {COLORS["light"]};
                font-weight: bold;
                text-transform: uppercase;
                font-size: 12px;
            }}
            
            QTableWidget::item:hover {{
                background-color: #E0E0E0;
                color: {COLORS["dark"]};
            }}
            
            QTableWidget::item:selected {{
                background-color: #BBDEFB;
                color: {COLORS["dark"]};
                border: none;
            }}
        """)

        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        # Container Principal
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

        # --- Páginas ---
        # Página 0: Dashboard
        self.page_dashboard = DashboardView(
            self.service, self.doc_service, self.meeting_service, self.venue_service
        )
        self.content_stack.addWidget(self.page_dashboard)

        # Página 1: Alunos (Lista)
        self.page_list = QWidget()
        self._setup_list_page()
        self.content_stack.addWidget(self.page_list)

        # Página 2: Locais
        self.page_venues = VenueView(self.venue_service)
        self.content_stack.addWidget(self.page_venues)

        # Página 3: Critérios
        self.page_criteria = CriteriaView(self.criteria_service)
        self.content_stack.addWidget(self.page_criteria)

        # Inicialização
        self.sidebar_list.currentRowChanged.connect(self.on_sidebar_changed)
        self.sidebar_list.setCurrentRow(0)

    def _setup_sidebar(self, parent_layout):
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(260)
        sidebar_frame.setStyleSheet(f"""
            QFrame {{ background-color: {COLORS["sidebar_bg"]}; border: none; }}
            QLabel {{ color: {COLORS["sidebar_text"]}; }}
        """)

        slayout = QVBoxLayout(sidebar_frame)
        slayout.setContentsMargins(0, 0, 0, 20)
        slayout.setSpacing(10)

        # Título App
        app_title = QLabel("InternManager")
        app_title.setStyleSheet(
            "font-size: 20px; font-weight: 900; padding: 30px 20px 5px 20px; letter-spacing: 1px;"
        )
        app_subtitle = QLabel("Pro 2026")
        app_subtitle.setStyleSheet(
            f"font-size: 12px; font-weight: normal; color: {COLORS['secondary']}; padding: 0 20px 30px 20px;"
        )

        slayout.addWidget(app_title)
        slayout.addWidget(app_subtitle)

        # Lista de Navegação
        self.sidebar_list = QListWidget()
        self.sidebar_list.setFrameShape(QFrame.Shape.NoFrame)
        self.sidebar_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sidebar_list.setStyleSheet(f"""
            QListWidget {{ background-color: transparent; outline: none; }}
            QListWidget::item {{
                color: #A0A0A0;
                padding: 15px 25px;
                border-left: 4px solid transparent;
                font-weight: 500;
                font-size: 14px;
            }}
            QListWidget::item:selected {{
                background-color: #2D2C2B;
                border-left: 4px solid {COLORS["primary"]};
                color: {COLORS["white"]};
                font-weight: bold;
            }}
            QListWidget::item:hover {{
                background-color: #2D2C2B;
                color: {COLORS["white"]};
            }}
        """)

        # Itens
        self.sidebar_list.addItem(
            QListWidgetItem(qta.icon("fa5s.chart-pie", color="white"), "  Dashboard")
        )
        self.sidebar_list.addItem(
            QListWidgetItem(qta.icon("fa5s.user-graduate", color="white"), "  Alunos")
        )
        self.sidebar_list.addItem(
            QListWidgetItem(qta.icon("fa5s.hospital", color="white"), "  Locais")
        )
        self.sidebar_list.addItem(
            QListWidgetItem(qta.icon("fa5s.tasks", color="white"), "  Critérios")
        )

        slayout.addWidget(self.sidebar_list)
        slayout.addStretch()

        # Rodapé Sidebar
        btn_settings = QPushButton(" Configurações")
        btn_settings.setIcon(qta.icon("fa5s.cog", color=COLORS["secondary"]))
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.setStyleSheet(f"""
            QPushButton {{ text-align: left; padding: 15px 25px; background: transparent; color: {COLORS["secondary"]}; border: none; font-weight: 600; }}
            QPushButton:hover {{ color: white; }}
        """)
        btn_settings.clicked.connect(self.open_settings)
        slayout.addWidget(btn_settings)

        parent_layout.addWidget(sidebar_frame)

    def _setup_list_page(self):
        layout = QVBoxLayout(self.page_list)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        lbl = QLabel("Gerenciar Alunos")
        lbl.setStyleSheet(
            f"font-size: 26px; font-weight: 800; color: {COLORS['dark']};"
        )
        header.addWidget(lbl)
        header.addStretch()

        self.btn_add = QPushButton(" Novo Aluno")
        self.btn_add.setIcon(qta.icon("fa5s.plus", color="white"))
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["primary"]}; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_add.clicked.connect(self.open_add_dialog)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        # Toolbar (Busca)
        actions = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍  Buscar por nome, RA ou local...")
        self.txt_search.setFixedWidth(400)
        self.txt_search.setStyleSheet(f"""
            QLineEdit {{ background-color: {COLORS["white"]}; border: 1px solid {COLORS["border"]}; border-radius: 6px; padding: 10px; color: {COLORS["dark"]}; }}
            QLineEdit:focus {{ border: 1px solid {COLORS["primary"]}; }}
        """)
        self.txt_search.textChanged.connect(self.filter_table)
        actions.addWidget(self.txt_search)
        actions.addStretch()

        btn_import = QPushButton(" Importar CSV")
        btn_import.setIcon(qta.icon("fa5s.file-import", color=COLORS["dark"]))
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["white"]}; border: 1px solid {COLORS["border"]}; padding: 8px 15px; border-radius: 6px; color: {COLORS["dark"]}; font-weight: 600; }}
            QPushButton:hover {{ background-color: {COLORS["light"]}; }}
        """)
        btn_import.clicked.connect(self.import_csv_dialog)
        actions.addWidget(btn_import)
        layout.addLayout(actions)

        # --- TABELA DE ALUNOS ---
        self.table = QTableWidget()

        # FIX DA PALETA (Para seleção ficar azul bonita)
        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#BBDEFB"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS["dark"]))
        self.table.setPalette(palette)

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nome Completo", "Local de Estágio", "RA", "Status"]
        )
        self.table.setColumnHidden(0, True)

        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setRowHeight(0, 50)

        # Delegate na coluna Status (4)
        self.table.setItemDelegateForColumn(4, StatusDelegate(self.table))
        self.table.doubleClicked.connect(self.open_edit_dialog)

        layout.addWidget(self.table)

        # Painel de Ações Inferior
        self._setup_action_panel(layout)

    def _setup_action_panel(self, parent_layout):
        container = QFrame()
        container.setStyleSheet(
            f"background-color: {COLORS['white']}; border-radius: 8px; border: 1px solid {COLORS['border']};"
        )
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        lbl = QLabel("Ações:")
        lbl.setStyleSheet(
            f"font-weight: bold; color: {COLORS['medium']}; margin-right: 10px;"
        )
        layout.addWidget(lbl)

        def make_btn(text, icon, func):
            b = QPushButton(text)
            b.setIcon(qta.icon(icon, color=COLORS["dark"]))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{ background-color: transparent; border: 1px solid {COLORS["border"]}; padding: 8px 15px; border-radius: 4px; color: {COLORS["dark"]}; font-weight: 600; }}
                QPushButton:hover {{ background-color: {COLORS["light"]}; border-color: {COLORS["medium"]}; }}
            """)
            b.clicked.connect(func)
            return b

        layout.addWidget(make_btn("Editar", "fa5s.pen", self.open_edit_dialog))
        layout.addWidget(make_btn("Notas", "fa5s.star", self.open_grades_dialog))
        layout.addWidget(make_btn("Boletim", "fa5s.file-pdf", self.open_report))
        layout.addWidget(make_btn("Docs", "fa5s.folder-open", self.open_documents))
        layout.addWidget(make_btn("Reuniões", "fa5s.calendar-alt", self.open_meetings))
        layout.addWidget(make_btn("Obs", "fa5s.eye", self.open_observations))

        layout.addStretch()

        btn_del = QPushButton(" Excluir Aluno")
        btn_del.setIcon(qta.icon("fa5s.trash-alt", color=COLORS["danger"]))
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; border: 1px solid #F5C6CB; padding: 8px 15px; border-radius: 4px; color: {COLORS["danger"]}; font-weight: 600; }}
            QPushButton:hover {{ background-color: #F8D7DA; }}
        """)
        btn_del.clicked.connect(self.delete_intern)
        layout.addWidget(btn_del)

        parent_layout.addWidget(container)

    # --- LÓGICA DE DADOS ---
    def load_data(self):
        interns = self.service.get_all_interns()
        all_venues = self.venue_service.get_all()
        venue_map = {v.venue_id: v.venue_name for v in all_venues}

        self.table.setRowCount(0)
        for row, intern in enumerate(interns):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 50)  # Altura confortável

            self.table.setItem(row, 0, QTableWidgetItem(str(intern.intern_id)))

            # Nome em Negrito
            name_item = QTableWidgetItem(intern.name)
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            self.table.setItem(row, 1, name_item)

            self.table.setItem(
                row, 2, QTableWidgetItem(venue_map.get(intern.venue_id, "-"))
            )
            self.table.setItem(
                row, 3, QTableWidgetItem(str(intern.registration_number or "-"))
            )
            self.table.setItem(row, 4, QTableWidgetItem(intern.status))

        if self.txt_search.text():
            self.filter_table(self.txt_search.text())

    def filter_table(self, text):
        search = text.lower().strip()
        for row in range(self.table.rowCount()):
            match = False
            for col in [1, 2, 3]:  # Nome, Local, RA
                item = self.table.item(row, col)
                if item and search in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def get_selected_intern(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno na tabela.")
            return None

        item_id = self.table.item(rows[0].row(), 0)
        if not item_id:
            return None
        return self.service.get_by_id(int(item_id.text()))

    # --- Wrappers de Dialogs ---
    def open_add_dialog(self):
        d = InternDialog(self, self.venue_service)
        if d.exec():
            try:
                new_id = self.service.add_new_intern(d.get_data())
                if new_id:
                    self.doc_service.create_initial_documents_batch(new_id)
                self.load_data()
                self.page_dashboard.refresh_data()
                QMessageBox.information(self, "Sucesso", "Aluno cadastrado!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro: {e}")

    def open_edit_dialog(self):
        i = self.get_selected_intern()
        if not i:
            return
        d = InternDialog(self, self.venue_service, intern=i)
        if d.exec():
            try:
                # Update seguro
                data = d.get_data()
                i.name = data.name
                i.venue_id = data.venue_id
                i.registration_number = data.registration_number
                i.email = data.email
                i.term = data.term
                i.start_date = data.start_date
                i.end_date = data.end_date
                i.working_days = data.working_days
                i.working_hours = data.working_hours

                self.service.update_intern(i)
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Erro", str(e))

    def delete_intern(self):
        i = self.get_selected_intern()
        if not i:
            return
        if (
            QMessageBox.question(
                self,
                "Excluir",
                f"Apagar {i.name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            self.service.delete_intern(i)
            self.load_data()
            self.page_dashboard.refresh_data()

    def open_grades_dialog(self):
        i = self.get_selected_intern()
        if i:
            GradeDialog(self, i, self.criteria_service, self.grade_service).exec()

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

    # --- Navegação ---

    def open_report(self):
        i = self.get_selected_intern()
        if i:
            ReportDialog(
                self,
                i,
                self.grade_service,
                self.criteria_service,
                self.report_service,
                self.venue_service,
                self.doc_service,
                self.meeting_service,
                self.obs_service,
            ).exec()

    def open_observations(self):
        i = self.get_selected_intern()
        if i:
            ObservationDialog(self, i, self.obs_service).exec()

    def on_sidebar_changed(self, row):
        # Apenas troca a página. Simples e limpo.
        if row < self.content_stack.count():
            self.content_stack.setCurrentIndex(row)

            # Atualização sob demanda (Lazy loading)
            if row == 0:  # Dashboard
                self.page_dashboard.refresh_data()
            elif row == 1:  # Alunos
                self.load_data()
            elif row == 2:  # Locais
                self.page_venues.refresh_data()
            elif row == 3:  # Critérios
                self.page_criteria.refresh_data()
