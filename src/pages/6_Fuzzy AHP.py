from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.ahp import calculate_weighted_scores
from mcdm.fuzzy_ahp import calculate_fuzzy_ahp

_CR_THRESHOLD = 0.10

st.set_page_config(page_title="Fuzzy AHP", page_icon="🪢", layout="wide")

st.title("🪢 Multi-Criteria Decision Making with Fuzzy AHP")

st.markdown(
    "**Fuzzy AHP** extends the Analytic Hierarchy Process with "
    "**Triangular Fuzzy Numbers** for pairwise comparisons, "
    "allowing multiple decision makers to express uncertainty "
    "in their judgments. Uses Buckley's geometric mean method."
)

with st.expander("How It Works"):
    st.markdown(
        "Fuzzy AHP (Buckley's method) replaces crisp pairwise "
        "comparisons with **Triangular Fuzzy Numbers (TFNs)**, "
        "capturing the vagueness in human judgment.\n\n"
        "The algorithm follows five steps:\n\n"
        "1. **Collect** fuzzy pairwise comparison matrices from "
        "multiple decision makers\n"
        "2. **Aggregate** matrices using TFN combination\n"
        "3. **Derive fuzzy weights** via fuzzy geometric mean, "
        "then defuzzify\n"
        "4. **Check consistency** on the defuzzified matrix\n"
        "5. **Score and rank** alternatives using the derived weights"
    )

with st.expander("Fuzzy Comparison Scale"):
    st.markdown(
        "| Linguistic term | TFN |\n"
        "|----------------|-----|\n"
        "| Equal importance | (1, 1, 1) |\n"
        "| Slightly more important | (1, 2, 3) |\n"
        "| Moderately more important | (2, 3, 4) |\n"
        "| More important | (3, 4, 5) |\n"
        "| Strongly more important | (4, 5, 6) |\n"
        "| Very strongly more important | (5, 6, 7) |\n"
        "| Demonstrably more important | (6, 7, 8) |\n"
        "| Extremely more important | (7, 8, 9) |\n"
        "| Absolutely more important | (8, 9, 9) |"
    )

with st.expander("The Math"):
    st.markdown("**Step 1 — Aggregating comparison matrices**")
    st.markdown(
        "Given $K$ decision makers, their fuzzy comparisons "
        "$\\tilde{a}_{ij}^k = (a^k, b^k, c^k)$ are combined:"
    )
    st.latex(
        r"\tilde{a}_{ij} = \left("
        r"\min_k\, a_{ij}^k,\;"
        r"\frac{1}{K}\sum_{k=1}^{K} b_{ij}^k,\;"
        r"\max_k\, c_{ij}^k"
        r"\right)"
    )

    st.markdown("**Step 2 — Fuzzy geometric mean (Buckley's method)**")
    st.latex(r"\tilde{g}_i = \left(\prod_{j=1}^{n} \tilde{a}_{ij}\right)^{1/n}")
    st.markdown("where TFN product and power are computed component-wise.")

    st.markdown("**Step 3 — Defuzzified weights**")
    st.latex(r"\hat{g}_i = \frac{a_i + b_i + c_i}{3}")
    st.latex(r"w_i = \frac{\hat{g}_i}{\sum_{k=1}^{n} \hat{g}_k}")

    st.markdown("**Step 4 — Consistency check**")
    st.markdown(
        "The combined fuzzy matrix is defuzzified (centroid method) "
        "and the standard AHP consistency ratio is computed on the "
        "crisp matrix."
    )

with st.expander("References"):
    st.markdown(
        "Buckley, J.J. (1985). "
        '"Fuzzy hierarchical analysis". '
        "_Fuzzy Sets and Systems_. "
        "**17** (3): 233-247. "
        "[doi](https://en.wikipedia.org/wiki/Digital_object_identifier):"
        "[10.1016/0165-0114(85)90090-9]"
        "(https://doi.org/10.1016%2F0165-0114%2885%2990090-9)."
    )

st.divider()

