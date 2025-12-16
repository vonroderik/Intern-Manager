from datetime import datetime
import re
from typing import Any

DATE_INPUT_FORMAT = "%d/%m/%Y"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def validate_email_format(email: str):
    """Verifica se a string é um e-mail válido."""
    if not re.match(EMAIL_REGEX, email):
        raise ValueError("Verifique o formato do e-mail.")


def validate_date_range(start_date_str: str, end_date_str: str) -> None:
    """Valida se as datas estão no formato DD/MM/AAAA e se o fim é posterior ao início."""
    try:
        dt_start = datetime.strptime(start_date_str, DATE_INPUT_FORMAT)
        dt_end = datetime.strptime(end_date_str, DATE_INPUT_FORMAT)
    except ValueError:
        raise ValueError(f"O formato de data deve ser {DATE_INPUT_FORMAT}.")

    if dt_end <= dt_start:
        raise ValueError("A data de encerramento deve ser posterior à data de início.")


def validate_required_fields(data_object: Any, fields_map: dict):
    """
    Checa a existência de campos obrigatórios em um objeto (Intern, Venue, etc.).

    Args:
        data_object: O objeto (Intern, Venue) a ser verificado.
        fields_map: Um dicionário {atributo_do_objeto: 'Nome Amigável para o Erro'}.
    """
    missing = []
    for attr, ui_attr_name in fields_map.items():
        if not getattr(data_object, attr):
            missing.append(ui_attr_name)

    if missing:
        raise ValueError(
            f"Você precisa preencher os dados obrigatórios: {', '.join(missing)}"
        )
