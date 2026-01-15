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
    def __init__(self, parent, venue_service: VenueService, intern: Optional[Intern] = None):
        super().__init__(parent)
        self.intern = intern
        self.venue_service = venue_service

        self.setWindowTitle("Ficha do Estagiário")
        self.setMinimumWidth(550)

        # CSS
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS['light']}; }}
            QLabel {{ color: {COLORS['dark']}; font-size: 13px; }}
            QLineEdit, QComboBox, QDateEdit {{
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                color: {COLORS['dark']};
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{ border: 1px solid {COLORS['primary']}; }}
            QDateEdit::drop-down {{ border: none; width: 20px; }}
        """)

        self._setup_ui()
        self.load_venues()

        if self.intern:
            self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Header
        lbl_head = QLabel("Editar Aluno" if self.intern else "Novo Aluno")
        lbl_head.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {COLORS['primary']}; margin-bottom: 10px;")
        layout.addWidget(lbl_head)

        # Form
        form_frame = QFrame()
        form_frame.setStyleSheet(f"background-color: {COLORS['white']}; border-radius: 8px; border: 1px solid {COLORS['border']};")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        self.txt_name = QLineEdit()
        self.txt_ra = QLineEdit()
        self.txt_email = QLineEdit()

        # Venue
        self.combo_venue = QComboBox()
        self.btn_add_venue = QPushButton()
        self.btn_add_venue.setIcon(qta.icon('fa5s.plus', color='white'))
        self.btn_add_venue.setFixedSize(36, 36)
        self.btn_add_venue.setStyleSheet(f"background-color: {COLORS['success']}; border-radius: 4px; border: none;")
        self.btn_add_venue.clicked.connect(self.quick_add_venue)

        venue_layout = QHBoxLayout()
        venue_layout.addWidget(self.combo_venue)
        venue_layout.addWidget(self.btn_add_venue)

        # Datas
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("dd/MM/yyyy")
        self.date_start.setDate(QDate.currentDate())

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("dd/MM/yyyy")
        self.date_end.setDate(QDate.currentDate().addMonths(6))

        # Term
        self.combo_term = QComboBox()
        self.combo_term.addItems([f"{y}/{s}" for y in range(2025, 2030) for s in [1, 2]])

        # JORNADA E HORÁRIO
        self.txt_hours = QLineEdit()
        self.txt_hours.setPlaceholderText("Ex: 30h semanais")
        
        self.txt_days = QLineEdit()
        self.txt_days.setPlaceholderText("Ex: Seg a Sex")

        hours_layout = QHBoxLayout()
        # Coloquei labels internas para não haver confusão visual
        hours_layout.addWidget(self.txt_hours)
        hours_layout.addWidget(QLabel("   Dias:")) 
        hours_layout.addWidget(self.txt_days)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet("font-weight: bold;")
            return l

        form_layout.addRow(lbl("Nome Completo *:"), self.txt_name)
        form_layout.addRow(lbl("RA (Matrícula) *:"), self.txt_ra)
        form_layout.addRow(lbl("E-mail:"), self.txt_email)
        form_layout.addRow(lbl("Local de Estágio:"), venue_layout)
        form_layout.addRow(lbl("Semestre:"), self.combo_term)
        form_layout.addRow(lbl("Carga Horária:"), hours_layout) # <--- AQUI O LAYOUT
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(lbl("Início:"))
        date_layout.addWidget(self.date_start)
        date_layout.addSpacing(20)
        date_layout.addWidget(lbl("Término:"))
        date_layout.addWidget(self.date_end)
        form_layout.addRow(lbl("Vigência:"), date_layout)

        layout.addWidget(form_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton(" Salvar Aluno")
        self.btn_save.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_save.setStyleSheet(f"background-color: {COLORS['primary']}; color: white; border: none; padding: 10px 25px; border-radius: 6px; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_data)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def load_venues(self):
        current = self.combo_venue.currentData()
        self.combo_venue.clear()
        self.combo_venue.addItem("--- Selecione ---", None)
        for v in self.venue_service.get_all():
            self.combo_venue.addItem(v.venue_name, v.venue_id)
        if current:
            idx = self.combo_venue.findData(current)
            if idx >= 0: self.combo_venue.setCurrentIndex(idx)

    def quick_add_venue(self):
        dialog = VenueDialog(self)
        if dialog.exec():
            try:
                new_id = self.venue_service.add_new_venue(dialog.get_data())
                self.load_venues()
                idx = self.combo_venue.findData(new_id)
                if idx >= 0: self.combo_venue.setCurrentIndex(idx)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro: {e}")

    def load_data(self):
        if not self.intern: return
        self.txt_name.setText(self.intern.name)
        self.txt_ra.setText(self.intern.registration_number)
        self.txt_email.setText(self.intern.email or "")
        self.combo_term.setCurrentText(self.intern.term)
        
        # Carregamento Correto
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
        self.accept()

    def get_data(self) -> Intern:
        cid = self.intern.intern_id if self.intern else None
        
        # Mapeamento Correto
        return Intern(
            intern_id=cid,
            name=self.txt_name.text().strip(),
            registration_number=self.txt_ra.text().strip(),
            email=self.txt_email.text().strip(),
            venue_id=self.combo_venue.currentData(),
            term=self.combo_term.currentText(),
            start_date=self.date_start.date().toString("yyyy-MM-dd"),
            end_date=self.date_end.date().toString("yyyy-MM-dd"),
            
            # Aqui garantimos que txt_hours -> working_hours
            working_hours=self.txt_hours.text().strip() or None,
            working_days=self.txt_days.text().strip() or None
        )