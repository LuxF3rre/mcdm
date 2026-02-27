from decimal import Decimal
from functools import reduce
from operator import mul

import pandas as pd

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.ahp import (
    calculate_ahp_ranking,
    calculate_consistency_ratio,
    calculate_weighted_scores,
)


def _defuzzify(tfn: TriangularFuzzyNumber) -> Decimal:
    return (tfn.a + tfn.b + tfn.c) / Decimal("3")


def combine_comparison_matrices(
    matrices: list[pd.DataFrame],
) -> pd.DataFrame:
    criteria = matrices[0].index.tolist()
    combined = pd.DataFrame(index=criteria, columns=criteria)

    for i in criteria:
        for j in criteria:
            cell_values = [m.at[i, j] for m in matrices]
            combined.at[i, j] = TriangularFuzzyNumber.combine(cell_values)  # type: ignore[invalid-assignment,invalid-argument-type]

    return combined


def calculate_fuzzy_priority_vector(
    fuzzy_matrix: pd.DataFrame,
) -> pd.DataFrame:
    criteria = fuzzy_matrix.index.tolist()
    n = len(criteria)
    exponent = Decimal("1") / Decimal(str(n))

    fuzzy_gms: dict[str, TriangularFuzzyNumber] = {}
    for criterion in criteria:
        row_values = [fuzzy_matrix.loc[criterion, c] for c in criteria]
        product = reduce(mul, row_values)
        fuzzy_gms[criterion] = product**exponent

    total_defuzzified = sum(_defuzzify(fuzzy_gms[c]) for c in criteria)

    weights = pd.DataFrame(
        {
            "Criterion": criteria,
            "Weight": [_defuzzify(fuzzy_gms[c]) / total_defuzzified for c in criteria],
        }
    )

    return weights


def _defuzzify_matrix(fuzzy_matrix: pd.DataFrame) -> pd.DataFrame:
    criteria = fuzzy_matrix.index.tolist()
    crisp = pd.DataFrame(index=criteria, columns=criteria)

    for i in criteria:
        for j in criteria:
            crisp.at[i, j] = _defuzzify(fuzzy_matrix.at[i, j])  # type: ignore[invalid-assignment,invalid-argument-type]

    return crisp


def calculate_fuzzy_ahp(
    fuzzy_comparison_matrices: list[pd.DataFrame],
    scores: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, Decimal]:
    combined = combine_comparison_matrices(fuzzy_comparison_matrices)
    weights = calculate_fuzzy_priority_vector(combined)

    crisp_matrix = _defuzzify_matrix(combined)
    cr = calculate_consistency_ratio(crisp_matrix, weights)

    weighted = calculate_weighted_scores(scores, weights)
    ranking = calculate_ahp_ranking(weighted)

    return ranking, weights, cr
