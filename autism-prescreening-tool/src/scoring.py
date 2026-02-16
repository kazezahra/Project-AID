def qchat_score_item(question_number: int, answer_letter: str) -> int:
    """
    Implements Q-CHAT-10 scoring rules from the official scoring table.

    For Q1-Q9:
        C, D, E => 1 point
        A, B    => 0 points

    For Q10:
        A, B, C => 1 point
        D, E    => 0 points
    """
    answer_letter = answer_letter.strip().upper()

    if question_number in range(1, 10):
        return 1 if answer_letter in ["C", "D", "E"] else 0

    if question_number == 10:
        return 1 if answer_letter in ["A", "B", "C"] else 0

    raise ValueError("Q-CHAT has only 10 questions")


def compute_qchat_total_score(answers: dict) -> int:
    """
    answers format:
    {
        1: "A",
        2: "B",
        ...
        10: "C"
    }
    """
    total = 0
    for q in range(1, 11):
        total += qchat_score_item(q, answers[q])
    return total


def qchat_referral_interpretation(total_score: int) -> str:
    """
    Standard Q-CHAT-10 referral interpretation.
    Score > 3 => referral suggested
    """
    if total_score <= 3:
        return "Below Referral Threshold"
    return "Above Referral Threshold (Referral Suggested)"


def qchat_user_friendly_risk(total_score: int) -> str:
    """
    UI-friendly risk levels for parents.

    NOTE:
    This is NOT the official Q-CHAT standard.
    Official standard is referral threshold > 3.
    """
    if total_score <= 2:
        return "Low Risk"
    elif total_score == 3:
        return "Moderate Risk"
    else:
        return "High Risk"
