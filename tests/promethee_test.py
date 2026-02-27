from decimal import Decimal

import pandas as pd

from mcdm.promethee import calculate_promethee


def test_calculate_promethee_usual() -> None:
    """3 options, 2 criteria (1 benefit, 1 cost), equal weights, usual preference."""
    data = pd.DataFrame(
        {
            "Option": ["A", "A", "B", "B", "C", "C"],
            "Criterion": ["C1", "C2", "C1", "C2", "C1", "C2"],
            "Weight": [
                Decimal("0.5"),
                Decimal("0.5"),
                Decimal("0.5"),
                Decimal("0.5"),
                Decimal("0.5"),
                Decimal("0.5"),
            ],
            "Score": [
                Decimal("10"),
                Decimal("100"),
                Decimal("20"),
                Decimal("200"),
                Decimal("15"),
                Decimal("150"),
            ],
            "Is Negative": [False, True, False, True, False, True],
        }
    )

    # Hand calculation with usual preference function:
    # C1 (benefit): B(20) > C(15) > A(10)
    # C2 (cost, lower is better): A(100) > C(150) > B(200)
    #
    # Deviations (benefit: A-B, cost: B-A):
    # C1: d(A,B)=-10, d(A,C)=-5, d(B,A)=10, d(B,C)=5, d(C,A)=5, d(C,B)=-5
    # C2: d(A,B)=100, d(A,C)=50, d(B,A)=-100, d(B,C)=-50, d(C,A)=-50, d(C,B)=50
    #
    # Usual P (1 if d>0, 0 otherwise):
    # C1: P(A,B)=0, P(A,C)=0, P(B,A)=1, P(B,C)=1, P(C,A)=1, P(C,B)=0
    # C2: P(A,B)=1, P(A,C)=1, P(B,A)=0, P(B,C)=0, P(C,A)=0, P(C,B)=1
    #
    # Aggregated (w=0.5 each, sum_w=1):
    # pi(A,B) = (0.5*0 + 0.5*1)/1 = 0.5
    # pi(A,C) = (0.5*0 + 0.5*1)/1 = 0.5
    # pi(B,A) = (0.5*1 + 0.5*0)/1 = 0.5
    # pi(B,C) = (0.5*1 + 0.5*0)/1 = 0.5
    # pi(C,A) = (0.5*1 + 0.5*0)/1 = 0.5
    # pi(C,B) = (0.5*0 + 0.5*1)/1 = 0.5
    #
    # Flows (n=3, divide by 2):
    # Phi+(A) = (pi(A,B) + pi(A,C))/2 = (0.5+0.5)/2 = 0.5
    # Phi+(B) = (pi(B,A) + pi(B,C))/2 = (0.5+0.5)/2 = 0.5
    # Phi+(C) = (pi(C,A) + pi(C,B))/2 = (0.5+0.5)/2 = 0.5
    # Phi-(A) = (pi(B,A) + pi(C,A))/2 = (0.5+0.5)/2 = 0.5
    # Phi-(B) = (pi(A,B) + pi(C,B))/2 = (0.5+0.5)/2 = 0.5
    # Phi-(C) = (pi(A,C) + pi(B,C))/2 = (0.5+0.5)/2 = 0.5
    #
    # Net: all 0.0, all rank 2.0 (tied)

    result = calculate_promethee(data)

    assert list(result.columns) == ["Option", "Performance Score", "Rank"]
    assert len(result) == 3

    for _, row in result.iterrows():
        assert row["Performance Score"] == Decimal("0")


def test_calculate_promethee_clear_winner() -> None:
    """One option dominates on all criteria."""
    data = pd.DataFrame(
        {
            "Option": ["A", "A", "B", "B", "C", "C"],
            "Criterion": ["C1", "C2", "C1", "C2", "C1", "C2"],
            "Weight": [
                Decimal("0.5"),
                Decimal("0.5"),
                Decimal("0.5"),
                Decimal("0.5"),
                Decimal("0.5"),
                Decimal("0.5"),
            ],
            "Score": [
                Decimal("30"),
                Decimal("30"),
                Decimal("20"),
                Decimal("20"),
                Decimal("10"),
                Decimal("10"),
            ],
            "Is Negative": [False, False, False, False, False, False],
        }
    )

    result = calculate_promethee(data)
    result = result.sort_values("Rank").reset_index(drop=True)

    # A dominates all — highest net flow
    assert result.iloc[0]["Option"] == "A"
    assert result.iloc[0]["Rank"] == 1.0
    # C is worst
    assert result.iloc[2]["Option"] == "C"
    assert result.iloc[2]["Rank"] == 3.0
