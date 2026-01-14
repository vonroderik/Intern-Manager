import sys
import os
import shutil
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QLineEdit, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QAction

# --- BIBLIOTECA DE ÍCONES ---
import qtawesome as qta

# Config
from config import DB_PATH

# Models
from core.models.intern import Intern

# Services (Tipagem para o Python não reclamar)
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
from ui.dialogs.venue_manager_dialog import VenueManagerDialog
from ui.dialogs.criteria_manager_dialog import CriteriaManagerDialog
from ui.dialogs.grade_dialog import GradeDialog
from ui.dialogs.meeting_dialog import MeetingDialog
from ui.dialogs.observation_dialog import ObservationDialog
from ui.dialogs.report_dialog import ReportDialog
from ui.dialogs.settings_dialog import SettingsDialog

# --- PALETA DE CORES MODERNA ---
COLORS = {
    "primary": "#005A9E",    # Azul corporativo
    "primary_hover": "#004C87",
    "secondary": "#6C757D",  # Cinza neutro
    "success": "#107C10",    # Verde
    "warning": "#FFC107",    # Amarelo
    "danger": "#D13438",     # Vermelho
    "dark": "#323130",       # Texto escuro
    "medium": "#605E5C",     # Texto médio
    "light": "#F3F2F1",      # Fundo claro
    "white": "#FFFFFF",
    "border": "#E1DFDD"
}

# --- ESTILOS GERAIS ---
STYLESHEET = f"""
    QMainWindow {{
        background-color: {COLORS["white"]};
    }}
    QTabWidget::pane {{
        border: 1px solid {COLORS["border"]};
        border-top: 2px solid {COLORS["primary"]};
        background-color: {COLORS["white"]};
    }}
    QTabBar::tab {{
        background: {COLORS["light"]};
        color: {COLORS["medium"]};
        padding: 10px 15px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {COLORS["white"]};
        color: {COLORS["primary"]};
        font-weight: bold;
    }}
    QTableWidget {{
        border: 1px solid {COLORS["border"]};
        gridline-color: {COLORS["light"]};
        selection-background-color: {COLORS["primary"]};
        selection-color: {COLORS["white"]};
    }}
    QHeaderView::section {{
        background-color: {COLORS["light"]};
        color: {COLORS["dark"]};
        padding: 6px;
        border: none;
        border-bottom: 2px solid {COLORS["border"]};
        font-weight: bold;
    }}
    QLineEdit, QComboBox {{
        border: 1px solid {COLORS["border"]};
        padding: 6px;
        border-radius: 4px;
        color: {COLORS["dark"]};
    }}
    QLineEdit:focus {{
        border: 2px solid {COLORS["primary"]};
    }}
"""

