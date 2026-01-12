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

# Services imports
from services.grade_service import GradeService
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.report_service import ReportService
from services.venue_service import VenueService
from services.document_service import DocumentService
from services.meeting_service import MeetingService
from services.observation_service import ObservationService


class ReportDialog(QDialog):
    def __init__(
        self,
        parent,
        intern: Intern,
        grade_service: GradeService,
        criteria_service: EvaluationCriteriaService,
        report_service: ReportService,
        venue_service: VenueService,
        document_service: DocumentService,
        meeting_service: MeetingService,
        observation_service: ObservationService,
    ):
        super().__init__(parent)
        self.setWindowTitle(f"Boletim Completo: {intern.name}")
        self.resize(700, 550)

        self.intern = intern
        self.grade_service = grade_service
        self.criteria_service = criteria_service
        self.report_service = report_service

        self.venue_service = venue_service
        self.doc_service = document_service
        self.meeting_service = meeting_service
        self.obs_service = observation_service

        self.main_layout = QVBoxLayout(self)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        info_layout = QVBoxLayout()
        name_label = QLabel(f"Estagiário: {self.intern.name}")
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(name_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Critério", "Peso Máx", "Nota Obtida", "Situação"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.main_layout.addLayout(info_layout)
        self.main_layout.addWidget(self.table)

        self.total_label = QLabel("Nota Final: 0.0")
        self.total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.total_label)

        btn_layout = QHBoxLayout()
        self.btn_pdf = QPushButton("🖨️ Gerar Relatório Completo (PDF)")
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
            self.btn_pdf.setEnabled(False)
            return

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
        if not self.intern.intern_id:
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            f"Relatorio_{self.intern.name.replace(' ', '_')}.pdf",
            "Arquivos PDF (*.pdf)",
        )

        if filename:
            try:
                # 1. Buscar Local
                venue = None
                if self.intern.venue_id:
                    venue = self.venue_service.get_by_id(self.intern.venue_id)

                # 2. Buscar Documentos
                documents = self.doc_service.repo.get_by_intern_id(
                    self.intern.intern_id
                )

                # 3. Buscar Reuniões
                meetings = self.meeting_service.get_meetings_by_intern(
                    self.intern.intern_id
                )

                # 4. Buscar Observações
                observations = self.obs_service.get_intern_observations(
                    self.intern.intern_id
                )

                # 5. Gerar PDF
                self.report_service.generate_pdf(
                    filepath=filename,
                    intern=self.intern,
                    venue=venue,
                    criteria_list=self.all_criteria,
                    grades=self.student_grades,
                    documents=documents,
                    meetings=meetings,
                    observations=observations,
                )

                QMessageBox.information(
                    self, "Sucesso", f"Relatório completo salvo em:\n{filename}"
                )
            except Exception as e:
                import traceback

                traceback.print_exc()
                QMessageBox.critical(self, "Erro", f"Falha ao gerar PDF: {e}")
