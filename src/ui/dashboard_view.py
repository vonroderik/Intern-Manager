from datetime import datetime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt
from ui.components.stat_card import StatCard

# Services
from services.intern_service import InternService
from services.document_service import DocumentService
from services.meeting_service import MeetingService
from services.venue_service import VenueService


class DashboardView(QWidget):
    def __init__(
        self,
        intern_service: InternService,
        doc_service: DocumentService,
        meeting_service: MeetingService,
        venue_service: VenueService,
    ):
        super().__init__()
        self.i_service = intern_service
        self.d_service = doc_service
        self.m_service = meeting_service
        self.v_service = venue_service

        self._setup_ui()
        self.refresh_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Título
        lbl_title = QLabel("Visão Geral")
        lbl_title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px;"
        )
        main_layout.addWidget(lbl_title)

        # --- Área de Cards (KPIs) ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.card_total = StatCard("Estagiários Ativos", "0", "#0078D7", "👥")
        self.card_docs = StatCard("Documentos Pendentes", "0", "#D32F2F", "⚠️")
        # MUDANÇA 1: Título do card agora especifica "Mês Atual"
        self.card_meetings = StatCard("Reuniões (Mês)", "0", "#2E7D32", "📅")
        self.card_venues = StatCard("Locais de Estágio", "0", "#E65100", "🏥")

        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_docs)
        cards_layout.addWidget(self.card_meetings)
        cards_layout.addWidget(self.card_venues)

        main_layout.addLayout(cards_layout)

        # --- Área de Detalhes / Alertas ---
        main_layout.addSpacing(30)

        lbl_alerts = QLabel("📢 Alertas e Pendências")
        lbl_alerts.setStyleSheet("font-size: 18px; font-weight: bold; color: #555;")
        main_layout.addWidget(lbl_alerts)

        # Scroll Area para os alertas não estourarem a tela
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.alert_frame = QFrame()
        self.alert_frame.setStyleSheet("""
            QFrame { background-color: transparent; }
            .WarningBox { 
                background-color: #FFF3CD; 
                border: 1px solid #FFEEBA; 
                border-radius: 5px; 
                padding: 10px; margin-bottom: 5px;
            }
            .InfoBox {
                background-color: #D1ECF1;
                border: 1px solid #BEE5EB;
                border-radius: 5px;
                padding: 10px; margin-bottom: 5px;
            }
        """)
        self.alert_layout = QVBoxLayout(self.alert_frame)
        self.alert_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.alert_frame)
        main_layout.addWidget(scroll)

    def refresh_data(self):
        """Recalcula os números do dashboard com lógica de negócio real."""

        interns = self.i_service.get_all_interns()
        self.card_total.update_value(str(len(interns)))

        venues = self.v_service.get_all()
        self.card_venues.update_value(str(len(venues)))

        # --- Lógica de Supervisão Inteligente ---
        all_meetings = self.m_service.repo.get_all()

        # Filtra: Quantas foram este mês?
        now = datetime.now()
        meetings_this_month = 0
        supervised_ids = set()

        for m in all_meetings:
            supervised_ids.add(m.intern_id)
            try:
                # Converte string ISO YYYY-MM-DD para data
                m_date = datetime.strptime(m.meeting_date, "%Y-%m-%d")
                if m_date.month == now.month and m_date.year == now.year:
                    meetings_this_month += 1
            except ValueError:
                pass  # Ignora datas mal formatadas

        self.card_meetings.update_value(str(meetings_this_month))

        # Contagem de Docs
        pending_docs = self.d_service.count_total_pending()
        self.card_docs.update_value(str(pending_docs))

        # Gera Alertas
        self._generate_alerts(interns, supervised_ids)

    def _generate_alerts(self, interns, supervised_ids):
        # Limpa alertas antigos
        while self.alert_layout.count():
            item = self.alert_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 1. Alerta de Alunos Fantasmas (Nunca supervisionados)
        unsupervised = [i for i in interns if i.intern_id not in supervised_ids]

        if unsupervised:
            # Cria um card de alerta agrupado
            names = ", ".join(
                [i.name.split()[0] for i in unsupervised[:10]]
            )  # Pega só o primeiro nome dos 5 primeiros
            remaining = len(unsupervised) - 10
            msg = f"⚠️ <b>{len(unsupervised)} Alunos nunca foram supervisionados!</b><br>Fique de olho em: {names}"
            if remaining > 0:
                msg += f" e mais {remaining}..."

            lbl = QLabel(msg)
            lbl.setProperty("class", "WarningBox")  # Para pegar o CSS
            lbl.setTextFormat(Qt.TextFormat.RichText)
            lbl.setWordWrap(True)
            self.alert_layout.addWidget(lbl)

        # 2. Alerta de RA
        no_ra = [i for i in interns if not i.registration_number]
        if no_ra:
            lbl = QLabel(
                f"⚠️ Existem {len(no_ra)} alunos sem matrícula (RA) cadastrada."
            )
            lbl.setProperty("class", "WarningBox")
            self.alert_layout.addWidget(lbl)

        # 3. Mensagem de Bom trabalho se tudo estiver limpo
        if not unsupervised and not no_ra and interns:
            lbl = QLabel(
                "✅ Tudo em dia! Todos os alunos ativos já participaram das reuniões."
            )
            lbl.setProperty("class", "InfoBox")
            self.alert_layout.addWidget(lbl)