class MetricCard(QFrame):
    """Card Visual para o Dashboard."""
    def __init__(self, title, value, icon_name, color_key="primary"):
        super().__init__()
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {COLORS["white"]};
                border-radius: 8px;
                border: 1px solid {COLORS["border"]};
            }}
        """)
        
        # Sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Ícone
        lbl_icon = QLabel()
        icon = qta.icon(icon_name, color=COLORS[color_key])
        lbl_icon.setPixmap(icon.pixmap(QSize(48, 48)))
        layout.addWidget(lbl_icon)

        # Textos
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet(f"color: {COLORS['medium']}; font-size: 12px; font-weight: bold;")
        
        lbl_value = QLabel(str(value))
        lbl_value.setStyleSheet(f"color: {COLORS['dark']}; font-size: 28px; font-weight: 900;")
        
        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_value)
        layout.addLayout(text_layout)
        layout.addStretch()

class DashboardView(QWidget):
    """Aba de Dashboard (Refatorada)."""
    def __init__(self, intern_service, doc_service, meeting_service, venue_service):
        super().__init__()
        self.i_service = intern_service
        self.d_service = doc_service
        self.m_service = meeting_service
        self.v_service = venue_service
        self._setup_ui()
        self.refresh_data() # Mantendo nome original

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Cabeçalho
        header = QHBoxLayout()
        title = QLabel("Visão Geral do Semestre")
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COLORS['dark']};")
        
        btn_refresh = QPushButton("Atualizar")
        btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color="white"))
        btn_refresh.setStyleSheet(f"background-color: {COLORS['secondary']}; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold;")
        btn_refresh.clicked.connect(self.refresh_data)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_refresh)
        layout.addLayout(header)

        # Cards
        cards_layout = QHBoxLayout()
        self.card_total = MetricCard("Total Alunos", "0", 'fa5s.user-graduate', 'primary')
        self.card_docs = MetricCard("Docs Pendentes", "0", 'fa5s.file-contract', 'danger')
        self.card_meetings = MetricCard("Reuniões (Mês)", "0", 'fa5s.calendar-check', 'success')
        self.card_venues = MetricCard("Locais Ativos", "0", 'fa5s.hospital', 'warning')

        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_docs)
        cards_layout.addWidget(self.card_meetings)
        cards_layout.addWidget(self.card_venues)
        layout.addLayout(cards_layout)

        # Área Inferior (Exemplo de lista rápida)
        layout.addStretch()

    def refresh_data(self):
        """Recarrega os números usando os Services."""
        # 1. Total Alunos
        interns = self.i_service.get_all_interns()
        self._update_card(self.card_total, str(len(interns)))

        # 2. Locais
        venues = self.v_service.get_all()
        self._update_card(self.card_venues, str(len(venues)))

        # 3. Docs Pendentes
        pending = self.d_service.count_total_pending()
        self._update_card(self.card_docs, str(pending))

        # 4. Reuniões (Mês Atual)
        all_meetings = self.m_service.repo.get_all()
        now = datetime.now()
        count_month = sum(
            1 for m in all_meetings 
            if datetime.strptime(m.meeting_date, "%Y-%m-%d").month == now.month
        )
        self._update_card(self.card_meetings, str(count_month))

    def _update_card(self, card, value):
        # Navega na hierarquia do layout para achar o QLabel do valor
        # Layout -> Layout de Texto -> Label Valor (item 1)
        try:
            label = card.layout().itemAt(1).layout().itemAt(1).widget()
            label.setText(str(value))
        except:
            pass

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

        self.setWindowTitle("InternManager Pro 2026")
        self.setMinimumSize(1100, 700)
        self.setWindowIcon(qta.icon('fa5s.notes-medical', color=COLORS["primary"]))
        self.setStyleSheet(STYLESHEET)

        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        # Menu
        self._create_menu_bar()

        # Corpo
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Abas
        self.tabs = QTabWidget()
        self.tabs.setIconSize(QSize(20, 20))

        # Aba 1: Dashboard
        self.tab_dashboard = DashboardView(
            self.service, self.doc_service, self.meeting_service, self.venue_service
        )
        self.tabs.addTab(self.tab_dashboard, qta.icon('fa5s.chart-line', color=COLORS["primary"]), "Visão Geral")

        # Aba 2: Lista
        self.tab_list = QWidget()
        self._setup_list_tab()
        self.tabs.addTab(self.tab_list, qta.icon('fa5s.users', color=COLORS["primary"]), "Gerenciar Estagiários")
        
        # Eventos
        self.tabs.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tabs)

    def _create_menu_bar(self):
        menu = self.menuBar()
        
        # Arquivo
        file_menu = menu.addMenu("Arquivo")
        
        act_import = QAction(qta.icon('fa5s.file-import', color="black"), "Importar CSV...", self)
        act_import.triggered.connect(self.import_csv_dialog)
        file_menu.addAction(act_import)

        act_backup = QAction(qta.icon('fa5s.save', color="black"), "Fazer Backup...", self)
        act_backup.triggered.connect(self.backup_database)
        file_menu.addAction(act_backup)
        
        file_menu.addSeparator()
        
        act_settings = QAction(qta.icon('fa5s.cog', color="black"), "Configurações", self)
        act_settings.triggered.connect(self.open_settings)
        file_menu.addAction(act_settings)

    def _setup_list_tab(self):
        layout = QVBoxLayout(self.tab_list)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Topo: Busca e Novo
        top_bar = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Buscar por nome ou RA...")
        self.txt_search.setFixedWidth(350)
        self.txt_search.textChanged.connect(self.filter_table)
        
        self.btn_add = QPushButton("Novo Aluno")
        self.btn_add.setIcon(qta.icon('fa5s.plus', color="white"))
        self.btn_add.setStyleSheet(f"background-color: {COLORS['primary']}; color: white; border: none; padding: 10px 20px; border-radius: 4px; font-weight: bold;")
        self.btn_add.clicked.connect(self.open_add_dialog)

        top_bar.addWidget(self.txt_search)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_add)
        layout.addLayout(top_bar)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nome Completo", "Local", "RA", "Status"])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(f"alternate-background-color: {COLORS['light']};")
        self.table.doubleClicked.connect(self.open_edit_dialog)
        
        layout.addWidget(self.table)

        # Botões de Ação Inferiores
        actions_layout = QHBoxLayout()
        
        # Helper para criar botões secundários
        def create_sec_btn(text, icon_name, color_key="primary", callback=None):
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon_name, color=COLORS[color_key]))
            btn.setStyleSheet(f"""
                QPushButton {{ background-color: {COLORS["white"]}; color: {COLORS["dark"]}; border: 1px solid {COLORS["border"]}; padding: 8px 12px; border-radius: 4px; }}
                QPushButton:hover {{ background-color: {COLORS["light"]}; border-color: {COLORS[color_key]}; }}
            """)
            if callback: btn.clicked.connect(callback)
            return btn

        # Grupo 1: Edição
        actions_layout.addWidget(create_sec_btn("Editar", 'fa5s.pen', 'primary', self.open_edit_dialog))
        actions_layout.addWidget(create_sec_btn("Excluir", 'fa5s.trash', 'danger', self.delete_intern))
        
        actions_layout.addWidget(self._create_v_line())
        
        # Grupo 2: Acadêmico
        actions_layout.addWidget(create_sec_btn("Notas", 'fa5s.chart-bar', 'primary', self.open_grades_dialog))
        actions_layout.addWidget(create_sec_btn("Boletim", 'fa5s.file-pdf', 'danger', self.open_report))
        actions_layout.addWidget(create_sec_btn("Critérios", 'fa5s.tasks', 'medium', self.open_criteria_manager))

        actions_layout.addWidget(self._create_v_line())
        
        # Grupo 3: Gestão
        actions_layout.addWidget(create_sec_btn("Documentos", 'fa5s.folder', 'warning', self.open_documents))
        actions_layout.addWidget(create_sec_btn("Reuniões", 'fa5s.calendar', 'success', self.open_meetings))
        actions_layout.addWidget(create_sec_btn("Locais", 'fa5s.hospital', 'success', self.open_venue_manager))

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

    def _create_v_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"color: {COLORS['border']}")
        return line

    def on_tab_changed(self, index):
        if index == 0: self.tab_dashboard.refresh_data()
        elif index == 1: self.load_data()

    # --- LÓGICA DE DADOS (Restaurada da original) ---
    def load_data(self):
        interns = self.service.get_all_interns()
        all_venues = self.venue_service.get_all()
        venue_map = {v.venue_id: v.venue_name for v in all_venues}
        
        self.table.setRowCount(0)
        for row, intern in enumerate(interns):
            self.table.insertRow(row)
            
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(intern.intern_id)))
            
            # Nome com ícone
            item_name = QTableWidgetItem(intern.name)
            item_name.setIcon(qta.icon('fa5s.user', color=COLORS["secondary"]))
            self.table.setItem(row, 1, item_name)
            
            # Local
            venue_name = venue_map.get(intern.venue_id, "-")
            self.table.setItem(row, 2, QTableWidgetItem(venue_name))
            
            # RA
            self.table.setItem(row, 3, QTableWidgetItem(intern.registration_number or ""))
            
            # Status Colorido
            status = intern.status
            item_status = QTableWidgetItem(status)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if status == "Concluído":
                item_status.setForeground(QColor(COLORS["success"]))
                item_status.setIcon(qta.icon('fa5s.check', color=COLORS["success"]))
            
            self.table.setItem(row, 4, item_status)

        if self.txt_search.text():
            self.filter_table(self.txt_search.text())

    def filter_table(self, text):
        search_text = text.lower().strip()
        for row in range(self.table.rowCount()):
            item_name = self.table.item(row, 1)
            item_ra = self.table.item(row, 3) # RA agora é coluna 3
            
            name_val = item_name.text().lower() if item_name else ""
            ra_val = item_ra.text().lower() if item_ra else ""
            
            match = search_text in name_val or search_text in ra_val
            self.table.setRowHidden(row, not match)

    def get_selected_intern(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "Atenção", "Selecione um aluno na tabela.")
            return None
        
        item_id = self.table.item(rows[0].row(), 0)
        if not item_id: return None
        
        return self.service.get_by_id(int(item_id.text()))

    # --- DIALOGS (Restaurados da original) ---
    def open_add_dialog(self):
        d = InternDialog(self, self.venue_service)
        if d.exec():
            try:
                new_intern = d.get_data()
                new_id = self.service.add_new_intern(new_intern)
                if new_id:
                    self.doc_service.create_initial_documents_batch(new_id)
                self.load_data()
                self.tab_dashboard.refresh_data()
                QMessageBox.information(self, "Sucesso", "Aluno cadastrado!")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Erro ao salvar: {e}")

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
                i.start_date = new_data.start_date
                i.end_date = new_data.end_date
                
                self.service.update_intern(i)
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self, "Erro", str(e))

    def delete_intern(self):
        i = self.get_selected_intern()
        if not i: return
        confirm = QMessageBox.question(self, "Excluir", f"Apagar {i.name}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.service.delete_intern(i)
            self.load_data()
            self.tab_dashboard.refresh_data()

    # Outros Dialogs simples
    def open_grades_dialog(self):
        i = self.get_selected_intern()
        if i: GradeDialog(self, i, self.criteria_service, self.grade_service).exec()

    def open_report(self):
        i = self.get_selected_intern()
        if i: ReportDialog(self, i, self.grade_service, self.criteria_service, self.report_service, self.venue_service, self.doc_service, self.meeting_service, self.obs_service).exec()

    def open_venue_manager(self):
        VenueManagerDialog(self, self.venue_service).exec()

    def open_criteria_manager(self):
        CriteriaManagerDialog(self, self.criteria_service).exec()

    def open_observations(self):
        i = self.get_selected_intern()
        if i: ObservationDialog(self, i, self.obs_service).exec()

    def open_documents(self):
        i = self.get_selected_intern()
        if i: DocumentDialog(self, i, self.doc_service).exec()
        self.tab_dashboard.refresh_data()

    def open_meetings(self):
        i = self.get_selected_intern()
        if i: MeetingDialog(self, i, self.meeting_service).exec()
        self.tab_dashboard.refresh_data()

    def open_settings(self):
        SettingsDialog(self).exec()

    def backup_database(self):
        filename = f"backup_interns_{datetime.now():%Y-%m-%d_%H%M}.db"
        path, _ = QFileDialog.getSaveFileName(self, "Backup", filename, "SQLite DB (*.db)")
        if path:
            shutil.copy(DB_PATH, path)
            QMessageBox.information(self, "Backup", "Sucesso!")

    def import_csv_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar CSV", "", "CSV (*.csv)")
        if path:
            try:
                self.import_service.read_file(path)
                self.load_data()
                self.tab_dashboard.refresh_data()
                QMessageBox.information(self, "Sucesso", "Importação concluída.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))