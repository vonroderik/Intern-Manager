from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea
)
# CORREÇÃO 1: QSize adicionado
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from ui.styles import COLORS
# Certifique-se de que existe um __init__.py em src/ui/components/
from ui.components.metric_card import MetricCard

class DashboardView(QWidget):
    def __init__(self, intern_service, doc_service, meeting_service, venue_service):
        super().__init__()
        self.i_service = intern_service
        self.d_service = doc_service
        self.m_service = meeting_service
        self.v_service = venue_service
        
        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        # ... (código anterior mantido até a parte dos alertas) ...
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Visão Geral do Semestre")
        title.setStyleSheet(f"font-size: 26px; font-weight: 800; color: {COLORS['dark']};")
        subtitle = QLabel("Monitore o progresso e pendências dos alunos.")
        subtitle.setStyleSheet(f"font-size: 14px; color: {COLORS['medium']};")
        
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        
        btn_refresh = QPushButton(" Atualizar Dados")
        btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color="white"))
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(f"background-color: {COLORS['primary']}; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold; border: none;")
        btn_refresh.clicked.connect(self.refresh_data)

        header.addLayout(title_box)
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

        # Alertas
        lbl_alerts = QLabel("📢 Atenção Necessária")
        lbl_alerts.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['dark']}; margin-top: 10px;")
        layout.addWidget(lbl_alerts)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        self.alert_container = QWidget()
        self.alert_container.setStyleSheet("background-color: transparent;")
        self.alert_layout = QVBoxLayout(self.alert_container)
        self.alert_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.alert_layout.setSpacing(10)

        scroll.setWidget(self.alert_container)
        layout.addWidget(scroll)

    def refresh_data(self):
        interns = self.i_service.get_all_interns()
        venues = self.v_service.get_all()
        pending_docs = self.d_service.count_total_pending()
        all_meetings = self.m_service.repo.get_all()

        now = datetime.now()
        meetings_this_month = 0
        supervised_ids = set()

        for m in all_meetings:
            supervised_ids.add(m.intern_id)
            try:
                m_date = datetime.strptime(m.meeting_date, "%Y-%m-%d")
                if m_date.month == now.month and m_date.year == now.year:
                    meetings_this_month += 1
            except:
                pass

        self.card_total.set_value(len(interns))
        self.card_venues.set_value(len(venues))
        self.card_docs.set_value(pending_docs)
        self.card_meetings.set_value(meetings_this_month)

        self._generate_alerts(interns, supervised_ids)

    def _generate_alerts(self, interns, supervised_ids):
        while self.alert_layout.count():
            item = self.alert_layout.takeAt(0)
            # CORREÇÃO 2: Verificação segura para evitar erro em 'None'
            widget = item.widget()
            if widget:
                widget.deleteLater()

        def add_alert_widget(text, type="warning"):
            frame = QFrame()
            if type == "warning":
                bg, border, icon, text_col = "#FFF4CE", "#FFD700", "fa5s.exclamation-triangle", "#664d03"
            elif type == "danger":
                bg, border, icon, text_col = "#F8D7DA", "#F5C6CB", "fa5s.times-circle", "#721c24"
            else:
                bg, border, icon, text_col = "#D1E7DD", "#BADBCC", "fa5s.check-circle", "#0f5132"

            frame.setStyleSheet(f"QFrame {{ background-color: {bg}; border: 1px solid {border}; border-radius: 6px; }}")
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(15, 10, 15, 10)
            
            # CORREÇÃO 1: Uso de QSize corrigido aqui
            lbl_icon = QLabel()
            lbl_icon.setPixmap(qta.icon(icon, color=text_col).pixmap(QSize(20, 20)))
            
            lbl_text = QLabel(text)
            lbl_text.setWordWrap(True)
            lbl_text.setStyleSheet(f"color: {text_col}; font-weight: 500; border: none;")
            
            fl.addWidget(lbl_icon)
            fl.addWidget(lbl_text, 1)
            self.alert_layout.addWidget(frame)

        unsupervised = [i for i in interns if i.intern_id not in supervised_ids]
        if unsupervised:
            names = ", ".join([i.name.split()[0] for i in unsupervised[:5]])
            rest = len(unsupervised) - 5
            msg = f"<b>{len(unsupervised)} Alunos nunca foram supervisionados!</b><br>Verifique: {names}"
            if rest > 0: msg += f" e mais {rest}..."
            add_alert_widget(msg, "warning")

        no_ra = [i for i in interns if not i.registration_number]
        if no_ra:
            add_alert_widget(f"Existem <b>{len(no_ra)} alunos</b> sem matrícula (RA).", "danger")

        if not unsupervised and not no_ra and interns:
            add_alert_widget("Tudo em dia! Todos os alunos ativos estão sendo supervisionados.", "success")