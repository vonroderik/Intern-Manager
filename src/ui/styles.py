# src/ui/styles.py

COLORS = {
    "primary": "#005A9E",  # Azul corporativo
    "primary_hover": "#004C87",
    "secondary": "#6C757D",  # Cinza neutro
    "success": "#107C10",  # Verde
    "warning": "#FFC107",  # Amarelo
    "danger": "#D13438",  # Vermelho
    "dark": "#323130",  # Texto escuro
    "medium": "#605E5C",  # Texto médio
    "light": "#F3F2F1",  # Fundo claro
    "white": "#FFFFFF",
    "border": "#E1DFDD",
    "sidebar_bg": "#201F1E",  # Fundo escuro da sidebar
    "sidebar_text": "#F3F2F1",
}


def get_color(key):
    return COLORS.get(key, "#000000")
