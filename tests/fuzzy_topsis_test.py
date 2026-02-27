from decimal import Decimal

import pandas as pd

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.fuzzy_topsis import (
    calculate_closeness_coefficient,
    calculate_distance_from_solutions,
    calculate_fuzzy_topsis,
    calculate_ideal_solutions,
    calculate_normalized_fuzzy_decision_matrix,
    calculate_weighted_normalized_fuzzy_decision_matrix,
    combine_decision_makers,
)

_D = Decimal


def _tfn(a: str, b: str, c: str) -> TriangularFuzzyNumber:
    return TriangularFuzzyNumber(_D(a), _D(b), _D(c))


def _make_decision_matrix() -> pd.DataFrame:
    """Two decision makers, 3 options, 2 criteria (1 benefit, 1 cost)."""
    rows = []
    options = ["A", "B", "C"]
    criteria = ["C1", "C2"]
    is_neg = [False, True]

    dm1 = {
        "scores": {
            ("A", "C1"): _tfn("7", "8", "9"),
            ("A", "C2"): _tfn("3", "4", "5"),
            ("B", "C1"): _tfn("5", "6", "7"),
            ("B", "C2"): _tfn("6", "7", "8"),
            ("C", "C1"): _tfn("8", "9", "10"),
            ("C", "C2"): _tfn("2", "3", "4"),
        },
        "weights": {
            "C1": _tfn("7", "8", "9"),
            "C2": _tfn("5", "6", "7"),
        },
    }

    dm2 = {
        "scores": {
            ("A", "C1"): _tfn("6", "7", "8"),
            ("A", "C2"): _tfn("4", "5", "6"),
            ("B", "C1"): _tfn("4", "5", "6"),
            ("B", "C2"): _tfn("5", "6", "7"),
            ("C", "C1"): _tfn("7", "8", "9"),
            ("C", "C2"): _tfn("3", "4", "5"),
        },
        "weights": {
            "C1": _tfn("5", "6", "7"),
            "C2": _tfn("7", "8", "9"),
        },
    }

    for dm in [dm1, dm2]:
        for opt in options:
            for crit, neg in zip(criteria, is_neg, strict=True):
                rows.append(
                    {
                        "Option": opt,
                        "Criterion": crit,
                        "Score": dm["scores"][(opt, crit)],
                        "Weight": dm["weights"][crit],
                        "Is Negative": neg,
                    }
                )

    return pd.DataFrame(rows)


def test_combine_decision_makers() -> None:
    """Combining 2 DMs produces one row per (Option, Criterion)."""
    data = _make_decision_matrix()

    combined = combine_decision_makers(data)

    # 3 options * 2 criteria = 6 rows
    assert len(combined) == 6

    for _, row in combined.iterrows():
        assert isinstance(row["Score"], TriangularFuzzyNumber)
        assert isinstance(row["Weight"], TriangularFuzzyNumber)


def test_calculate_normalized_fuzzy_decision_matrix() -> None:
    """Normalized scores are TFNs with values in [0, 1]."""
    data = _make_decision_matrix()
    combined = combine_decision_makers(data)

    normalized = calculate_normalized_fuzzy_decision_matrix(combined)

    assert "NormalizedScore" in normalized.columns
    for _, row in normalized.iterrows():
        ns = row["NormalizedScore"]
        assert isinstance(ns, TriangularFuzzyNumber)
        # All components should be between 0 and ~1
        assert ns.a >= _D("0")
        assert ns.c <= _D("1.01")  # small tolerance


def test_calculate_weighted_normalized_fuzzy_decision_matrix() -> None:
    """Weighted normalized scores are TFNs."""
    data = _make_decision_matrix()
    combined = combine_decision_makers(data)
    normalized = calculate_normalized_fuzzy_decision_matrix(combined)

    weighted = calculate_weighted_normalized_fuzzy_decision_matrix(normalized)

    assert "WeightedNormalizedScore" in weighted.columns
    for _, row in weighted.iterrows():
        assert isinstance(row["WeightedNormalizedScore"], TriangularFuzzyNumber)


def test_calculate_ideal_solutions() -> None:
    """Ideal solutions add IdealBest and IdealWorst columns."""
    data = _make_decision_matrix()
    combined = combine_decision_makers(data)
    normalized = calculate_normalized_fuzzy_decision_matrix(combined)
    weighted = calculate_weighted_normalized_fuzzy_decision_matrix(normalized)

    with_ideal = calculate_ideal_solutions(weighted)

    assert "IdealBest" in with_ideal.columns
    assert "IdealWorst" in with_ideal.columns
    for _, row in with_ideal.iterrows():
        assert isinstance(row["IdealBest"], TriangularFuzzyNumber)
        assert isinstance(row["IdealWorst"], TriangularFuzzyNumber)


def test_calculate_distance_from_solutions() -> None:
    """Distances are non-negative Decimals."""
    data = _make_decision_matrix()
    combined = combine_decision_makers(data)
    normalized = calculate_normalized_fuzzy_decision_matrix(combined)
    weighted = calculate_weighted_normalized_fuzzy_decision_matrix(normalized)
    with_ideal = calculate_ideal_solutions(weighted)

    with_dist = calculate_distance_from_solutions(with_ideal)

    assert "DistanceBest" in with_dist.columns
    assert "DistanceWorst" in with_dist.columns
    for _, row in with_dist.iterrows():
        assert row["DistanceBest"] >= _D("0")
        assert row["DistanceWorst"] >= _D("0")


def test_calculate_closeness_coefficient() -> None:
    """Closeness coefficients are between 0 and 1."""
    data = _make_decision_matrix()
    combined = combine_decision_makers(data)
    normalized = calculate_normalized_fuzzy_decision_matrix(combined)
    weighted = calculate_weighted_normalized_fuzzy_decision_matrix(normalized)
    with_ideal = calculate_ideal_solutions(weighted)
    with_dist = calculate_distance_from_solutions(with_ideal)

    result = calculate_closeness_coefficient(with_dist)

    assert "ClosenessCoefficient" in result.columns
    assert "Rank" in result.columns
    assert len(result) == 3
    for _, row in result.iterrows():
        cc = row["ClosenessCoefficient"]
        assert _D("0") <= cc <= _D("1")


def test_calculate_fuzzy_topsis() -> None:
    """Full Fuzzy TOPSIS pipeline produces valid ranking."""
    data = _make_decision_matrix()

    result = calculate_fuzzy_topsis(data)

    assert list(result.columns) == ["Option", "Performance Score", "Rank"]
    assert len(result) == 3
    assert set(result["Option"]) == {"A", "B", "C"}

    # All performance scores between 0 and 1
    for _, row in result.iterrows():
        assert _D("0") <= row["Performance Score"] <= _D("1")


def test_calculate_fuzzy_topsis_ranking_order() -> None:
    """C has highest benefit and lowest cost, should rank first."""
    data = _make_decision_matrix()

    result = calculate_fuzzy_topsis(data)
    result = result.sort_values("Rank").reset_index(drop=True)

    # C: highest on C1 (benefit), lowest on C2 (cost) → best
    assert result.iloc[0]["Option"] == "C"
    assert result.iloc[0]["Rank"] == 1.0
