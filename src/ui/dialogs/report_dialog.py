from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QMessageBox,
    QFileDialog,
    QWidget,
    QProgressBar,
)
from PySide6.QtCore import Qt, QSize, QTimer
import qtawesome as qta

from core.models.intern import Intern

# Services imports
from services.grade_service import GradeService
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.report_service import ReportService
from services.venue_service import VenueService
from services.document_service import DocumentService
from services.meeting_service import MeetingService
from services.observation_service import ObservationService

from ui.styles import COLORS


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
        self.setWindowTitle(f"Gerar Relatório: {intern.name}")
        self.resize(500, 450)

        # Guarda referências
        self.intern = intern
        self.grade_service = grade_service
        self.criteria_service = criteria_service
        self.report_service = report_service
        self.venue_service = venue_service
        self.doc_service = document_service
        self.meeting_service = meeting_service
        self.obs_service = observation_service

        # Estilo
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["white"]}; }}
            QLabel {{ color: {COLORS["dark"]}; font-size: 14px; }}
            QProgressBar {{
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                text-align: center;
                background-color: {COLORS["light"]};
            }}
            QProgressBar::chunk {{ background-color: {COLORS["primary"]}; }}
        """)

        self._setup_ui()
        self._load_summary()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # --- Header com Ícone PDF ---
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(
            qta.icon("fa5s.file-pdf", color=COLORS["danger"]).pixmap(QSize(48, 48))
        )

        title_box = QVBoxLayout()
        title_box.setSpacing(5)
        lbl_title = QLabel("Relatório de Estágio")
        lbl_title.setStyleSheet(
            f"font-size: 22px; font-weight: 800; color: {COLORS['dark']};"
        )
        lbl_sub = QLabel(f"Aluno: {self.intern.name}")
        lbl_sub.setStyleSheet(f"font-size: 14px; color: {COLORS['secondary']};")

        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)

        header.addWidget(icon_lbl)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {COLORS['border']}")
        layout.addWidget(line)

        # --- Resumo do Conteúdo ---
        self.info_container = QWidget()
        info_layout = QVBoxLayout(self.info_container)
        info_layout.setSpacing(10)

        lbl_info = QLabel("O arquivo PDF conterá:")
        lbl_info.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        info_layout.addWidget(lbl_info)

        self.lbl_grades = QLabel("⌛ Verificando Notas...")
        self.lbl_docs = QLabel("⌛ Verificando Documentos...")
        self.lbl_meetings = QLabel("⌛ Verificando Supervisão...")

        info_layout.addWidget(self.lbl_grades)
        info_layout.addWidget(self.lbl_docs)
        info_layout.addWidget(self.lbl_meetings)

        layout.addWidget(self.info_container)
        layout.addStretch()

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # --- Botões ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(
            f"background: transparent; color: {COLORS['secondary']}; border: none; font-weight: 600;"
        )
        btn_cancel.clicked.connect(self.reject)

        self.btn_generate = QPushButton(" Gerar PDF Agora")
        self.btn_generate.setIcon(qta.icon("fa5s.download", color="white"))
        self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["success"]}; color: white; border: none; 
                padding: 12px 25px; border-radius: 6px; font-weight: bold; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #0E6A0E; }}
        """)
        self.btn_generate.clicked.connect(self.generate_report)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_generate)
        layout.addLayout(btn_layout)

    def _load_summary(self):
        if self.intern.intern_id is None:
            self.lbl_grades.setText("Erro: Aluno não salvo no banco de dados.")
            return

        intern_id = self.intern.intern_id

        # 1. Notas
        grades = self.grade_service.get_grades_by_intern(intern_id)
        if grades:
            avg = sum(g.value for g in grades)
            self.lbl_grades.setText(f"✅ {len(grades)} Notas lançadas (Soma: {avg:.1f})")
            self.lbl_grades.setStyleSheet(f"color: {COLORS['success']};")
        else:
            self.lbl_grades.setText("⚠️ Nenhuma nota lançada (Relatório sairá zerado)")
            self.lbl_grades.setStyleSheet(f"color: {COLORS['warning']};")

        # 2. Documentos
        docs = self.doc_service.get_documents_by_intern(intern_id)
        # CORREÇÃO DE LÓGICA: Considera pendente tudo que não for "Aprovado"
        pending = sum(1 for d in docs if d.status != "Aprovado")
        
        if pending > 0:
            self.lbl_docs.setText(f"⚠️ {pending} Documentos pendentes de aprovação")
            self.lbl_docs.setStyleSheet(f"color: {COLORS['warning']};")
        else:
            self.lbl_docs.setText(f"✅ {len(docs)} Documentos verificados")
            self.lbl_docs.setStyleSheet(f"color: {COLORS['success']};")

        # 3. Meetings
        meetings = self.meeting_service.get_meetings_by_intern(intern_id)
        self.lbl_meetings.setText(f"📅 {len(meetings)} Registros de supervisão")

    def generate_report(self):
        if self.intern.intern_id is None:
            QMessageBox.warning(self, "Erro", "Este aluno ainda não foi salvo. Salve antes de gerar relatório.")
            return

        filename = f"Relatorio_{self.intern.name.replace(' ', '_')}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório PDF", filename, "PDF Files (*.pdf)")

        if not path:
            return

        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("Gerando...")
        self.progress.setVisible(True)
        self.progress.setValue(20)

        QTimer.singleShot(100, lambda: self._process_generation(path))

    def _process_generation(self, path):
        try:
            if self.intern.intern_id is None:
                raise ValueError("ID do aluno inválido.")

            intern_id = self.intern.intern_id
            self.progress.setValue(40)

            venue = None
            if self.intern.venue_id:
                venue = self.venue_service.get_by_id(self.intern.venue_id)

            all_criteria = self.criteria_service.list_active_criteria()
            grades = self.grade_service.get_grades_by_intern(intern_id)
            documents = self.doc_service.get_documents_by_intern(intern_id)
            meetings = self.meeting_service.get_meetings_by_intern(intern_id)
            observations = self.obs_service.get_observations_by_intern(intern_id)

            self.progress.setValue(70)

            self.report_service.generate_pdf(
                filepath=path,
                intern=self.intern,
                venue=venue,
                criteria_list=all_criteria,
                grades=grades,
                documents=documents,
                meetings=meetings,
                observations=observations,
            )

            self.progress.setValue(100)
            QMessageBox.information(self, "Sucesso", f"Relatório salvo com sucesso!\n{path}")
            self.accept()

        except Exception as e:
            self.progress.setVisible(False)
            self.btn_generate.setEnabled(True)
            self.btn_generate.setText("Tentar Novamente")
            QMessageBox.critical(self, "Erro Fatal", f"Não foi possível gerar o PDF.\nErro: {e}")