_EXAMPLE_OPTIONS = ["Laptop A", "Laptop B", "Laptop C"]
_EXAMPLE_CRITERIA = ["Price", "Performance", "Battery"]

col_load, col_clear, _ = st.columns([3, 3, 6], gap="small")

with col_load:
    if st.button("Load example", width="stretch"):
        for key in list(st.session_state.keys()):
            if isinstance(key, str) and (
                key
                in (
                    "fuzzy_ahp_options",
                    "fuzzy_ahp_criteria",
                    "fuzzy_ahp_scores",
                )
                or key.startswith("FAHPComp")
            ):
                del st.session_state[key]
        st.session_state["fuzzy_ahp_example"] = True
        st.session_state["fahp_dm_slider"] = 2
        st.rerun()

with col_clear:
    if st.button("Clear data", width="stretch"):
        for key in list(st.session_state.keys()):
            if isinstance(key, str) and (
                key
                in (
                    "fuzzy_ahp_options",
                    "fuzzy_ahp_criteria",
                    "fuzzy_ahp_scores",
                    "fuzzy_ahp_example",
                )
                or key.startswith("FAHPComp")
            ):
                del st.session_state[key]
        st.session_state.pop("fahp_dm_slider", None)
        st.rerun()

_use_example = st.session_state.get("fuzzy_ahp_example", False)

st.header("Step 1: Define Options")
st.caption(
    "Add the alternatives you want to compare. Click the **+** button to add rows."
)

if _use_example:
    options = pd.DataFrame({"Option": _EXAMPLE_OPTIONS})
else:
    options = pd.DataFrame(columns=["Option"])

edited_options = st.data_editor(
    options,
    num_rows="dynamic",
    width="stretch",
    key="fuzzy_ahp_options",
)

st.header("Step 2: Define Criteria")
st.caption(
    "Add the criteria for evaluation. "
    "Check **Is Negative** for cost-type criteria "
    "(lower is better, e.g. price, risk). "
    "Weights will be derived from fuzzy pairwise comparisons."
)

if _use_example:
    criteria_df = pd.DataFrame(
        {
            "Criterion": _EXAMPLE_CRITERIA,
            "Is Negative": [True, False, False],
        }
    )
else:
    criteria_df = pd.DataFrame(columns=["Criterion", "Is Negative"])
criteria_df["Is Negative"] = criteria_df["Is Negative"].astype(bool)

edited_criteria = st.data_editor(
    criteria_df,
    num_rows="dynamic",
    width="stretch",
    key="fuzzy_ahp_criteria",
)

st.header("Step 3: Number of Decision Makers")
st.caption("Select how many decision makers will provide independent assessments.")

number_of_decision_makers = st.slider(
    "Number of decision makers", 1, 5, key="fahp_dm_slider"
)

st.header("Step 4: Pairwise Comparisons")
st.caption(
    "For each decision maker, compare pairs of criteria "
    "as Triangular Fuzzy Numbers (Min, Likely, Max). "
    "A value like (3, 4, 5) means Criterion A is roughly "
    "4x more important than Criterion B."
)

criteria_list = edited_criteria["Criterion"].dropna().tolist()
criteria_list = [c for c in criteria_list if c != ""]

_pairs: list[tuple[str, str]] = [
    (criteria_list[i], criteria_list[j])
    for i in range(len(criteria_list))
    for j in range(i + 1, len(criteria_list))
]

_example_comparisons = {
    0: {
        ("Price", "Performance"): (1.0, 2.0, 3.0),
        ("Price", "Battery"): (3.0, 4.0, 5.0),
        ("Performance", "Battery"): (1.0, 2.0, 3.0),
    },
    1: {
        ("Price", "Performance"): (2.0, 3.0, 4.0),
        ("Price", "Battery"): (4.0, 5.0, 6.0),
        ("Performance", "Battery"): (1.0, 2.0, 3.0),
    },
}

comparison_dicts = {}

dm_tabs = st.tabs([f"Decision Maker {i + 1}" for i in range(number_of_decision_makers)])

