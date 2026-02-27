from decimal import Decimal

import pytest

from fuzzy_numbers import TriangularFuzzyNumber


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
    assert TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3")) * Decimal(
        "2"
    ) == TriangularFuzzyNumber(Decimal("2"), Decimal("4"), Decimal("6"))


def test_fuzzy_multiply() -> None:
    assert TriangularFuzzyNumber(
        Decimal("1"), Decimal("2"), Decimal("3")
    ) * TriangularFuzzyNumber(
        Decimal("2"), Decimal("3"), Decimal("4")
    ) == TriangularFuzzyNumber(Decimal("2"), Decimal("6"), Decimal("12"))


def test_scalar_divide() -> None:
    assert TriangularFuzzyNumber(Decimal("2"), Decimal("4"), Decimal("6")) / Decimal(
        "2"
    ) == TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3"))


def test_fuzzy_divide() -> None:
    assert TriangularFuzzyNumber(
        Decimal("2"), Decimal("6"), Decimal("12")
    ) / TriangularFuzzyNumber(
        Decimal("2"), Decimal("3"), Decimal("4")
    ) == TriangularFuzzyNumber(Decimal("0.5"), Decimal("2"), Decimal("6"))


def test_power_positive() -> None:
    assert TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3")) ** Decimal(
        "2"
    ) == TriangularFuzzyNumber(Decimal("1"), Decimal("4"), Decimal("9"))


def test_power_negative() -> None:
    assert TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3")) ** Decimal(
        "-2"
    ) == TriangularFuzzyNumber(
        Decimal("1") / Decimal("9"),
        Decimal("1") / Decimal(Decimal("4")),
        Decimal("1") / Decimal("1"),
    )


def test_less_than() -> None:
    assert TriangularFuzzyNumber(
        Decimal("1"), Decimal("4"), Decimal("5")
    ) < TriangularFuzzyNumber(Decimal("2"), Decimal("2"), Decimal("2"))
    assert not TriangularFuzzyNumber(
        Decimal("1"), Decimal("4"), Decimal("5")
    ) < TriangularFuzzyNumber(Decimal("0"), Decimal("2"), Decimal("2"))


def test_greater_than() -> None:
    assert TriangularFuzzyNumber(
        Decimal("1"), Decimal("1"), Decimal("10")
    ) > TriangularFuzzyNumber(Decimal("5"), Decimal("6"), Decimal("7"))
    assert not TriangularFuzzyNumber(
        Decimal("1"), Decimal("1"), Decimal("10")
    ) > TriangularFuzzyNumber(Decimal("5"), Decimal("6"), Decimal("15"))


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


def test_less_than_or_equal() -> None:
    tfn1 = TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3"))
    tfn2 = TriangularFuzzyNumber(Decimal("2"), Decimal("3"), Decimal("4"))
    tfn_same = TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("3"))

    # a < other.a → True
    assert tfn1 <= tfn2
    # Equal → True
    assert tfn1 <= tfn_same
    # a > other.a and not equal → False
    assert not tfn2 <= tfn1


def test_greater_than_or_equal() -> None:
    tfn1 = TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("5"))
    tfn2 = TriangularFuzzyNumber(Decimal("2"), Decimal("3"), Decimal("4"))
    tfn_same = TriangularFuzzyNumber(Decimal("1"), Decimal("2"), Decimal("5"))

    # c > other.c → True
    assert tfn1 >= tfn2
    # Equal → True
    assert tfn1 >= tfn_same
    # c < other.c and not equal → False
    assert not tfn2 >= tfn1


def test_membership_outside_support() -> None:
    tfn = TriangularFuzzyNumber(Decimal("2"), Decimal("5"), Decimal("8"))

    # Below a
    assert tfn.membership(Decimal("1")) == Decimal("0")
    # Above c
    assert tfn.membership(Decimal("9")) == Decimal("0")


def test_membership_ascending_side() -> None:
    tfn = TriangularFuzzyNumber(Decimal("2"), Decimal("5"), Decimal("8"))

    # At a → 0
    assert tfn.membership(Decimal("2")) == Decimal("0")
    # At b → 1
    assert tfn.membership(Decimal("5")) == Decimal("1")
    # Midpoint of ascending side: (3.5 - 2) / (5 - 2) = 0.5
    assert tfn.membership(Decimal("3.5")) == Decimal("0.5")


def test_membership_descending_side() -> None:
    tfn = TriangularFuzzyNumber(Decimal("2"), Decimal("5"), Decimal("8"))

    # At c → 0
    assert tfn.membership(Decimal("8")) == Decimal("0")
    # Midpoint of descending side: (8 - 6.5) / (8 - 5) = 0.5
    assert tfn.membership(Decimal("6.5")) == Decimal("0.5")


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
