from decimal import Decimal

import pandas as pd

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.fuzzy_ahp import (
    calculate_fuzzy_ahp,
    calculate_fuzzy_priority_vector,
    combine_comparison_matrices,
)

_D = Decimal
_ONE = TriangularFuzzyNumber(_D("1"), _D("1"), _D("1"))


def _tfn(a: str, b: str, c: str) -> TriangularFuzzyNumber:
    return TriangularFuzzyNumber(_D(a), _D(b), _D(c))


def _reciprocal(tfn: TriangularFuzzyNumber) -> TriangularFuzzyNumber:
    return TriangularFuzzyNumber(_D("1") / tfn.c, _D("1") / tfn.b, _D("1") / tfn.a)


def _make_fuzzy_comparison(
    criteria: list[str],
) -> pd.DataFrame:
    """3x3 fuzzy comparison matrix: C1 > C2 > C3."""
    tfn_3 = _tfn("2", "3", "4")
    tfn_5 = _tfn("4", "5", "6")
    tfn_mid = _tfn("1", "2", "3")

    matrix = pd.DataFrame(index=criteria, columns=criteria)
    for c in criteria:
        matrix.at[c, c] = _ONE  # type: ignore[invalid-assignment]

    matrix.at[criteria[0], criteria[1]] = tfn_3  # type: ignore[invalid-assignment]
    matrix.at[criteria[1], criteria[0]] = _reciprocal(tfn_3)  # type: ignore[invalid-assignment]
    matrix.at[criteria[0], criteria[2]] = tfn_5  # type: ignore[invalid-assignment]
    matrix.at[criteria[2], criteria[0]] = _reciprocal(tfn_5)  # type: ignore[invalid-assignment]
    matrix.at[criteria[1], criteria[2]] = tfn_mid  # type: ignore[invalid-assignment]
    matrix.at[criteria[2], criteria[1]] = _reciprocal(tfn_mid)  # type: ignore[invalid-assignment]

    return matrix


def test_combine_comparison_matrices() -> None:
    """Combining two matrices produces valid TFN cells."""
    criteria = ["C1", "C2", "C3"]
    m1 = _make_fuzzy_comparison(criteria)
    m2 = _make_fuzzy_comparison(criteria)

    combined = combine_comparison_matrices([m1, m2])

    assert combined.shape == (3, 3)
    # Diagonal should remain (1,1,1)
    for c in criteria:
        cell = combined.at[c, c]
        assert isinstance(cell, TriangularFuzzyNumber)
        assert cell.a == _D("1")
        assert cell.b == _D("1")
        assert cell.c == _D("1")


def test_calculate_fuzzy_priority_vector() -> None:
    """Fuzzy priority vector weights sum to 1."""
    criteria = ["C1", "C2", "C3"]
    matrix = _make_fuzzy_comparison(criteria)

    weights = calculate_fuzzy_priority_vector(matrix)

    assert list(weights.columns) == ["Criterion", "Weight"]
    assert len(weights) == 3

    total = sum(weights["Weight"])
    assert abs(total - _D("1")) < _D("0.0001")

    # C1 should have highest weight
    w = dict(zip(weights["Criterion"], weights["Weight"], strict=True))
    assert w["C1"] > w["C2"] > w["C3"]


def test_calculate_fuzzy_ahp() -> None:
    """Full Fuzzy AHP pipeline with 2 decision makers."""
    criteria = ["Price", "Quality", "Speed"]
    m1 = _make_fuzzy_comparison(criteria)
    m2 = _make_fuzzy_comparison(criteria)

    scores = pd.DataFrame(
        {
            "Option": ["A", "A", "A", "B", "B", "B", "C", "C", "C"],
            "Criterion": criteria * 3,
            "Score": [
                _D("500"),
                _D("8"),
                _D("90"),
                _D("300"),
                _D("6"),
                _D("70"),
                _D("700"),
                _D("9"),
                _D("80"),
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

    ranking, weights, cr = calculate_fuzzy_ahp([m1, m2], scores)

    assert list(ranking.columns) == ["Option", "Performance Score", "Rank"]
    assert len(ranking) == 3
    assert list(weights.columns) == ["Criterion", "Weight"]
    assert cr < _D("0.10")
    assert set(ranking["Option"]) == {"A", "B", "C"}
