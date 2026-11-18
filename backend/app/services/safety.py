from app.models.schemas import ScreeningAnswers
from typing import Tuple

def evaluate_safety_screening(answers: ScreeningAnswers, confirm_cleared: bool) -> Tuple[bool, str]:
    """
    Evaluates physical screening responses according to SAFE-01 through SAFE-12.
    Returns: (safety_hold: bool, safety_screening_status: str)
    """
    # 1. Urgent cardiovascular / systemic symptoms (SAFE-04)
    if answers.has_urgent_symptoms:
        return True, "URGENT_SYMPTOMS"

    # 2. Active injuries, physical limitations, or current unexplained pain (SAFE-02, SAFE-03)
    if answers.has_active_injury or answers.has_ongoing_limitation or answers.has_current_pain:
        return True, "HOLD"

    # 3. Resumption requires explicit confirmation that physical condition is resolved (SAFE-08)
    if not confirm_cleared:
        return True, "HOLD"

    # 4. Cleared state
    return False, "CLEARED"
