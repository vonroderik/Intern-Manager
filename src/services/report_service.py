from datetime import datetime
from PySide6.QtGui import QTextDocument, QPageSize  # <--- Adicionado QPageSize
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

        # 1. Preparar os dados (Matemática básica)
        # Filtramos grades que não tem criteria_id para evitar chaves None no dicionário
        grades_map = {
            g.criteria_id: g.value for g in grades if g.criteria_id is not None
        }

        total_score = 0.0
        max_score = 0.0

        rows_html = ""

        for c in criteria_list:
            # CORREÇÃO PYLANCE 1:
            # Verificamos se o critério tem ID antes de usar como chave
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

        date_str = datetime.now().strftime("%d/%m/%Y às %H:%M")

        # 2. O Template HTML (Beleza interior)
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; padding: 20px; }}
                h1 {{ color: #0078D7; }}
                .header {{ margin-bottom: 30px; border-bottom: 2px solid #ccc; padding-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ background-color: #f2f2f2; padding: 10px; border: 1px solid #ddd; }}
                td {{ padding: 8px; border: 1px solid #ddd; }}
                .total {{ font-size: 18px; font-weight: bold; text-align: right; margin-top: 20px; }}
                .footer {{ margin-top: 50px; font-size: 10px; color: gray; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Boletim de Avaliação de Estágio</h1>
                <p><strong>Estagiário:</strong> {intern.name}</p>
                <p><strong>RA:</strong> {intern.registration_number} | <strong>Semestre:</strong> {intern.term}</p>
                <p><strong>Data de Emissão:</strong> {date_str}</p>
            </div>

            <table>
                <thead>
                    <tr>
                        <th style="text-align: left;">Critério Avaliado</th>
                        <th>Peso Máx</th>
                        <th>Nota Obtida</th>
                        <th>Situação</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <div class="total">
                <p>Nota Final: {total_score:.1f} / {max_score:.1f}</p>
                <p style="color: {status_color};">SITUAÇÃO: {status}</p>
            </div>

            <div class="footer">
                Documento gerado automaticamente pelo Sistema Intern Manager 2026.
                <br>Verifique a autenticidade com o supervisor responsável.
            </div>
        </body>
        </html>
        """

        # 3. Renderização (A Mágica)
        doc = QTextDocument()
        doc.setHtml(html_content)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filepath)

        # CORREÇÃO PYLANCE 2:
        # A4 agora vive em QPageSize.PageSizeId.A4 no PySide6
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

        doc.print_(printer)
