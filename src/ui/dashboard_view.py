from typing import Optional
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QGraphicsDropShadowEffect,
    QSizePolicy, QComboBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
import qtawesome as qta

# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from ui.styles import COLORS

class ChartWidget(QFrame):
    """Widget personalizado para gráficos, com tipagem explícita para o Pylance."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure: Optional[Figure] = None
        self.canvas: Optional[FigureCanvas] = None

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

        # --- Header ---
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Monitoramento de Estágio")
        title.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {COLORS['dark']};")
        subtitle = QLabel("Status de alocação e conformidade documental.")
        subtitle.setStyleSheet(f"font-size: 14px; color: {COLORS['secondary']};")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        
        btn_refresh = QPushButton(" Atualizar Dados")
        btn_refresh.setIcon(qta.icon("fa5s.sync-alt", color="white"))
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']}; color: white; border: none; 
                padding: 10px 20px; border-radius: 6px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        btn_refresh.clicked.connect(self.refresh_data)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(btn_refresh)
        layout.addLayout(header)

        # --- Cards Superiores ---
        self.cards_container = QHBoxLayout()
        self.cards_container.setSpacing(20)
        layout.addLayout(self.cards_container)
        
        self.card_total = self._create_card_widget("Total Alunos", "fa5s.user-graduate", COLORS['primary'])
        self.card_no_venue = self._create_card_widget("Sem Local", "fa5s.map-marker-alt", COLORS['danger'])
        self.card_pending = self._create_card_widget("Documentos Pendentes", "fa5s.file-contract", COLORS['warning'])
        self.card_meetings = self._create_card_widget("Reuniões (Mês)", "fa5s.calendar-check", COLORS['success'])

        self.cards_container.addWidget(self.card_total)
        self.cards_container.addWidget(self.card_no_venue)
        self.cards_container.addWidget(self.card_pending)
        self.cards_container.addWidget(self.card_meetings)

        # --- Área de Gráficos (Split 50/50) ---
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        # Gráfico 1: Vínculos (Pizza)
        self.chart1_frame = self._create_chart_frame("Distribuição de Locais")
        charts_layout.addWidget(self.chart1_frame)

        # Gráfico 2: Documentação (Barras com Filtro)
        doc_container = QFrame()
        doc_container.setStyleSheet(f"background-color: {COLORS['white']}; border-radius: 12px; border: 1px solid {COLORS['border']};")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15); shadow.setColor(QColor(0, 0, 0, 20)); shadow.setOffset(0, 2)
        doc_container.setGraphicsEffect(shadow)
        
        doc_layout = QVBoxLayout(doc_container)
        doc_layout.setContentsMargins(10, 15, 10, 5)

        # Header do Gráfico 2
        doc_header = QHBoxLayout()
        lbl_doc = QLabel("Status Documental")
        lbl_doc.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['dark']}; border: none;")
        
        self.combo_doc_filter = QComboBox()
        
        # --- LISTA ATUALIZADA COM OS SEUS DOCUMENTOS REAIS ---
        doc_types = [
            "Todos", 
            "Contrato de Estágio",        # <--- Agora bate com o banco
            "Ficha de Frequência",
            "Diário de Campo", 
            "Projeto de Intervenção", 
            "Avaliação do Supervisor Local" # Agrupa Física e Carreiras
        ]
        # -----------------------------------------------------
        
        self.combo_doc_filter.addItems(doc_types)
        self.combo_doc_filter.setCurrentIndex(1) # Padrão: Contrato de Estágio
        self.combo_doc_filter.setFixedWidth(200) # Aumentei um pouco pra caber nomes longos
        self.combo_doc_filter.currentTextChanged.connect(self.refresh_data)

        doc_header.addWidget(lbl_doc)
        doc_header.addStretch()
        doc_header.addWidget(self.combo_doc_filter)
        doc_layout.addLayout(doc_header)

        # Canvas do Gráfico 2
        self.fig_docs = Figure(figsize=(4, 3), dpi=100)
        self.fig_docs.patch.set_facecolor('none')
        self.canvas_docs = FigureCanvas(self.fig_docs)
        self.canvas_docs.setStyleSheet("background-color: transparent;")
        doc_layout.addWidget(self.canvas_docs)

        charts_layout.addWidget(doc_container)
        layout.addLayout(charts_layout, stretch=1)

    def _create_card_widget(self, title, icon_name, color_hex):
        frame = QFrame()
        frame.setStyleSheet(f"QFrame {{ background-color: {COLORS['white']}; border-radius: 12px; border: 1px solid {COLORS['border']}; }}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setColor(QColor(0, 0, 0, 30)); shadow.setOffset(0, 4)
        frame.setGraphicsEffect(shadow)
        frame.setMinimumHeight(100)
        frame.setMaximumHeight(120)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)

        lbl_icon = QLabel()
        lbl_icon.setPixmap(qta.icon(icon_name, color=color_hex).pixmap(QSize(36, 36)))
        lbl_icon.setStyleSheet("border: none; background: transparent;")
        
        vbox = QVBoxLayout()
        vbox.setSpacing(2)
        lbl_val = QLabel("0")
        lbl_val.setObjectName("value_label")
        lbl_val.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {COLORS['dark']}; border: none; background: transparent;")
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLORS['secondary']}; border: none; background: transparent; text-transform: uppercase;")
        
        vbox.addWidget(lbl_val)
        vbox.addWidget(lbl_title)
        
        layout.addLayout(vbox)
        layout.addStretch()
        layout.addWidget(lbl_icon)
        return frame

    def _create_chart_frame(self, title):
        frame = ChartWidget()
        frame.setStyleSheet(f"background-color: {COLORS['white']}; border-radius: 12px; border: 1px solid {COLORS['border']};")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15); shadow.setColor(QColor(0, 0, 0, 20)); shadow.setOffset(0, 2)
        frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 15, 10, 5)
        
        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['dark']}; border: none;")
        layout.addWidget(lbl)
        
        fig = Figure(figsize=(4, 3), dpi=100)
        fig.patch.set_facecolor('none')
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color: transparent;")
        
        layout.addWidget(canvas)
        frame.canvas = canvas 
        frame.figure = fig
        return frame

    def _update_card_value(self, card_widget, value):
        lbl = card_widget.findChild(QLabel, "value_label")
        if lbl: lbl.setText(str(value))

    def refresh_data(self):
        interns = self.i_service.get_all_interns()
        
        total_interns = len(interns)
        no_venue_count = sum(1 for i in interns if not i.venue_id)
        
        # Pendências Gerais (Card)
        total_pending_items = 0
        for i in interns:
            docs = self.d_service.get_documents_by_intern(i.intern_id)
            total_pending_items += sum(1 for d in docs if d.status != "Aprovado")
            if not docs: total_pending_items += 1

        all_meetings = self.m_service.repo.get_all()
        now = datetime.now()
        meetings_month = sum(1 for m in all_meetings if 
                             datetime.strptime(m.meeting_date, "%Y-%m-%d").month == now.month)

        self._update_card_value(self.card_total, total_interns)
        self._update_card_value(self.card_no_venue, no_venue_count)
        self._update_card_value(self.card_pending, total_pending_items)
        self._update_card_value(self.card_meetings, meetings_month)

        self._plot_venue_distribution(self.chart1_frame, total_interns, no_venue_count)
        
        filter_doc = self.combo_doc_filter.currentText()
        self._plot_docs_filtered(filter_doc, interns)

    def _plot_venue_distribution(self, frame, total, no_venue):
        if frame.figure is None or frame.canvas is None: return

        frame.figure.clear()
        ax = frame.figure.add_axes([0, 0, 0.6, 1]) 
        
        with_venue = total - no_venue
        if total == 0:
            ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
        else:
            labels = ['Alocados', 'Sem Local']
            sizes = [with_venue, no_venue]
            colors = [COLORS['success'], COLORS['danger']]
            
            wedges, texts, autotexts = ax.pie(
                sizes, autopct='%1.0f%%', startangle=90, 
                colors=colors, pctdistance=0.80,
                textprops={'color': "#FFFFFF", 'fontsize': 10, 'weight': 'bold'},
                wedgeprops={'width': 0.4, 'edgecolor': 'white'}
            )
            
            frame.figure.legend(wedges, labels, title="Status", loc="center left", bbox_to_anchor=(0.65, 0.5), frameon=False)
            
        frame.canvas.draw()

    def _plot_docs_filtered(self, filter_name, interns):
        self.fig_docs.clear()
        ax = self.fig_docs.add_subplot(111)

        ok_count = 0
        pending_count = 0
        
        if filter_name == "Todos":
            for i in interns:
                docs = self.d_service.get_documents_by_intern(i.intern_id)
                if not docs:
                    pending_count += 1
                elif any(d.status != "Aprovado" for d in docs):
                    pending_count += 1
                else:
                    ok_count += 1
        else:
            for i in interns:
                docs = self.d_service.get_documents_by_intern(i.intern_id)
                target_docs = [d for d in docs if filter_name.lower() in d.document_name.lower()]
                
                if not target_docs:
                    pending_count += 1
                else:
                    is_ok = any(d.status == "Aprovado" for d in target_docs)
                    if is_ok:
                        ok_count += 1
                    else:
                        pending_count += 1

        categories = ['Aprovado', 'Pendente']
        values = [ok_count, pending_count]
        colors = [COLORS['success'], COLORS['warning']]

        if sum(values) == 0:
             ax.text(0.5, 0.5, "Sem dados", ha='center', va='center')
        else:
            bars = ax.barh(categories, values, color=colors, height=0.4)
            ax.bar_label(bars, padding=3, fontweight='bold')
            ax.set_xlim(0, max(values)*1.2 if max(values)>0 else 1)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.get_xaxis().set_visible(False)
            ax.tick_params(axis='y', length=0)
            
        self.fig_docs.tight_layout()
        self.canvas_docs.draw()