for dm_num in range(number_of_decision_makers):
    with dm_tabs[dm_num]:
        if _pairs:
            if _use_example and dm_num in _example_comparisons:
                ex = _example_comparisons[dm_num]
                comp_df = pd.DataFrame(
                    {
                        "Criterion A": [a for a, _ in _pairs],
                        "Criterion B": [b for _, b in _pairs],
                        "Min": [ex.get(p, (1.0, 1.0, 1.0))[0] for p in _pairs],
                        "Likely": [ex.get(p, (1.0, 1.0, 1.0))[1] for p in _pairs],
                        "Max": [ex.get(p, (1.0, 1.0, 1.0))[2] for p in _pairs],
                    }
                )
            else:
                comp_df = pd.DataFrame(
                    {
                        "Criterion A": [a for a, _ in _pairs],
                        "Criterion B": [b for _, b in _pairs],
                        "Min": [1.0] * len(_pairs),
                        "Likely": [1.0] * len(_pairs),
                        "Max": [1.0] * len(_pairs),
                    }
                )

            comparison_dicts[dm_num] = st.data_editor(
                comp_df,
                column_config={
                    "Criterion A": st.column_config.TextColumn(disabled=True),
                    "Criterion B": st.column_config.TextColumn(disabled=True),
                    "Min": st.column_config.NumberColumn(min_value=0.11, max_value=9.0),
                    "Likely": st.column_config.NumberColumn(
                        min_value=0.11, max_value=9.0
                    ),
                    "Max": st.column_config.NumberColumn(min_value=0.11, max_value=9.0),
                },
                hide_index=True,
                width="stretch",
                key=f"FAHPComp{dm_num}",
            )
        else:
            st.info("Define criteria first.")
            comparison_dicts[dm_num] = pd.DataFrame()

st.header("Step 5: Scores")
st.caption(
    "Enter raw scores for each option on each criterion. "
    "No weights needed here — they come from the fuzzy comparison matrices."
)

options_list = edited_options["Option"].tolist()

if _use_example and options_list == _EXAMPLE_OPTIONS:
    scores_data = pd.DataFrame(
        {
            "Criterion": _EXAMPLE_CRITERIA,
            "Is Negative": [True, False, False],
            "Laptop A": [999.0, 85.0, 8.0],
            "Laptop B": [1299.0, 95.0, 6.0],
            "Laptop C": [799.0, 70.0, 10.0],
        }
    )
else:
    scores_data = pd.DataFrame(
        columns=[
            "Criterion",
            "Is Negative",
            *options_list,
        ]
    )
scores_data["Is Negative"] = scores_data["Is Negative"].astype(bool)

edited_scores = st.data_editor(
    scores_data,
    num_rows="dynamic",
    width="stretch",
    key="fuzzy_ahp_scores",
)

st.divider()

st.header("Step 6: Results")

