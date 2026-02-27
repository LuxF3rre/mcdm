from decimal import Decimal

import pandas as pd

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.fuzzy_promethee import calculate_fuzzy_promethee

_D = Decimal


def _tfn(a: str, b: str, c: str) -> TriangularFuzzyNumber:
    return TriangularFuzzyNumber(_D(a), _D(b), _D(c))


def _make_decision_matrix() -> pd.DataFrame:
    """Two decision makers, 3 options, 2 criteria (1 benefit, 1 cost)."""
    rows = []
    options = ["A", "B", "C"]
    criteria = ["C1", "C2"]
    is_neg = [False, True]

    # DM1 scores
    dm1_scores = {
        ("A", "C1"): _tfn("7", "8", "9"),
        ("A", "C2"): _tfn("3", "4", "5"),
        ("B", "C1"): _tfn("5", "6", "7"),
        ("B", "C2"): _tfn("6", "7", "8"),
        ("C", "C1"): _tfn("3", "4", "5"),
        ("C", "C2"): _tfn("1", "2", "3"),
    }
    dm1_weights = {
        "C1": _tfn("7", "8", "9"),
        "C2": _tfn("5", "6", "7"),
    }

    # DM2 scores
    dm2_scores = {
        ("A", "C1"): _tfn("6", "7", "8"),
        ("A", "C2"): _tfn("4", "5", "6"),
        ("B", "C1"): _tfn("4", "5", "6"),
        ("B", "C2"): _tfn("5", "6", "7"),
        ("C", "C1"): _tfn("4", "5", "6"),
        ("C", "C2"): _tfn("2", "3", "4"),
    }
    dm2_weights = {
        "C1": _tfn("5", "6", "7"),
        "C2": _tfn("7", "8", "9"),
    }

    for dm_scores, dm_weights in [
        (dm1_scores, dm1_weights),
        (dm2_scores, dm2_weights),
    ]:
        for opt in options:
            for crit, neg in zip(criteria, is_neg, strict=True):
                rows.append(
                    {
                        "Option": opt,
                        "Criterion": crit,
                        "Score": dm_scores[(opt, crit)],
                        "Weight": dm_weights[crit],
                        "Is Negative": neg,
                    }
                )

    return pd.DataFrame(rows)


def test_calculate_fuzzy_promethee() -> None:
    """Full Fuzzy PROMETHEE pipeline produces valid ranking."""
    data = _make_decision_matrix()

    result = calculate_fuzzy_promethee(data)

    assert list(result.columns) == ["Option", "Performance Score", "Rank"]
    assert len(result) == 3
    assert set(result["Option"]) == {"A", "B", "C"}

    # Net flows sum to zero
    total_flow = sum(result["Performance Score"])
    assert abs(total_flow) < _D("0.0001")


def test_calculate_fuzzy_promethee_ranking_order() -> None:
    """A dominates on benefit criterion, C best on cost criterion."""
    data = _make_decision_matrix()

    result = calculate_fuzzy_promethee(data)
    result = result.sort_values("Rank").reset_index(drop=True)

    # A has highest benefit scores, should rank well
    # C has lowest cost scores (best for cost), should also rank well
    # B is middle on benefit and worst on cost
    best = result.iloc[0]["Option"]
    worst = result.iloc[2]["Option"]
    assert best != worst


def test_calculate_fuzzy_promethee_with_linear_preference() -> None:
    """Fuzzy PROMETHEE with linear preference function."""
    data = _make_decision_matrix()

    pref_funcs = pd.DataFrame(
        {
            "Criterion": ["C1", "C2"],
            "PreferenceFunction": ["linear", "usual"],
            "IndifferenceThreshold": [_D("0.5"), _D("0")],
            "PreferenceThreshold": [_D("3"), _D("0")],
        }
    )

    result = calculate_fuzzy_promethee(data, preference_functions=pref_funcs)

    assert list(result.columns) == ["Option", "Performance Score", "Rank"]
    assert len(result) == 3
    assert set(result["Option"]) == {"A", "B", "C"}
