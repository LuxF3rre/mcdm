from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from mcdm.ahp import calculate_ahp, calculate_weighted_scores

_CR_THRESHOLD = 0.10

st.set_page_config(page_title="AHP", page_icon="⚖️", layout="wide")

st.title("⚖️ Multi-Criteria Decision Making with AHP")

st.markdown(
    "**AHP** (Analytic Hierarchy Process) derives criterion "
    "weights from pairwise comparisons using Saaty's 1-9 scale. "
    "It includes a built-in consistency check to ensure your "
    "comparisons are logically coherent."
)

with st.expander("How It Works"):
    st.markdown(
        "AHP structures a decision problem into a hierarchy "
        "of criteria and alternatives. Instead of assigning "
        "weights directly, you compare criteria **pairwise** "
        "to derive their relative importance.\n\n"
        "The algorithm follows four steps:\n\n"
        "1. **Build** a pairwise comparison matrix for criteria "
        "using Saaty's 1-9 scale\n"
        "2. **Derive weights** using the geometric mean method\n"
        "3. **Check consistency** — ensure judgments are logically coherent\n"
        "4. **Score and rank** alternatives using the derived weights"
    )

with st.expander("Saaty's Scale"):
    st.markdown(
        "| Intensity | Definition |\n"
        "|-----------|------------|\n"
        "| 1 | Equal importance |\n"
        "| 3 | Moderate importance |\n"
        "| 5 | Strong importance |\n"
        "| 7 | Very strong importance |\n"
        "| 9 | Extreme importance |\n"
        "| 2, 4, 6, 8 | Intermediate values |\n"
        "| 1/2 ... 1/9 | Reciprocals (inverse comparison) |"
    )

with st.expander("The Math"):
    st.markdown("**Step 1 — Pairwise comparison matrix**")
    st.markdown(
        "A square matrix $A$ where $a_{ij}$ represents how much "
        "criterion $i$ is preferred over criterion $j$. "
        "The diagonal is 1, and $a_{ji} = 1/a_{ij}$."
    )

    st.markdown("**Step 2 — Geometric mean method**")
    st.markdown("For each criterion $i$, compute the geometric mean of its row:")
    st.latex(r"\bar{g}_i = \left(\prod_{j=1}^{n} a_{ij}\right)^{1/n}")
    st.markdown("Normalize to get weights:")
    st.latex(r"w_i = \frac{\bar{g}_i}{\sum_{k=1}^{n} \bar{g}_k}")

    st.markdown("**Step 3 — Consistency ratio**")
    st.latex(
        r"\lambda_{\max} = \frac{1}{n}"
        r" \sum_{i=1}^{n} \frac{(A \mathbf{w})_i}{w_i}"
    )
    st.latex(r"CI = \frac{\lambda_{\max} - n}{n - 1}")
    st.latex(r"CR = \frac{CI}{RI}")
    st.markdown(
        "where $RI$ is the Random Index from Saaty's table. "
        "$CR < 0.10$ indicates acceptable consistency."
    )

    st.markdown("**Step 4 — Weighted scoring**")
    st.markdown(
        "Scores are normalized per criterion (sum normalization), "
        "then multiplied by the AHP-derived weights:"
    )
    st.latex(r"S_i = \sum_{j=1}^{n} w_j \cdot \frac{x_{ij}}{\sum_{k} x_{kj}}")

with st.expander("References"):
    st.markdown(
        "Saaty, T.L. (1980). "
        '"The Analytic Hierarchy Process". '
        "_New York: McGraw-Hill_. "
        "ISBN 978-0-07-054371-3.\n\n"
        "Saaty, T.L. (1987). "
        '"The analytic hierarchy process — what it is '
        'and how it is used". '
        "_Mathematical Modelling_. "
        "**9** (3-5): 161-176. "
        "[doi](https://en.wikipedia.org/wiki/Digital_object_identifier):"
        "[10.1016/0270-0255(87)90473-8]"
        "(https://doi.org/10.1016%2F0270-0255%2887%2990473-8)."
    )

st.divider()

_EXAMPLE_OPTIONS = ["Laptop A", "Laptop B", "Laptop C"]
_EXAMPLE_CRITERIA = ["Price", "Performance", "Battery"]

col_load, col_clear, _ = st.columns([3, 3, 6], gap="small")

