from typing import Optional


class EvaluationCriteria:
    """
    Domain model representing a specific assessment criteria.

    This class defines the "rules" of an evaluation, such as its name
    (e.g., "Final Report") and its weight in the final grade calculation.
    It acts as a reference table for the Grade entries.

    This class mirrors the structure of the `evaluation_criteria` table in the database.

    Attributes:
        criteria_id (Optional[int]): Unique database identifier. None if the
            criteria has not yet been persisted.
        name (str): The display name of the criteria (e.g., "Supervisor Evaluation").
        description (Optional[str]): Detailed instructions or description of the criteria.
        weight (float): The weight of this criteria in the final grade average.
            Defaults to 1.0.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        weight: float = 1.0,
        criteria_id: Optional[int] = None,
    ):
        """
        Initializes an EvaluationCriteria instance.

        Args:
            name (str): The name of the evaluation criteria.
            description (str): Optional description/instructions. Defaults to empty string.
            weight (float): The mathematical weight for this criteria. Defaults to 1.0.
            criteria_id (Optional[int]): Database identifier. None if not persisted.
        """
        self.name = name
        self.description = description
        self.weight = weight
        self.criteria_id = criteria_id

    def __repr__(self) -> str:
        return (
            f"EvaluationCriteria("
            f"id={self.criteria_id}, "
            f"name='{self.name}', "
            f"weight={self.weight}"
            f")"
        )
