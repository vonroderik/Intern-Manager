from datetime import datetime
from PySide6.QtGui import QTextDocument, QPageSize
from PySide6.QtCore import QSettings
from PySide6.QtPrintSupport import QPrinter
from core.models.intern import Intern
from core.models.grade import Grade
from core.models.evaluation_criteria import EvaluationCriteria


class ReportService:
    """
    Serviço responsável por transformar dados em documentos oficiais (PDF).
    Porque se não está no papel (ou PDF), não aconteceu.
    """

    def generate_pdf(
        self,
        filepath: str,
        intern: Intern,
        criteria_list: list[EvaluationCriteria],
        grades: list[Grade],
    ):
        """
        Gera um boletim em PDF baseado nos dados fornecidos.
        Usa HTML/CSS para estilização.
        """

        grades_map = {
            g.criteria_id: g.value for g in grades if g.criteria_id is not None
        }

        total_score = 0.0
        max_score = 0.0

        rows_html = ""

        for c in criteria_list:
            if c.criteria_id is None:
                continue

            score = grades_map.get(c.criteria_id, 0.0)
            total_score += score
            max_score += c.weight

            # Estilização condicional da linha
            color = "green" if score >= (c.weight * 0.7) else "#D32F2F"

            rows_html += f"""
            <tr>
                <td>{c.name}</td>
                <td style="text-align: center;">{c.weight:.1f}</td>
                <td style="text-align: center; color: {color}; font-weight: bold;">{score:.1f}</td>
                <td style="text-align: center;">{"Concluído" if score > 0 else "Pendente"}</td>
            </tr>
            """

        status = "APROVADO" if total_score >= 7.0 else "EM ANÁLISE"
        status_color = "green" if total_score >= 7.0 else "red"

        settings = QSettings("MyOrganization", "InternManager2026")
        institution = settings.value(
            "institution_name", "INSTITUIÇÃO DE ENSINO SUPERIOR"
        )
        coordinator = settings.value("coordinator_name", "Coordenação de Estágios")
        city = settings.value("city_state", "")

        date_str = datetime.now().strftime("%d/%m/%Y às %H:%M")

        html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: sans-serif; padding: 40px; }}
                    h1 {{ color: #2c3e50; font-size: 24px; text-align: center; margin-bottom: 5px; }}
                    h2 {{ color: #7f8c8d; font-size: 16px; text-align: center; margin-top: 0; margin-bottom: 30px; }}
                    .meta-box {{ border: 1px solid #ddd; padding: 15px; background-color: #f9f9f9; margin-bottom: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th {{ background-color: #0078D7; color: white; padding: 10px; border: 1px solid #005a9e; }}
                    td {{ padding: 8px; border: 1px solid #ddd; }}
                    .total-box {{ text-align: right; margin-top: 20px; font-size: 18px; }}
                    .footer {{ margin-top: 80px; text-align: center; font-size: 12px; color: #555; border-top: 1px solid #ccc; padding-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{institution}</h1>
                    <h2>Boletim de Avaliação de Estágio</h2>
                </div>

                <div class="meta-box">
                    <p><strong>Estagiário(a):</strong> {intern.name}</p>
                    <p><strong>RA:</strong> {intern.registration_number} &nbsp;|&nbsp; <strong>Semestre:</strong> {intern.term}</p>
                    <p><strong>Emissão:</strong> {date_str} &nbsp;|&nbsp; <strong>Local:</strong> {city}</p>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th style="text-align: left;">Critério Avaliado</th>
                            <th style="width: 80px;">Peso</th>
                            <th style="width: 80px;">Nota</th>
                            <th style="width: 100px;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>

                <div class="total-box">
                    <p><strong>Nota Final:</strong> {total_score:.1f} / {max_score:.1f}</p>
                    <p style="color: {status_color};"><strong>SITUAÇÃO: {status}</strong></p>
                </div>

                <div class="footer">
                    <p>___________________________________________________</p>
                    <p>{coordinator}<br>Supervisor(a) de Estágios</p>
                    <p><small>Documento gerado eletronicamente pelo Intern Manager 2026.</small></p>
                </div>
            </body>
            </html>
            """

        doc = QTextDocument()
        doc.setHtml(html_content)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filepath)

        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

        doc.print_(printer)
