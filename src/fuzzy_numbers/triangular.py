from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TriangularFuzzyNumber:
    a: Decimal
    b: Decimal
    c: Decimal

    def __post_init__(self) -> None:
        if self.a < 0 or self.b < 0 or self.c < 0:
            raise ValueError
        if not (self.a <= self.b <= self.c):
            raise ValueError

    def __mul__(
        self, other: "TriangularFuzzyNumber | Decimal"
    ) -> "TriangularFuzzyNumber":
        if isinstance(other, TriangularFuzzyNumber):
            return TriangularFuzzyNumber(
                self.a * other.a,
                self.b * other.b,
                self.c * other.c,
            )
        return TriangularFuzzyNumber(
            self.a * other,
            self.b * other,
            self.c * other,
        )

    def __truediv__(
        self, other: "TriangularFuzzyNumber | Decimal"
    ) -> "TriangularFuzzyNumber":
        if isinstance(other, TriangularFuzzyNumber):
            return TriangularFuzzyNumber(
                self.a / other.c,
                self.b / other.b,
                self.c / other.a,
            )
        return TriangularFuzzyNumber(
            self.a / other,
            self.b / other,
            self.c / other,
        )

    def __pow__(self, other: Decimal) -> "TriangularFuzzyNumber":
        if other < 0:
            return TriangularFuzzyNumber(
                Decimal("1") / (self.c ** abs(other)),
                Decimal("1") / (self.b ** abs(other)),
                Decimal("1") / (self.a ** abs(other)),
            )
        return TriangularFuzzyNumber(
            self.a**other,
            self.b**other,
            self.c**other,
        )

    def __lt__(self, other: "TriangularFuzzyNumber") -> bool:
        return self.a < other.a

    def __le__(self, other: "TriangularFuzzyNumber") -> bool:
        return self.a < other.a or self == other

    def __gt__(self, other: "TriangularFuzzyNumber") -> bool:
        return self.c > other.c

    def __ge__(self, other: "TriangularFuzzyNumber") -> bool:
        return self.c > other.c or self == other

    def membership(self, other: Decimal) -> Decimal:
        if other < self.a or other > self.c:
            return Decimal("0")
        if self.a <= other <= self.b:
            return (other - self.a) / (self.b - self.a)
        # self.b <= other <= self.c case
        return (self.c - other) / (self.c - self.b)

    @staticmethod
    def combine(
        fuzzy_numbers: list["TriangularFuzzyNumber"],
        how: str | None = None,
    ) -> "TriangularFuzzyNumber":
        if how == "max":
            return TriangularFuzzyNumber(
                max(number.a for number in fuzzy_numbers),
                max(number.b for number in fuzzy_numbers),
                max(number.c for number in fuzzy_numbers),
            )

        if how == "min":
            return TriangularFuzzyNumber(
                min(number.a for number in fuzzy_numbers),
                min(number.b for number in fuzzy_numbers),
                min(number.c for number in fuzzy_numbers),
            )

        return TriangularFuzzyNumber(
            min(number.a for number in fuzzy_numbers),
            sum(number.b for number in fuzzy_numbers) / Decimal(len(fuzzy_numbers)),
            max(number.c for number in fuzzy_numbers),
        )

    @staticmethod
    def euclidean_distance(
        left: "TriangularFuzzyNumber",
        right: "TriangularFuzzyNumber",
    ) -> Decimal:
        return (
            (
                (left.a - right.a) ** Decimal("2")
                + (left.b - right.b) ** Decimal("2")
                + (left.c - right.c) ** Decimal("2")
            )
            / Decimal("3")
        ) ** Decimal("0.5")
