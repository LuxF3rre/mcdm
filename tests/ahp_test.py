from decimal import Decimal

import pandas as pd

from mcdm.ahp import (
    calculate_ahp,
    calculate_consistency_ratio,
    calculate_priority_vector,
)

_ONE = Decimal("1")
_THREE = Decimal("3")
_FIVE = Decimal("5")


def _make_3x3_comparison(criteria: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            criteria[0]: [_ONE, _ONE / _THREE, _ONE / _FIVE],
            criteria[1]: [_THREE, _ONE, _ONE / _THREE],
            criteria[2]: [_FIVE, _THREE, _ONE],
        },
        index=criteria,
    )


def test_calculate_priority_vector() -> None:
    """Classic 3x3 Saaty example."""
    criteria = ["C1", "C2", "C3"]
    comparison = _make_3x3_comparison(criteria)

    weights = calculate_priority_vector(comparison)

    assert list(weights.columns) == ["Criterion", "Weight"]
    assert len(weights) == 3

    # Weights should sum to 1
    total = sum(weights["Weight"])
    assert abs(total - Decimal("1")) < Decimal("0.0001")

    # C1 has highest weight (most important), C3 lowest
    w = dict(zip(weights["Criterion"], weights["Weight"], strict=True))
    assert w["C1"] > w["C2"] > w["C3"]


def test_calculate_consistency_ratio() -> None:
    """CR should be < 0.10 for a consistent 3x3 matrix."""
    criteria = ["C1", "C2", "C3"]
    comparison = _make_3x3_comparison(criteria)

    weights = calculate_priority_vector(comparison)
    cr = calculate_consistency_ratio(comparison, weights)

    assert cr < Decimal("0.10")


def test_calculate_ahp() -> None:
    """Full AHP pipeline with 3 options, 3 criteria."""
    criteria = ["Price", "Quality", "Speed"]
    comparison = _make_3x3_comparison(criteria)

    scores = pd.DataFrame(
        {
            "Option": [
                "A",
                "A",
                "A",
                "B",
                "B",
                "B",
                "C",
                "C",
                "C",
            ],
            "Criterion": criteria * 3,
            "Score": [
                Decimal("500"),
                Decimal("8"),
                Decimal("90"),
                Decimal("300"),
                Decimal("6"),
                Decimal("70"),
                Decimal("700"),
                Decimal("9"),
                Decimal("80"),
            ],
            "Is Negative": [
                True,
                False,
                False,
                True,
                False,
                False,
                True,
                False,
                False,
            ],
        }
    )

    ranking, weights, cr = calculate_ahp(comparison, scores)

    assert list(ranking.columns) == [
        "Option",
        "Performance Score",
        "Rank",
    ]
    assert len(ranking) == 3
    assert list(weights.columns) == ["Criterion", "Weight"]
    assert cr < Decimal("0.10")

    # Verify ranking has all options
    assert set(ranking["Option"]) == {"A", "B", "C"}


def test_consistency_ratio_two_criteria() -> None:
    """CR should be 0 for n<=2 (always consistent by definition)."""
    criteria = ["C1", "C2"]
    comparison = pd.DataFrame(
        {
            criteria[0]: [_ONE, _ONE / _THREE],
            criteria[1]: [_THREE, _ONE],
        },
        index=criteria,
    )

    weights = calculate_priority_vector(comparison)
    cr = calculate_consistency_ratio(comparison, weights)

    assert cr == Decimal("0")