with col_load:
    if st.button("Load example", width="stretch"):
        for key in (
            "ahp_options",
            "ahp_criteria",
            "ahp_comparison",
            "ahp_scores",
        ):
            st.session_state.pop(key, None)
        st.session_state["ahp_example"] = True
        st.rerun()

with col_clear:
    if st.button("Clear data", width="stretch"):
        for key in (
            "ahp_options",
            "ahp_criteria",
            "ahp_comparison",
            "ahp_scores",
            "ahp_example",
        ):
            st.session_state.pop(key, None)
        st.rerun()

_use_example = st.session_state.get("ahp_example", False)

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
    key="ahp_options",
)

st.header("Step 2: Define Criteria")
st.caption(
    "Add the criteria for evaluation. "
    "Check **Is Negative** for cost-type criteria "
    "(lower is better, e.g. price, risk). "
    "Weights will be derived from pairwise comparisons."
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
    key="ahp_criteria",
)

st.header("Step 3: Pairwise Comparisons")
st.caption(
    "Compare each pair of criteria using Saaty's 1-9 scale. "
    "A value of **3** means the left criterion is 3x more "
    "important than the right. Use **1** for equal importance."
)

criteria_list = edited_criteria["Criterion"].dropna().tolist()
criteria_list = [c for c in criteria_list if c != ""]

_pairs: list[tuple[str, str]] = [
    (criteria_list[i], criteria_list[j])
    for i in range(len(criteria_list))
    for j in range(i + 1, len(criteria_list))
]

if _use_example and criteria_list == _EXAMPLE_CRITERIA:
    comparison_df = pd.DataFrame(
        {
            "Criterion A": ["Price", "Price", "Performance"],
            "Criterion B": ["Performance", "Battery", "Battery"],
            "Value": [3.0, 5.0, 3.0],
        }
    )
elif _pairs:
    comparison_df = pd.DataFrame(
        {
            "Criterion A": [a for a, _ in _pairs],
            "Criterion B": [b for _, b in _pairs],
            "Value": [1.0] * len(_pairs),
        }
    )
else:
    comparison_df = pd.DataFrame(columns=["Criterion A", "Criterion B", "Value"])

edited_comparison = st.data_editor(
    comparison_df,
    column_config={
        "Criterion A": st.column_config.TextColumn(disabled=True),
        "Criterion B": st.column_config.TextColumn(disabled=True),
        "Value": st.column_config.NumberColumn(
            help="How many times more important is A over B?",
            min_value=0.11,
            max_value=9.0,
            format="%.4f",
        ),
    },
    hide_index=True,
    width="stretch",
    key="ahp_comparison",
)

st.header("Step 4: Scores")
st.caption(
    "Enter raw scores for each option on each criterion. "
    "No weights needed here — they come from the comparison matrix."
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
    key="ahp_scores",
)

st.divider()

st.header("Step 5: Results")

if st.button("Calculate options preference", type="primary"):
    if edited_options.empty or edited_options["Option"].isna().all():
        st.error("Please add at least one option.")
    elif not criteria_list:
        st.error("Please add at least one criterion.")
    elif edited_comparison.empty:
        st.error("Please fill in the pairwise comparisons.")
    elif edited_comparison["Value"].isna().any():
        st.error("Please fill in all comparison values.")
    else:
        # Build square matrix from pairs
        comp = pd.DataFrame(
            {c: [Decimal("1")] * len(criteria_list) for c in criteria_list},
            index=criteria_list,
        )
        for _, row in edited_comparison.iterrows():
            ca, cb = row["Criterion A"], row["Criterion B"]
            val = Decimal(str(row["Value"]))
            comp.at[ca, cb] = val  # type: ignore[invalid-assignment]
            comp.at[cb, ca] = Decimal("1") / val  # type: ignore[invalid-assignment]

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

            ranking, weights, cr = calculate_ahp(comp, scores_melted)
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
            radar_data["NormalizedScore"] = radar_data["NormalizedScore"].apply(float)
            radar_criteria = radar_data["Criterion"].unique().tolist()

            fig = go.Figure()
            for option in ranking["Option"]:
                option_data = radar_data[radar_data["Option"] == option]
                values = [
                    option_data[option_data["Criterion"] == c]["NormalizedScore"].iloc[
                        0
                    ]
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
