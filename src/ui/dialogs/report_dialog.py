from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QLabel, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from core.models.intern import Intern
from services.grade_service import GradeService
from services.evaluation_criteria_service import EvaluationCriteriaService

class ReportDialog(QDialog):
    """
    Dialog to visualize the student's academic performance (The "Boletim").
    """
    def __init__(
        self, 
        parent, 
        intern: Intern, 
        grade_service: GradeService, 
        criteria_service: EvaluationCriteriaService
    ):
        super().__init__(parent)
        self.setWindowTitle(f"Boletim: {intern.name}")
        self.resize(600, 400)
        
        self.intern = intern
        self.grade_service = grade_service
        self.criteria_service = criteria_service
        
        # CORREÇÃO PYLANCE: Renomeado de self.layout para self.main_layout
        # 'self.layout' conflitava com o método nativo layout() do QDialog
        self.main_layout = QVBoxLayout(self)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        # Cabeçalho com dados do aluno
        info_layout = QVBoxLayout()
        name_label = QLabel(f"Estagiário: {self.intern.name}")
        
        # CORREÇÃO PYLANCE: QFont.Weight.Bold
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(name_label)
        
        # Tabela de Notas
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Critério", "Peso Máx", "Nota Obtida", "Situação"])
        
 # Certifique-se de importar isso lá em cima
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus) # Remove o foco visual (opcional)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection) # Opcional: usuário não pode nem selecionar
        # CORREÇÃO PYLANCE: QHeaderView.ResizeMode.Stretch
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        self.main_layout.addLayout(info_layout)
        self.main_layout.addWidget(self.table)

        # Rodapé com o Total
        self.total_label = QLabel("Nota Final: 0.0 / 10.0")
        
        # CORREÇÃO PYLANCE: QFont.Weight.Bold e Qt.AlignmentFlag.AlignCenter
        self.total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.total_label)

        # Botão Fechar
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)
        self.main_layout.addWidget(btn_close)

    def load_data(self):
        # CORREÇÃO PYLANCE: Garantir que ID existe antes de chamar o serviço
        if self.intern.intern_id is None:
            self.total_label.setText("Erro: Aluno sem ID")
            return

        # 1. Buscar todas as regras do jogo (Critérios)
        all_criteria = self.criteria_service.list_active_criteria()
        
        # 2. Buscar o desempenho do jogador (Notas do Aluno)
        student_grades = self.grade_service.get_intern_grades(self.intern.intern_id)
        
        # Mapear notas por criteria_id para acesso rápido (O(1))
        grades_map = {g.criteria_id: g.value for g in student_grades}

        self.table.setRowCount(len(all_criteria))
        
        total_score = 0.0
        max_possible_score = 0.0

        for row, criteria in enumerate(all_criteria):
            # Nome do Critério
            self.table.setItem(row, 0, QTableWidgetItem(criteria.name))
            
            # Peso Máximo
            self.table.setItem(row, 1, QTableWidgetItem(f"{criteria.weight:.1f}"))
            max_possible_score += criteria.weight

            # Nota do Aluno (Se não tiver nota, é 0.0)
            score = grades_map.get(criteria.criteria_id, 0.0)
            total_score += score
            
            score_item = QTableWidgetItem(f"{score:.1f}")
            if score >= (criteria.weight * 0.7): # Ex: 70% do peso
                score_item.setForeground(QColor("green"))
            else:
                score_item.setForeground(QColor("red")) # Alerta visual
            
            self.table.setItem(row, 2, score_item)

            # Situação (Texto)
            status = "Ok" if score > 0 else "Pendente"
            self.table.setItem(row, 3, QTableWidgetItem(status))

        # Atualiza o Placar Final
        self.total_label.setText(f"Nota Final: {total_score:.1f} / {max_possible_score:.1f}")
        
        # Decoração Condicional (Passou ou Rodou?)
        if total_score >= 7.0:
            self.total_label.setStyleSheet("color: green;")
            self.total_label.setText(self.total_label.text() + " (APROVADO)")
        else:
            self.total_label.setStyleSheet("color: red;")
            self.total_label.setText(self.total_label.text() + " (EM RISCO)")