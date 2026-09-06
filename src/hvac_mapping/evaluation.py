"""Human-label evaluation metrics for mapping with abstention."""

from __future__ import annotations

import pandas as pd


VALID_DECISIONS = {
    "correct_as_predicted", "incorrect_mapping", "valid_abstention",
    "missed_mapping", "insufficient_evidence", "out_of_scope",
}


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def evaluate_labels(labels: pd.DataFrame) -> dict:
    decisions = labels["reviewer_decision"].fillna("").astype(str).str.strip()
    invalid = sorted(set(decisions) - VALID_DECISIONS - {""})
    if invalid:
        raise ValueError(f"Invalid decisions: {invalid}")
    counts = decisions[decisions.ne("")].value_counts()
    correct = int(counts.get("correct_as_predicted", 0))
    incorrect = int(counts.get("incorrect_mapping", 0))
    valid_abstain = int(counts.get("valid_abstention", 0))
    missed = int(counts.get("missed_mapping", 0))
    evaluable = correct + incorrect + valid_abstain + missed
    return {
        "records": int(len(labels)),
        "reviewed": int(decisions.ne("").sum()),
        "selective_precision": _rate(correct, correct + incorrect),
        "abstention_validity": _rate(valid_abstain, valid_abstain + missed),
        "overall_decision_accuracy": _rate(correct + valid_abstain, evaluable),
    }
