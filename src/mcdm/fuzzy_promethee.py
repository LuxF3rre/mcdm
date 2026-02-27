from decimal import Decimal

import pandas as pd

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.fuzzy_topsis import combine_decision_makers


def _defuzzify(tfn: TriangularFuzzyNumber) -> Decimal:
    return (tfn.a + tfn.b + tfn.c) / Decimal("3")


def calculate_fuzzy_deviations(combined: pd.DataFrame) -> pd.DataFrame:
    merged = combined.merge(combined, on="Criterion", suffixes=("_A", "_B"))
    merged = merged[merged["Option_A"] != merged["Option_B"]]

    merged["DeviationCrisp"] = merged.apply(
        lambda row: (
            _defuzzify(row["Score_B"]) - _defuzzify(row["Score_A"])
            if row["Is Negative_A"]
            else _defuzzify(row["Score_A"]) - _defuzzify(row["Score_B"])
        ),
        axis=1,
    )

    return merged[
        [
            "Criterion",
            "Weight_A",
            "Option_A",
            "Option_B",
            "DeviationCrisp",
            "Is Negative_A",
        ]
    ].rename(columns={"Weight_A": "Weight", "Is Negative_A": "Is Negative"})


def calculate_fuzzy_preference_degrees(
    deviations: pd.DataFrame,
    preference_functions: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if preference_functions is None:
        deviations["PreferenceDegree"] = deviations["DeviationCrisp"].apply(
            lambda d: Decimal("1") if d > 0 else Decimal("0")
        )
        return deviations

    merged = deviations.merge(preference_functions, on="Criterion", how="left")

    merged["PreferenceFunction"] = merged["PreferenceFunction"].fillna("usual")
    merged["IndifferenceThreshold"] = merged["IndifferenceThreshold"].fillna(0)
    merged["PreferenceThreshold"] = merged["PreferenceThreshold"].fillna(0)

    def _apply_preference(row: pd.Series) -> Decimal:
        d: Decimal = row["DeviationCrisp"]
        pf: str = row["PreferenceFunction"]
        q: Decimal = row["IndifferenceThreshold"]
        p: Decimal = row["PreferenceThreshold"]

        if pf == "usual":
            return Decimal("1") if d > 0 else Decimal("0")

        # linear (Type V)
        if d <= q:
            return Decimal("0")
        if d >= p:
            return Decimal("1")
        return (d - q) / (p - q)

    merged["PreferenceDegree"] = merged.apply(_apply_preference, axis=1)

    return merged[
        [
            "Criterion",
            "Weight",
            "Option_A",
            "Option_B",
            "DeviationCrisp",
            "PreferenceDegree",
        ]
    ]


def calculate_fuzzy_aggregated_preference(
    preference_degrees: pd.DataFrame,
) -> pd.DataFrame:
    preference_degrees["WeightCrisp"] = preference_degrees["Weight"].apply(
        lambda tfn: _defuzzify(tfn)  # noqa: PLW0108
    )
    preference_degrees["WeightedPreference"] = (
        preference_degrees["WeightCrisp"] * preference_degrees["PreferenceDegree"]
    )

    aggregated = (
        preference_degrees.groupby(["Option_A", "Option_B"])
        .agg({"WeightedPreference": "sum", "WeightCrisp": "sum"})
        .reset_index()
    )

    aggregated["AggregatedPreference"] = (
        aggregated["WeightedPreference"] / aggregated["WeightCrisp"]
    )

    return aggregated[["Option_A", "Option_B", "AggregatedPreference"]]


def calculate_fuzzy_flows(aggregated_preference: pd.DataFrame) -> pd.DataFrame:
    options = aggregated_preference["Option_A"].unique()
    n = len(options)

    leaving = (
        aggregated_preference.groupby("Option_A")["AggregatedPreference"]
        .sum()
        .reset_index()
        .rename(columns={"Option_A": "Option", "AggregatedPreference": "LeavingFlow"})
    )
    leaving["LeavingFlow"] = leaving["LeavingFlow"] / Decimal(str(n - 1))

    entering = (
        aggregated_preference.groupby("Option_B")["AggregatedPreference"]
        .sum()
        .reset_index()
        .rename(columns={"Option_B": "Option", "AggregatedPreference": "EnteringFlow"})
    )
    entering["EnteringFlow"] = entering["EnteringFlow"] / Decimal(str(n - 1))

    flows = leaving.merge(entering, on="Option", how="outer")
    flows["LeavingFlow"] = flows["LeavingFlow"].fillna(0)
    flows["EnteringFlow"] = flows["EnteringFlow"].fillna(0)
    flows["NetFlow"] = flows["LeavingFlow"] - flows["EnteringFlow"]

    return flows


def calculate_fuzzy_promethee_ranking(flows: pd.DataFrame) -> pd.DataFrame:
    flows["Rank"] = flows["NetFlow"].rank(ascending=False)

    return flows[["Option", "NetFlow", "Rank"]].rename(
        columns={"NetFlow": "Performance Score"}
    )


def calculate_fuzzy_promethee(
    decision_matrixes: pd.DataFrame,
    *,
    preference_functions: pd.DataFrame | None = None,
) -> pd.DataFrame:
    combined = combine_decision_makers(decision_matrixes)
    deviations = calculate_fuzzy_deviations(combined)
    preferences = calculate_fuzzy_preference_degrees(deviations, preference_functions)
    aggregated = calculate_fuzzy_aggregated_preference(preferences)
    flows = calculate_fuzzy_flows(aggregated)
    return calculate_fuzzy_promethee_ranking(flows)
