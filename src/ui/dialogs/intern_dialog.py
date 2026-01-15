from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QHBoxLayout,
    QVBoxLayout, QMessageBox, QLabel, QPushButton, QFrame,
    QDateEdit, QComboBox
)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta

from core.models.intern import Intern
from services.venue_service import VenueService
from ui.dialogs.venue_dialog import VenueDialog
from utils.validations import validate_date_range
from ui.styles import COLORS

class InternDialog(QDialog):
    """Dialog para criar/editar Estagiário com estilo moderno."""
    
    def __init__(self, parent, venue_service: VenueService, intern: Optional[Intern] = None):
        super().__init__(parent)
        self.intern = intern
        self.venue_service = venue_service

        self.setWindowTitle("Ficha do Estagiário")
        self.setMinimumWidth(550) # Aumentei um pouco a largura para caber as datas confortavelmente

        # CSS Corrigido
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS['light']}; }}
            QLabel {{ color: {COLORS['dark']}; font-size: 13px; }}
            
            /* Estilo Geral para Inputs de Texto e Combo */
            QLineEdit, QComboBox {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                min-height: 20px;
                font-size: 13px;
                color: {COLORS['dark']};
            }}
            
            /* Estilo Específico para Data - Padding Reduzido para não cortar texto */
            QDateEdit {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 4px 4px 4px 8px; /* Padding direito menor para dar espaço ao botão */
                min-height: 20px;
                font-size: 13px;
                color: {COLORS['dark']};
            }}

            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{ 
                border: 1px solid {COLORS['primary']}; 
            }}
            
            /* Estilo para a seta do ComboBox */
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            
            /* IMPORTANTE: Removemos qualquer estilo de QDateEdit::drop-down 
               Isso força o Qt a desenhar o botão de calendário nativo do sistema,
               garantindo que ele apareça e funcione.
            */
        """)

        self._setup_ui()
        self.load_venues()

        if self.intern:
            self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # --- Header ---
        header_title = "Editar Aluno" if self.intern else "Novo Aluno"
        lbl_head = QLabel(header_title)
        lbl_head.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {COLORS['primary']}; margin-bottom: 10px;")
        layout.addWidget(lbl_head)

        # --- Card do Formulário ---
        form_frame = QFrame()
        form_frame.setStyleSheet(f"background-color: {COLORS['white']}; border-radius: 8px; border: 1px solid {COLORS['border']};")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        # Campos Pessoais
        self.txt_name = QLineEdit()
        self.txt_ra = QLineEdit()
        self.txt_email = QLineEdit()

        # Venue Combo + Botão Quick Add
        self.combo_venue = QComboBox()
        self.btn_add_venue = QPushButton()
        self.btn_add_venue.setIcon(qta.icon('fa5s.plus', color='white'))
        self.btn_add_venue.setFixedSize(36, 36)
        self.btn_add_venue.setToolTip("Cadastrar novo local")
        self.btn_add_venue.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_venue.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS['success']}; border-radius: 4px; border: none; }}
            QPushButton:hover {{ background-color: #0E6A0E; }}
        """)
        self.btn_add_venue.clicked.connect(self.quick_add_venue)

        venue_layout = QHBoxLayout()
        venue_layout.addWidget(self.combo_venue)
        venue_layout.addWidget(self.btn_add_venue)

        # Datas (Usando CalendarPopup=True para garantir o dropdown)
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True) 
        self.date_start.setDisplayFormat("dd/MM/yyyy")
        self.date_start.setDate(QDate.currentDate())
        # Ajuste de largura mínima para garantir que a data apareça inteira
        self.date_start.setMinimumWidth(120) 

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("dd/MM/yyyy")
        self.date_end.setDate(QDate.currentDate().addMonths(6))
        self.date_end.setMinimumWidth(120)

        # Semestre
        self.combo_term = QComboBox()
        terms = [f"{y}/{s}" for y in range(2025, 2030) for s in [1, 2]]
        self.combo_term.addItems(terms)

        # Novos Campos: Jornada
        self.txt_hours = QLineEdit()
        self.txt_hours.setPlaceholderText("Ex: 09:00 as 15:00")
        
        self.txt_days = QLineEdit()
        self.txt_days.setPlaceholderText("Ex: Seg a Sex")

        # Helper para labels bold
        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet("font-weight: bold;")
            return l

        form_layout.addRow(lbl("Nome Completo *:"), self.txt_name)
        form_layout.addRow(lbl("RA (Matrícula) *:"), self.txt_ra)
        form_layout.addRow(lbl("E-mail:"), self.txt_email)
        form_layout.addRow(lbl("Local de Estágio:"), venue_layout)
        form_layout.addRow(lbl("Semestre Letivo:"), self.combo_term)
        
        # Linha de Jornada (Horas e Dias lado a lado)
        hours_layout = QHBoxLayout()
        hours_layout.addWidget(self.txt_hours)
        hours_layout.addWidget(lbl("Dias:")) # Label intermediária
        hours_layout.addWidget(self.txt_days)
        form_layout.addRow(lbl("Horários:"), hours_layout)
        
        # Linha de datas lado a lado
        date_layout = QHBoxLayout()
        date_layout.addWidget(lbl("Início:"))
        date_layout.addWidget(self.date_start)
        date_layout.addSpacing(20)
        date_layout.addWidget(lbl("Término:"))
        date_layout.addWidget(self.date_end)
        
        form_layout.addRow(lbl("Vigência:"), date_layout)

        layout.addWidget(form_frame)

        # --- Botões de Ação ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{ background-color: transparent; border: 1px solid {COLORS['secondary']}; color: {COLORS['secondary']}; padding: 10px 20px; border-radius: 6px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {COLORS['light']}; }}
        """)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(" Salvar Aluno")
        self.btn_save.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS['primary']}; color: white; border: none; padding: 10px 25px; border-radius: 6px; font-weight: bold; font-size: 14px; }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        self.btn_save.clicked.connect(self.save_data)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def load_venues(self):
        current_data = self.combo_venue.currentData()
        self.combo_venue.clear()
        self.combo_venue.addItem("--- Selecione ---", None)
        venues = self.venue_service.get_all()
        for v in venues:
            self.combo_venue.addItem(v.venue_name, v.venue_id)
        if current_data:
            idx = self.combo_venue.findData(current_data)
            if idx >= 0: self.combo_venue.setCurrentIndex(idx)

    def quick_add_venue(self):
        dialog = VenueDialog(self)
        if dialog.exec():
            try:
                new_data = dialog.get_data()
                new_id = self.venue_service.add_new_venue(new_data)
                self.load_venues()
                idx = self.combo_venue.findData(new_id)
                if idx >= 0: self.combo_venue.setCurrentIndex(idx)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao criar local: {e}")

    def load_data(self):
        if not self.intern: return
        self.txt_name.setText(str(self.intern.name or ""))
        self.txt_ra.setText(str(self.intern.registration_number or ""))
        self.txt_email.setText(self.intern.email or "")
        self.combo_term.setCurrentText(self.intern.term)
        
        # Campos Novos
        self.txt_hours.setText(self.intern.working_hours or "")
        self.txt_days.setText(self.intern.working_days or "")
        
        if self.intern.venue_id:
            idx = self.combo_venue.findData(self.intern.venue_id)
            if idx >= 0: self.combo_venue.setCurrentIndex(idx)

        if self.intern.start_date:
            self.date_start.setDate(QDate.fromString(self.intern.start_date, "yyyy-MM-dd"))
        if self.intern.end_date:
            self.date_end.setDate(QDate.fromString(self.intern.end_date, "yyyy-MM-dd"))

    def save_data(self):
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Erro", "Nome é obrigatório.")
            return
        if not self.txt_ra.text().strip():
            QMessageBox.warning(self, "Erro", "RA é obrigatório.")
            return

        s_str = self.date_start.date().toString("dd/MM/yyyy")
        e_str = self.date_end.date().toString("dd/MM/yyyy")
        
        try:
            validate_date_range(s_str, e_str)
        except ValueError as e:
            QMessageBox.warning(self, "Data Inválida", str(e))
            return

        self.accept()

    def get_data(self) -> Intern:
        cid = self.intern.intern_id if self.intern else None
        return Intern(
            intern_id=cid,
            name=self.txt_name.text().strip(),
            registration_number=self.txt_ra.text().strip(),
            email=self.txt_email.text().strip(),
            venue_id=self.combo_venue.currentData(),
            term=self.combo_term.currentText(),
            start_date=self.date_start.date().toString("yyyy-MM-dd"),
            end_date=self.date_end.date().toString("yyyy-MM-dd"),
            # Campos Novos sendo salvos
            working_hours=self.txt_hours.text().strip() or None,
            working_days=self.txt_days.text().strip() or None
        )