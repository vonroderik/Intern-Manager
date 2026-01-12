import os
import locale
from datetime import datetime
from PySide6.QtGui import QTextDocument, QPageSize, QPageLayout, QImage
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCore import QMarginsF, QSettings, QByteArray, QBuffer, QIODevice

from core.models.intern import Intern
from core.models.grade import Grade
from core.models.evaluation_criteria import EvaluationCriteria
from core.models.venue import Venue
from core.models.document import Document
from core.models.meeting import Meeting
from core.models.observation import Observation




class ReportService:
    """
    Serviço de Geração de Relatórios (PDF).
    Gera um relatório completo usando dados do QSettings para personalização.
    """

    def _get_image_base64(self, path):
            """Lê a imagem do disco e converte para Base64 para embutir no HTML."""
            if not path or not os.path.exists(path):
                return ""
            
            image = QImage(path)
            if image.isNull(): return ""

            # Redimensionar se for muito grande
            if image.height() > 100:
                image = image.scaledToHeight(100)

            ba = QByteArray()
            buffer = QBuffer(ba)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            
            # 1. Pylance reclama de string, mas o Runtime precisa de string ("PNG").
            # Adicionamos o 'type: ignore' para o editor ficar quieto.
            image.save(buffer, "PNG") # type: ignore
            
            # 2. A SOLUÇÃO DEFINITIVA PARA O BASE64:
            # .toBase64() -> Retorna QByteArray com os dados codificados
            # .toStdString() -> Converte direto para string Python (str)
            # NÃO use bytes(...) nem .decode(...) aqui.
            return f"data:image/png;base64,{ba.toBase64().toStdString()}"

    def generate_pdf(
        self,
        filepath: str,
        intern: Intern,
        venue: Venue | None,
        criteria_list: list[EvaluationCriteria],
        grades: list[Grade],
        documents: list[Document],
        meetings: list[Meeting],
        observations: list[Observation],
    ):
        # --- 1. Carregar Configurações (User Prefs) ---
        settings = QSettings("MyOrganization", "InternManager2026")

        inst_name = settings.value("institution_name", "Instituição de Ensino")
        supervisor_name = settings.value("coordinator_name", "")
        city_state = settings.value("city_state", "")
        logo_path = settings.value("logo_path", "")

        # Processar Logo
        logo_html = ""
        if logo_path:
            b64 = self._get_image_base64(logo_path)
            if b64:
                # Flutua a esquerda, margem na direita
                logo_html = f'<img src="{b64}" style="max-height: 80px; float: left; margin-right: 20px;">'

        # Cabeçalho Dinâmico
        header_subtext = ""
        if supervisor_name:
            header_subtext += f"Supervisor(a): {supervisor_name}<br>"

        # --- 2. Processamento de Dados ---

        # Notas
        grades_map = {
            g.criteria_id: g.value for g in grades if g.criteria_id is not None
        }
        total_score = 0.0
        max_score = 0.0

        grades_html_rows = ""
        for c in criteria_list:
            if c.criteria_id is None:
                continue
            val = grades_map.get(c.criteria_id, 0.0)
            total_score += val
            max_score += c.weight

            # Formatação condicional da nota
            color = "#2E7D32" if val >= (c.weight * 0.7) else "#C62828"
            grades_html_rows += f"""
            <tr>
                <td>{c.name}</td>
                <td class="text-center">{c.weight:.1f}</td>
                <td class="text-center" style="color: {color}; font-weight: bold;">{val:.1f}</td>
            </tr>
            """

        status_text = "APROVADO" if total_score >= 7.0 else "EM ANÁLISE / REPROVADO"
        status_color = "#2E7D32" if total_score >= 7.0 else "#C62828"

        # Frequência
        total_meetings = len(meetings)
        present_meetings = sum(1 for m in meetings if m.is_intern_present)
        freq_percent = (
            (present_meetings / total_meetings * 100) if total_meetings > 0 else 0.0
        )

        # Documentos
        docs_rows = ""
        pending_docs = 0
        for d in documents:
            if d.is_completed:
                st = "<span style='color:#2E7D32; font-weight:bold'>Entregue</span>"
            else:
                st = "<span style='color:#C62828; font-weight:bold'>Pendente</span>"
                pending_docs += 1
            docs_rows += (
                f"<tr><td>{d.document_name}</td><td class='text-center'>{st}</td></tr>"
            )

        # Observações
        obs_html = ""
        if observations:
            obs_html = "<h3>Histórico de Observações</h3><ul>"
            for o in observations:
                data_obs = o.last_update if o.last_update else "S/D"
                obs_html += f"<li style='margin-bottom: 5px;'><b>[{data_obs}]:</b> {o.observation}</li>"
            obs_html += "</ul>"
        else:
            obs_html = (
                "<p style='color:#777;'><i>Nenhuma observação registrada.</i></p>"
            )

        # Dados do Local
        if venue:
            venue_html = f"""
            <table class="info-table">
                <tr><th>Local:</th><td>{venue.venue_name}</td></tr>
                <tr><th>Supervisor Local:</th><td>{venue.supervisor_name or "-"}</td></tr>
                <tr><th>Contato:</th><td>{venue.supervisor_email or "-"} / {venue.supervisor_phone or "-"}</td></tr>
            </table>
            """
        else:
            venue_html = "<p style='color:red; font-style:italic;'>Local de estágio não vinculado.</p>"

        # Datas

        locale.setlocale(locale.LC_TIME, "pt_BR") # Define local para Brasil
        date_emission = datetime.now().strftime("%d/%m/%Y às %H:%M")
        start_fmt = (
            datetime.strptime(intern.start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            if intern.start_date
            else "-"
        )
        end_fmt = (
            datetime.strptime(intern.end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            if intern.end_date
            else "-"
        )

        local_data_sig = (
            f"{city_state}, {datetime.now().strftime('%d de %B de %Y')}"
            if city_state
            else f"Emissão: {date_emission}"
        )

        # --- 3. HTML Template ---
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Helvetica', 'Arial', sans-serif; font-size: 10pt; color: #333; line-height: 1.4; }}
                h1 {{ color: #003366; font-size: 18pt; margin: 0; padding-bottom: 5px; }}
                h2 {{ color: #003366; font-size: 12pt; border-bottom: 2px solid #003366; padding-bottom: 3px; margin-top: 15px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }}
                h3 {{ color: #555; font-size: 11pt; margin-top: 10px; margin-bottom: 5px; }}
                
                .header-container {{ overflow: hidden; margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 15px; }}
                .header-text {{ overflow: hidden; }}
                .sub-header {{ font-size: 9pt; color: #555; margin-top: 2px; }}

                .info-box {{ background-color: #f9f9f9; padding: 10px; border: 1px solid #eee; border-radius: 4px; margin-bottom: 10px; }}
                .info-table {{ width: 100%; border-collapse: collapse; }}
                .info-table th {{ text-align: left; width: 100px; color: #444; font-weight: bold; vertical-align: top; }}
                .info-table td {{ padding-bottom: 3px; vertical-align: top; }}

                table.grid {{ width: 100%; border-collapse: collapse; margin-top: 5px; font-size: 9pt; }}
                table.grid th {{ background-color: #f0f0f0; color: #333; padding: 6px; border: 1px solid #ccc; text-align: left; }}
                table.grid td {{ padding: 6px; border: 1px solid #ddd; }}
                
                .text-center {{ text-align: center; }}
                
                .summary-box {{ float: right; width: 200px; padding: 10px; border: 2px solid #ddd; text-align: center; margin-top: 10px; background-color: #fff; }}
                .final-grade {{ font-size: 18pt; font-weight: bold; display: block; margin: 5px 0; }}
                
                .footer {{ position: fixed; bottom: 0; width: 100%; text-align: center; font-size: 8pt; color: #aaa; border-top: 1px solid #eee; padding-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="header-container">
                {logo_html}
                <div class="header-text">
                    <h1>{inst_name}</h1>
                    <div class="sub-header">
                        {header_subtext}
                        <b>Sistema de Gerenciamento de Estágios</b>
                    </div>
                </div>
            </div>

            <div style="width: 49%; float: left;">
                <h2>Identificação do Aluno</h2>
                <div class="info-box">
                    <table class="info-table">
                        <tr><th>Nome:</th><td><b>{intern.name}</b></td></tr>
                        <tr><th>RA:</th><td>{intern.registration_number}</td></tr>
                        <tr><th>Semestre:</th><td>{intern.term}</td></tr>
                        <tr><th>Vigência:</th><td>{start_fmt} a {end_fmt}</td></tr>
                    </table>
                </div>
            </div>
            <div style="width: 49%; float: right;">
                <h2>Local de Estágio</h2>
                <div class="info-box">
                    {venue_html}
                </div>
            </div>
            <div style="clear: both;"></div>

            <h2>Avaliação Acadêmica</h2>
            <table class="grid">
                <thead>
                    <tr>
                        <th>Critério Avaliativo</th>
                        <th width="80" class="text-center">Peso</th>
                        <th width="80" class="text-center">Nota</th>
                    </tr>
                </thead>
                <tbody>
                    {grades_html_rows}
                </tbody>
            </table>
            
            <div style="overflow: hidden; margin-top: 10px;">
                <div class="summary-box">
                    <span style="font-size: 9pt; color: #666;">MÉDIA FINAL</span>
                    <span class="final-grade" style="color: {status_color}">{total_score:.1f}</span>
                    <span style="font-size: 10pt; font-weight: bold; color: {status_color}">{status_text}</span>
                </div>
                <div style="float: left; width: 60%;">
                     <h3>Frequência</h3>
                     <p>De <b>{total_meetings}</b> reuniões supervisionadas, o aluno compareceu a <b>{present_meetings}</b>.</p>
                     <p>Percentual de Presença: <b>{freq_percent:.1f}%</b></p>
                </div>
            </div>

            <div style="page-break-inside: avoid;">
                <h2>Status Documental</h2>
                <p>Pendências atuais: <b>{pending_docs}</b> documentos.</p>
                <table class="grid" style="width: 100%;">
                    <thead><tr><th style="text-align:left;">Documento</th><th width="120" class="text-center">Situação</th></tr></thead>
                    <tbody>{docs_rows}</tbody>
                </table>
            </div>

            <div style="page-break-inside: avoid;">
                <h2>Observações do Supervisor</h2>
                {obs_html}
            </div>

            <br><br>
            <div style="text-align: center; margin-top: 30px;">
                <p>{local_data_sig}</p>
                <br><br>
                <div style="border-top: 1px solid #000; width: 300px; margin: 0 auto;"></div>
                <p style="font-size: 9pt;">Assinatura do Responsável</p>
            </div>

            <div class="footer">
                Relatório gerado eletronicamente em {date_emission} via Intern Manager 2026.
            </div>
        </body>
        </html>
        """

        # --- 4. Renderização ---
        doc = QTextDocument()
        doc.setHtml(html)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filepath)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

        margins = QMarginsF(15, 15, 15, 15)
        printer.setPageMargins(margins, QPageLayout.Unit.Millimeter)

        doc.print_(printer)