if st.button("Calculate options preference", type="primary"):
    if edited_options.empty or edited_options["Option"].isna().all():
        st.error("Please add at least one option.")
    elif not criteria_list:
        st.error("Please add at least one criterion.")
    else:
        # Build fuzzy comparison matrices from pairs
        fuzzy_matrices = []
        all_valid = True

        for dm_num in range(number_of_decision_makers):
            comp_edited = comparison_dicts[dm_num]
            if comp_edited.empty:
                st.error(f"Please fill in comparisons for Decision Maker {dm_num + 1}.")
                all_valid = False
                break

            if comp_edited[["Min", "Likely", "Max"]].isna().any().any():
                st.error(
                    "Please fill in all comparison values for "
                    f"Decision Maker {dm_num + 1}."
                )
                all_valid = False
                break

            _one = TriangularFuzzyNumber(Decimal("1"), Decimal("1"), Decimal("1"))
            matrix = pd.DataFrame(index=criteria_list, columns=criteria_list)
            for c in criteria_list:
                matrix.at[c, c] = _one  # type: ignore[invalid-assignment]

            for _, pair_row in comp_edited.iterrows():
                ca = pair_row["Criterion A"]
                cb = pair_row["Criterion B"]
                tfn = TriangularFuzzyNumber(
                    Decimal(str(pair_row["Min"])),
                    Decimal(str(pair_row["Likely"])),
                    Decimal(str(pair_row["Max"])),
                )
                matrix.at[ca, cb] = tfn  # type: ignore[invalid-assignment]
                matrix.at[cb, ca] = TriangularFuzzyNumber(  # type: ignore[invalid-assignment]
                    Decimal("1") / tfn.c,
                    Decimal("1") / tfn.b,
                    Decimal("1") / tfn.a,
                )

            fuzzy_matrices.append(matrix)

        if all_valid:
            # Prepare scores
            scores_melted = edited_scores.melt(
                id_vars=["Criterion", "Is Negative"],
                var_name="Option",
                value_name="Score",
            )
            if scores_melted["Score"].isna().any():
                st.error("Please fill in all scores.")
            else:
                scores_melted["Score"] = scores_melted["Score"].apply(
                    lambda x: Decimal(str(x))
                )
                scores_melted["Is Negative"] = (
                    scores_melted["Is Negative"].fillna(False).infer_objects(copy=False)
                )

                ranking, weights, cr = calculate_fuzzy_ahp(
                    fuzzy_matrices, scores_melted
                )
                ranking = ranking.sort_values("Rank").reset_index(drop=True)

                st.success(
                    f"Analysis complete — **{ranking.iloc[0]['Option']}** ranks first.",
                    icon="🏆",
                )

                # Display derived weights
                st.subheader("Derived Weights")
                weights_display = weights.copy()
                weights_display["Weight"] = weights_display["Weight"].apply(
                    lambda x: float(round(x, 4))
                )
                st.dataframe(weights_display, hide_index=True, width="stretch")

                # Display consistency ratio
                cr_float = float(round(cr, 4))
                if cr_float < _CR_THRESHOLD:
                    st.success(
                        f"Consistency Ratio: **{cr_float}** (< 0.10 — consistent)",
                        icon="✅",
                    )
                else:
                    st.warning(
                        f"Consistency Ratio: **{cr_float}** (>= 0.10 — "
                        "consider revising your comparisons)",
                        icon="⚠️",
                    )

                # Display ranking
                st.subheader("Ranking")
                st.dataframe(ranking, hide_index=True, width="stretch")

                # Radar chart
                weighted = calculate_weighted_scores(scores_melted, weights)
                radar_data = weighted[["Option", "Criterion", "NormalizedScore"]].copy()
                radar_data["NormalizedScore"] = radar_data["NormalizedScore"].apply(
                    float
                )
                radar_criteria = radar_data["Criterion"].unique().tolist()

                fig = go.Figure()
                for option in ranking["Option"]:
                    option_data = radar_data[radar_data["Option"] == option]
                    values = [
                        option_data[option_data["Criterion"] == c][
                            "NormalizedScore"
                        ].iloc[0]
                        for c in radar_criteria
                    ]
                    values.append(values[0])
                    fig.add_trace(
                        go.Scatterpolar(
                            r=values,
                            theta=[*radar_criteria, radar_criteria[0]],
                            name=str(option),
                            fill="toself",
                            opacity=0.6,
                        )
                    )

                fig.update_layout(
                    title="Options Comparison by Criteria",
                    polar={
                        "bgcolor": "rgba(0,0,0,0)",
                        "radialaxis": {"visible": True},
                    },
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#cad3f5",
                    legend_title_text="Option",
                    margin={"t": 60, "b": 30, "l": 60, "r": 60},
                )

                st.plotly_chart(fig, width="stretch")

st.divider()

st.markdown(
    "<div style='text-align: center'>Made with ❤ by Maurycy Blaszczak"
    " (<a href='https://maurycyblaszczak.com/'>maurycyblaszczak.com</a>)</div>",
    unsafe_allow_html=True,
)
