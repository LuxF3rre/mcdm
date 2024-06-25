from decimal import Decimal

import pytest

from mcdm_app.fuzzy_numbers import TriangularFuzzyNumber


def test_absolute_zero_scale() -> None:
    with pytest.raises(ValueError):
        TriangularFuzzyNumber(Decimal("-1"), Decimal("2"), Decimal("3"))
    with pytest.raises(ValueError):
        TriangularFuzzyNumber(Decimal("1"), Decimal("-2"), Decimal("3"))
    with pytest.raises(ValueError):
        TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("-3"))


def test_elements_assumptions_scale() -> None:
    with pytest.raises(ValueError):
        TriangularFuzzyNumber(Decimal("2"), Decimal("4"), Decimal("3"))
    with pytest.raises(ValueError):
        TriangularFuzzyNumber(Decimal("5"), Decimal("3"), Decimal("4"))


def test_combine() -> None:
    assert TriangularFuzzyNumber.combine(
        [
            TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3")),
            TriangularFuzzyNumber(Decimal("0"), Decimal("4"), Decimal("5")),
            TriangularFuzzyNumber(Decimal("0"), Decimal("6"), Decimal("7")),
        ],
        how=None,
    ) == TriangularFuzzyNumber(Decimal("0"), Decimal("4"), Decimal("7"))

    assert TriangularFuzzyNumber.combine(
        [
            TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3")),
            TriangularFuzzyNumber(Decimal("0"), Decimal("4"), Decimal("5")),
            TriangularFuzzyNumber(Decimal("0"), Decimal("6"), Decimal("7")),
        ],
        how="max",
    ) == TriangularFuzzyNumber(Decimal("1"), Decimal("6"), Decimal("7"))

    assert TriangularFuzzyNumber.combine(
        [
            TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3")),
            TriangularFuzzyNumber(Decimal("0"), Decimal("4"), Decimal("5")),
            TriangularFuzzyNumber(Decimal("0"), Decimal("6"), Decimal("7")),
        ],
        how="min",
    ) == TriangularFuzzyNumber(Decimal("0"), Decimal("2"), Decimal("3"))


def test_scalar_multiply() -> None:
    assert TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3")) * Decimal("2") == TriangularFuzzyNumber(
        Decimal("2"), Decimal("4"), Decimal("6")
    )


def test_fuzzy_multiply() -> None:
    assert TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3")) * TriangularFuzzyNumber(
        Decimal("2"), Decimal("3"), Decimal("4")
    ) == TriangularFuzzyNumber(Decimal("2"), Decimal("6"), Decimal("12"))


def test_scalar_divide() -> None:
    assert TriangularFuzzyNumber(Decimal("2"), Decimal("4"), Decimal("6")) / Decimal("2") == TriangularFuzzyNumber(
        Decimal("1"), Decimal("2"), Decimal("3")
    )


def test_fuzzy_divide() -> None:
    assert TriangularFuzzyNumber(Decimal("2"), Decimal("6"), Decimal("12")) / TriangularFuzzyNumber(
        Decimal("2"), Decimal("3"), Decimal("4")
    ) == TriangularFuzzyNumber(Decimal("0.5"), Decimal("2"), Decimal("6"))


def test_power_positive() -> None:
    assert TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3")) ** Decimal("2") == TriangularFuzzyNumber(
        Decimal("1"), Decimal("4"), Decimal("9")
    )


def test_power_negative() -> None:
    assert TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3")) ** Decimal("-2") == TriangularFuzzyNumber(
        Decimal("1") / Decimal("9"), Decimal("1") / Decimal(Decimal("4")), Decimal("1") / Decimal("1")
    )


def test_less_than() -> None:
    assert TriangularFuzzyNumber(Decimal("1"), Decimal("4"), Decimal("5")) < TriangularFuzzyNumber(
        Decimal("2"), Decimal("2"), Decimal("2")
    )
    assert not TriangularFuzzyNumber(Decimal("1"), Decimal("4"), Decimal("5")) < TriangularFuzzyNumber(
        Decimal("0"), Decimal("2"), Decimal("2")
    )


def test_greater_than() -> None:
    assert TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("10")) > TriangularFuzzyNumber(
        Decimal("5"), Decimal("6"), Decimal("7")
    )
    assert not TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("10")) > TriangularFuzzyNumber(
        Decimal("5"), Decimal("6"), Decimal("15")
    )


def test_min() -> None:
    assert min(
        TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("10")),
        TriangularFuzzyNumber(Decimal("5"), Decimal("6"), Decimal("7")),
    ) == TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("10"))
    assert min(
        TriangularFuzzyNumber(Decimal("5"), Decimal("6"), Decimal("7")),
        TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("10")),
    ) == TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("10"))


def test_max() -> None:
    assert max(
        TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("10")),
        TriangularFuzzyNumber(Decimal("5"), Decimal("6"), Decimal("7")),
    ) == TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("10"))
    assert max(
        TriangularFuzzyNumber(Decimal("5"), Decimal("6"), Decimal("7")),
        TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("10")),
    ) == TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("10"))


def test_euclidean_distance() -> None:
    assert TriangularFuzzyNumber.euclidean_distance(
        TriangularFuzzyNumber(
            Decimal("2"),
            Decimal("2"),
            Decimal("2"),
        ),
        TriangularFuzzyNumber(
            Decimal("0"),
            Decimal("0"),
            Decimal("0"),
        ),
    ) == Decimal("2")
