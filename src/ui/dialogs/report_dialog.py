from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QHeaderView,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

from core.models.intern import Intern
from services.grade_service import GradeService
from services.evaluation_criteria_service import EvaluationCriteriaService

# Import do novo serviço
from services.report_service import ReportService


class ReportDialog(QDialog):
    """
    Dialog to visualize the student's academic performance (The "Boletim").
    """

    def __init__(
        self,
        parent,
        intern: Intern,
        grade_service: GradeService,
        criteria_service: EvaluationCriteriaService,
        report_service: ReportService,  # <--- Injeção de Dependência aqui
    ):
        super().__init__(parent)
        self.setWindowTitle(f"Boletim: {intern.name}")
        self.resize(600, 500)

        self.intern = intern
        self.grade_service = grade_service
        self.criteria_service = criteria_service
        self.report_service = report_service

        self.main_layout = QVBoxLayout(self)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        # Cabeçalho
        info_layout = QVBoxLayout()
        name_label = QLabel(f"Estagiário: {self.intern.name}")
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(name_label)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Critério", "Peso Máx", "Nota Obtida", "Situação"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        # Tabela somente leitura é uma boa prática
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.main_layout.addLayout(info_layout)
        self.main_layout.addWidget(self.table)

        # Rodapé com o Total
        self.total_label = QLabel("Nota Final: 0.0 / 10.0")
        self.total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.total_label)

        # Botões
        btn_layout = QHBoxLayout()

        self.btn_pdf = QPushButton("🖨️ Exportar PDF")
        self.btn_pdf.setStyleSheet(
            "background-color: #0078D7; color: white; font-weight: bold; padding: 10px;"
        )
        self.btn_pdf.clicked.connect(self.export_pdf)

        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_pdf)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)

        self.main_layout.addLayout(btn_layout)

    def load_data(self):
        if self.intern.intern_id is None:
            self.total_label.setText("Erro: Aluno sem ID")
            self.btn_pdf.setEnabled(False)
            return

        # Carrega dados para a memória (serão usados na exportação também)
        self.all_criteria = self.criteria_service.list_active_criteria()
        self.student_grades = self.grade_service.get_intern_grades(
            self.intern.intern_id
        )

        grades_map = {g.criteria_id: g.value for g in self.student_grades}
        self.table.setRowCount(len(self.all_criteria))

        total_score = 0.0
        max_possible_score = 0.0

        for row, criteria in enumerate(self.all_criteria):
            self.table.setItem(row, 0, QTableWidgetItem(criteria.name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{criteria.weight:.1f}"))
            max_possible_score += criteria.weight

            score = grades_map.get(criteria.criteria_id, 0.0)
            total_score += score

            score_item = QTableWidgetItem(f"{score:.1f}")
            if score >= (criteria.weight * 0.7):
                score_item.setForeground(QColor("green"))
            else:
                score_item.setForeground(QColor("red"))

            self.table.setItem(row, 2, score_item)
            status = "Ok" if score > 0 else "Pendente"
            self.table.setItem(row, 3, QTableWidgetItem(status))

        self.total_label.setText(
            f"Nota Final: {total_score:.1f} / {max_possible_score:.1f}"
        )

        if total_score >= 7.0:
            self.total_label.setStyleSheet("color: green;")
            self.total_label.setText(self.total_label.text() + " (APROVADO)")
        else:
            self.total_label.setStyleSheet("color: red;")
            self.total_label.setText(self.total_label.text() + " (EM RISCO)")

    def export_pdf(self):
        """Chama o serviço para gerar o PDF."""
        if not self.intern.intern_id:
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Boletim",
            f"Boletim_{self.intern.name.replace(' ', '_')}.pdf",
            "Arquivos PDF (*.pdf)",
        )

        if filename:
            try:
                self.report_service.generate_pdf(
                    filename, self.intern, self.all_criteria, self.student_grades
                )
                QMessageBox.information(
                    self, "Sucesso", f"Boletim salvo em:\n{filename}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao gerar PDF: {e}")
