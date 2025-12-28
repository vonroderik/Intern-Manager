from services.evaluation_criteria_service import EvaluationCriteriaService
from core.models.evaluation_criteria import EvaluationCriteria

def seed_default_criteria(service: EvaluationCriteriaService):
    """
    Verifica se já existem critérios de avaliação. 
    Se não, cria o padrão da faculdade.
    """
    existing = service.repo.get_all()
    if len(existing) > 0:
        print("DEBUG: Critérios de avaliação já existem. Pulando seed.")
        return

    defaults = [
        EvaluationCriteria(name="Avaliação do Supervisor", weight=2.0, description="Nota dada pela empresa concedente."),
        EvaluationCriteria(name="Relatório Parcial", weight=1.0, description="Entrega na metade do estágio."),
        EvaluationCriteria(name="Relatório Final", weight=2.0, description="Documento conclusivo."),
        EvaluationCriteria(name="Apresentação de Banner", weight=1.5, description="Apresentação na feira acadêmica.")
    ]

    print("DEBUG: Criando critérios de avaliação padrão...")
    for criteria in defaults:
        service.add_new_criteria(criteria)
        print(f"   + Criado: {criteria.name}")