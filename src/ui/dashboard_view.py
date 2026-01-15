from datetime import datetime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
import qtawesome as qta

from ui.styles import COLORS


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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # --- Cabeçalho ---
        header = QHBoxLayout()

        # Textos
        title_box = QVBoxLayout()
        title = QLabel("Visão Geral")
        title.setStyleSheet(
            f"font-size: 28px; font-weight: 800; color: {COLORS['dark']};"
        )
        subtitle = QLabel("Acompanhamento em tempo real do semestre.")
        subtitle.setStyleSheet(f"font-size: 14px; color: {COLORS['secondary']};")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        # Botão Atualizar
        btn_refresh = QPushButton(" Atualizar")
        btn_refresh.setIcon(qta.icon("fa5s.sync-alt", color="white"))
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none; 
                padding: 10px 20px; border-radius: 6px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        btn_refresh.clicked.connect(self.refresh_data)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(btn_refresh)
        layout.addLayout(header)

        # --- Cards de Métricas ---
        self.cards_container = QHBoxLayout()
        self.cards_container.setSpacing(20)
        layout.addLayout(self.cards_container)

        # Inicializa os widgets dos cards (serão atualizados no refresh)
        self.card_total = self._create_card_widget(
            "Total Alunos", "fa5s.user-graduate", COLORS["primary"]
        )
        self.card_docs = self._create_card_widget(
            "Docs Pendentes", "fa5s.file-contract", COLORS["danger"]
        )
        self.card_meetings = self._create_card_widget(
            "Reuniões (Mês)", "fa5s.calendar-check", COLORS["success"]
        )
        self.card_venues = self._create_card_widget(
            "Locais Ativos", "fa5s.hospital", COLORS["warning"]
        )

        self.cards_container.addWidget(self.card_total)
        self.cards_container.addWidget(self.card_docs)
        self.cards_container.addWidget(self.card_meetings)
        self.cards_container.addWidget(self.card_venues)

        # --- Seção de Alertas ---
        lbl_alerts = QLabel("📢  Mural de Avisos")
        lbl_alerts.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {COLORS['dark']}; margin-top: 10px;"
        )
        layout.addWidget(lbl_alerts)

        # Área de Scroll para Alertas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        self.alert_container = QWidget()
        self.alert_container.setStyleSheet("background-color: transparent;")
        self.alert_layout = QVBoxLayout(self.alert_container)
        self.alert_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.alert_layout.setSpacing(10)
        self.alert_layout.setContentsMargins(0, 0, 5, 0)  # Margem direita pro scrollbar

        scroll.setWidget(self.alert_container)
        layout.addWidget(scroll)

    def _create_card_widget(self, title, icon_name, color_hex):
        """Cria um Card visual bonito com sombra."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["white"]};
                border-radius: 12px;
                border: 1px solid {COLORS["border"]};
            }}
        """)
        # Sombra suave
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        frame.setGraphicsEffect(shadow)
        frame.setMinimumHeight(110)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)

        # Icone
        lbl_icon = QLabel()
        lbl_icon.setPixmap(qta.icon(icon_name, color=color_hex).pixmap(QSize(40, 40)))
        lbl_icon.setStyleSheet("border: none; background: transparent;")

        # Textos
        vbox = QVBoxLayout()
        vbox.setSpacing(5)
        lbl_val = QLabel("0")  # Valor placeholder
        lbl_val.setObjectName("value_label")  # Tag para buscar depois
        lbl_val.setStyleSheet(
            f"font-size: 28px; font-weight: 800; color: {COLORS['dark']}; border: none; background: transparent;"
        )

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: {COLORS['secondary']}; border: none; background: transparent; text-transform: uppercase;"
        )

        vbox.addWidget(lbl_val)
        vbox.addWidget(lbl_title)

        layout.addLayout(vbox)
        layout.addStretch()
        layout.addWidget(lbl_icon)

        return frame

    def _update_card_value(self, card_widget, value):
        """Busca o label de valor dentro do card e atualiza."""
        lbl = card_widget.findChild(QLabel, "value_label")
        if lbl:
            lbl.setText(str(value))

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
            except Exception:
                pass

        # Atualiza os valores visuais
        self._update_card_value(self.card_total, len(interns))
        self._update_card_value(self.card_docs, pending_docs)
        self._update_card_value(self.card_meetings, meetings_this_month)
        self._update_card_value(self.card_venues, len(venues))

        self._generate_alerts(interns, supervised_ids)

    def _generate_alerts(self, interns, supervised_ids):
        # CORREÇÃO PYLANCE: Uso de variável auxiliar
        while self.alert_layout.count():
            item = self.alert_layout.takeAt(0)
            if not item:
                continue

            widget = item.widget()
            if widget:
                widget.deleteLater()

        def add_alert(text, style="info"):
            frame = QFrame()
            # Estilos de alerta baseados no Bootstrap
            styles = {
                "warning": (
                    "#FFF3CD",
                    "#FFECB5",
                    "#664D03",
                    "fa5s.exclamation-triangle",
                ),
                "danger": ("#F8D7DA", "#F5C6CB", "#721C24", "fa5s.times-circle"),
                "success": ("#D1E7DD", "#BADBCC", "#0F5132", "fa5s.check-circle"),
                "info": ("#CFF4FC", "#B6EFFB", "#055160", "fa5s.info-circle"),
            }
            bg, border, text_color, icon = styles.get(style, styles["info"])

            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg};
                    border: 1px solid {border};
                    border-radius: 8px;
                }}
            """)
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(15, 12, 15, 12)

            lbl_icon = QLabel()
            lbl_icon.setPixmap(qta.icon(icon, color=text_color).pixmap(QSize(20, 20)))
            lbl_icon.setStyleSheet("border: none;")

            lbl_text = QLabel(text)
            lbl_text.setWordWrap(True)
            lbl_text.setStyleSheet(
                f"color: {text_color}; font-weight: 500; border: none; font-size: 13px;"
            )

            fl.addWidget(lbl_icon)
            fl.addWidget(lbl_text, 1)
            self.alert_layout.addWidget(frame)

        # Lógica de Alertas
        unsupervised = [i for i in interns if i.intern_id not in supervised_ids]
        if unsupervised:
            count = len(unsupervised)
            names = ", ".join([i.name.split()[0] for i in unsupervised[:3]])
            suffix = f" e mais {count - 3}..." if count > 3 else "."
            msg = f"<b>{count} Alunos nunca tiveram supervisão!</b> (Prioridade)<br>Verificar: {names}{suffix}"
            add_alert(msg, "warning")

        no_ra = [i for i in interns if not i.registration_number]
        if no_ra:
            add_alert(
                f"Existem <b>{len(no_ra)} alunos</b> com cadastro incompleto (Sem RA).",
                "danger",
            )

        # Se não houver problemas
        if not unsupervised and not no_ra and interns:
            add_alert(
                "Excelente! Todos os alunos ativos estão sendo supervisionados e possuem cadastro completo.",
                "success",
            )
        elif not interns:
            add_alert(
                "Bem-vindo! Comece cadastrando um novo aluno na aba lateral.", "info"
            )
