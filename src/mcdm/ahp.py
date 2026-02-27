from decimal import Decimal
from functools import reduce
from operator import mul

import pandas as pd

_MIN_CRITERIA_FOR_CR = 2

_RANDOM_INDEX: dict[int, Decimal] = {
    1: Decimal("0"),
    2: Decimal("0"),
    3: Decimal("0.58"),
    4: Decimal("0.90"),
    5: Decimal("1.12"),
    6: Decimal("1.24"),
    7: Decimal("1.32"),
    8: Decimal("1.41"),
    9: Decimal("1.45"),
    10: Decimal("1.49"),
}


def calculate_priority_vector(comparison_matrix: pd.DataFrame) -> pd.DataFrame:
    criteria = comparison_matrix.index.tolist()
    n = len(criteria)

    geometric_means: dict[str, Decimal] = {}
    for criterion in criteria:
        row_values = [comparison_matrix.loc[criterion, c] for c in criteria]
        product = reduce(mul, row_values, Decimal("1"))
        geometric_means[criterion] = product ** (Decimal("1") / Decimal(str(n)))

    total_gm = sum(geometric_means.values())

    weights = pd.DataFrame(
        {
            "Criterion": criteria,
            "Weight": [geometric_means[c] / total_gm for c in criteria],
        }
    )

    return weights


def calculate_consistency_ratio(
    comparison_matrix: pd.DataFrame,
    priority_vector: pd.DataFrame,
) -> Decimal:
    criteria = comparison_matrix.index.tolist()
    n = len(criteria)

    if n <= _MIN_CRITERIA_FOR_CR:
        return Decimal("0")

    weights = dict(
        zip(
            priority_vector["Criterion"],
            priority_vector["Weight"],
            strict=True,
        )
    )

    lambdas: list[Decimal] = []
    for criterion in criteria:
        weighted_sum = sum(
            comparison_matrix.loc[criterion, c] * weights[c] for c in criteria
        )
        lambdas.append(weighted_sum / weights[criterion])

    lambda_max = sum(lambdas) / Decimal(str(n))
    ci = (lambda_max - Decimal(str(n))) / Decimal(str(n - 1))
    ri = _RANDOM_INDEX.get(n, Decimal("1.49"))

    if ri == Decimal("0"):
        return Decimal("0")

    return ci / ri


def calculate_weighted_scores(
    scores: pd.DataFrame,
    weights: pd.DataFrame,
) -> pd.DataFrame:
    merged = scores.merge(weights, on="Criterion", how="left")

    merged["AdjustedScore"] = merged.apply(
        lambda row: Decimal("1") / row["Score"] if row["Is Negative"] else row["Score"],
        axis=1,
    )

    criterion_sums = (
        merged.groupby("Criterion")["AdjustedScore"]
        .sum()
        .reset_index()
        .rename(columns={"AdjustedScore": "CriterionSum"})
    )

    merged = merged.merge(criterion_sums, on="Criterion", how="left")
    merged["NormalizedScore"] = merged["AdjustedScore"] / merged["CriterionSum"]
    merged["WeightedScore"] = merged["NormalizedScore"] * merged["Weight"]

    return merged[["Option", "Criterion", "NormalizedScore", "Weight", "WeightedScore"]]


def calculate_ahp_ranking(weighted_scores: pd.DataFrame) -> pd.DataFrame:
    ranking = (
        weighted_scores.groupby("Option")["WeightedScore"]
        .sum()
        .reset_index()
        .rename(columns={"WeightedScore": "Performance Score"})
    )

    ranking["Rank"] = ranking["Performance Score"].rank(ascending=False)

    return ranking


def calculate_ahp(
    comparison_matrix: pd.DataFrame,
    scores: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, Decimal]:
    weights = calculate_priority_vector(comparison_matrix)
    cr = calculate_consistency_ratio(comparison_matrix, weights)
    weighted = calculate_weighted_scores(scores, weights)
    ranking = calculate_ahp_ranking(weighted)

    return ranking, weights, cr
