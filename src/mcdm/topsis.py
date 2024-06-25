from decimal import Decimal

import pandas as pd


def calculate_normalized_weighted_scores(scores: pd.DataFrame) -> pd.DataFrame:
    normalization_factor = scores
    normalization_factor["SqueredScore"] = normalization_factor["Score"] ** Decimal("2")  # type: ignore
    normalization_factor = (
        normalization_factor.groupby("Criterion")["SqueredScore"]
        .sum()
        .reset_index()
        .rename(columns={"SqueredScore": "SumOfSqueredScore"})
    )
    normalization_factor["NormalizationFactor"] = normalization_factor["SumOfSqueredScore"] ** Decimal("0.5")  # type: ignore

    normalized_weighted = scores.merge(normalization_factor, on="Criterion", how="left")
    normalized_weighted["NormalizedScore"] = normalized_weighted["Score"] / normalized_weighted["NormalizationFactor"]
    normalized_weighted["NormalizedWeightedScore"] = (
        normalized_weighted["NormalizedScore"] * normalized_weighted["Weight"]
    )

    return normalized_weighted


def calculate_ideal_best_and_worst(normalized_weighted_scores: pd.DataFrame) -> pd.DataFrame:
    positive_criteria = normalized_weighted_scores[~normalized_weighted_scores["Is Negative"]]
    best_positive = (
        positive_criteria.groupby("Criterion")["NormalizedWeightedScore"]
        .max()
        .reset_index()
        .rename(columns={"NormalizedWeightedScore": "IdealBest"})
    )
    worst_positive = (
        positive_criteria.groupby("Criterion")["NormalizedWeightedScore"]
        .min()
        .reset_index()
        .rename(columns={"NormalizedWeightedScore": "IdealWorst"})
    )

    negative_criteria = normalized_weighted_scores[normalized_weighted_scores["Is Negative"]]
    best_negative = (
        negative_criteria.groupby("Criterion")["NormalizedWeightedScore"]
        .min()
        .reset_index()
        .rename(columns={"NormalizedWeightedScore": "IdealBest"})
    )
    worst_negative = (
        negative_criteria.groupby("Criterion")["NormalizedWeightedScore"]
        .max()
        .reset_index()
        .rename(columns={"NormalizedWeightedScore": "IdealWorst"})
    )

    best_worst_positive = best_positive.merge(worst_positive, on="Criterion", how="left")
    best_worst_negative = best_negative.merge(worst_negative, on="Criterion", how="left")
    ideal_best_worst = pd.concat([best_worst_positive, best_worst_negative])

    with_ideal_best_and_worst = normalized_weighted_scores.merge(
        ideal_best_worst[["Criterion", "IdealBest", "IdealWorst"]],
        on="Criterion",
        how="left",
    )

    return with_ideal_best_and_worst


def calculate_euclidian_distance(ideal_best_and_worst: pd.DataFrame) -> pd.DataFrame:
    ideal_best_and_worst["EuclidianDistanceBest"] = (
        ideal_best_and_worst["NormalizedWeightedScore"] - ideal_best_and_worst["IdealBest"]
    ) ** Decimal("2")  # type: ignore
    ideal_best_and_worst["EuclidianDistanceWorst"] = (
        ideal_best_and_worst["NormalizedWeightedScore"] - ideal_best_and_worst["IdealWorst"]
    ) ** Decimal("2")  # type: ignore

    euclidian_distance = (
        ideal_best_and_worst.groupby("Option")[["EuclidianDistanceBest", "EuclidianDistanceWorst"]].sum().reset_index()
    )
    euclidian_distance["EuclidianDistanceBest"] = euclidian_distance["EuclidianDistanceBest"] ** Decimal("0.5")  # type: ignore
    euclidian_distance["EuclidianDistanceWorst"] = euclidian_distance["EuclidianDistanceWorst"] ** Decimal("0.5")  # type: ignore

    return euclidian_distance


def calculate_performance_score(euclidian_distance: pd.DataFrame) -> pd.DataFrame:
    euclidian_distance["Performance Score"] = euclidian_distance["EuclidianDistanceWorst"] / (
        euclidian_distance["EuclidianDistanceBest"] + euclidian_distance["EuclidianDistanceWorst"]
    )

    euclidian_distance["Rank"] = euclidian_distance["Performance Score"].rank(ascending=False)

    return euclidian_distance


def calculate_topsis(scores: pd.DataFrame) -> pd.DataFrame:
    return calculate_performance_score(
        calculate_euclidian_distance(calculate_ideal_best_and_worst(calculate_normalized_weighted_scores(scores)))
    )[["Option", "Performance Score", "Rank"]]
