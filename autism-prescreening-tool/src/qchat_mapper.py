from typing import Dict


def qchat_answer_to_binary(question_number: int, answer_letter: str) -> int:
    """
    Converts Q-CHAT-10 answer (A/B/C/D/E) into 0/1 score per official scoring.

    Q1-Q9:
        C, D, E => 1
        A, B    => 0

    Q10:
        A, B, C => 1
        D, E    => 0
    """
    answer_letter = str(answer_letter).strip().upper()

    if answer_letter not in ["A", "B", "C", "D", "E"]:
        raise ValueError(f"Invalid answer '{answer_letter}'. Must be A/B/C/D/E.")

    if 1 <= question_number <= 9:
        return 1 if answer_letter in ["C", "D", "E"] else 0

    if question_number == 10:
        return 1 if answer_letter in ["A", "B", "C"] else 0

    raise ValueError("Q-CHAT only has questions 1..10")


def map_qchat_answers_to_features(qchat_answers: Dict[int, str]) -> Dict[str, int]:
    """
    Input example:
    {
        1: "A",
        2: "C",
        ...
        10: "B"
    }

    Output:
    {
        "a1": 0,
        "a2": 1,
        ...
        "a10": 1
    }
    """
    features = {}

    for q in range(1, 11):
        if q not in qchat_answers:
            raise ValueError(f"Missing answer for question {q}")

        features[f"a{q}"] = qchat_answer_to_binary(q, qchat_answers[q])

    return features


def compute_qchat_total_score(mapped_features: Dict[str, int]) -> int:
    """
    Computes total Q-CHAT score (0..10) from a1..a10.
    """
    return sum(mapped_features[f"a{i}"] for i in range(1, 11))
