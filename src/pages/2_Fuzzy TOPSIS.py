from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.fuzzy_topsis import (
    calculate_fuzzy_topsis,
    calculate_normalized_fuzzy_decision_matrix,
    calculate_weighted_normalized_fuzzy_decision_matrix,
    combine_decision_makers,
)

st.set_page_config(page_title="Fuzzy TOPSIS", page_icon="🧶", layout="wide")

st.title("🧶 Multi-Criteria Decision Making with Fuzzy TOPSIS")

st.markdown(
    "**Fuzzy TOPSIS** works like regular TOPSIS, but lets "
    "you use ranges instead of exact numbers. This is useful "
    "when scores are subjective or when several people are "
    "weighing in with different perspectives."
)

with st.expander("How It Works"):
    st.markdown(
        "Fuzzy TOPSIS extends the classical TOPSIS method by replacing "
        "crisp numbers with **Triangular Fuzzy Numbers (TFNs)**, allowing "
        "decision makers to express uncertainty and subjectivity in their "
        "evaluations.\n\n"
        "The algorithm follows six steps:\n\n"
        "1. **Aggregate** inputs from multiple decision makers into a single "
        "fuzzy decision matrix\n"
        "2. **Normalize** the fuzzy matrix — benefit criteria are divided "
        "by the column max; cost criteria are inverted\n"
        "3. **Apply fuzzy weights** to get the weighted normalized matrix\n"
        "4. **Determine fuzzy ideal solutions** — the best and worst "
        "fuzzy values for each criterion\n"
        "5. **Compute distances** from each alternative to both fuzzy ideals "
        "using a Euclidean metric for TFNs\n"
        "6. **Rank** alternatives by their closeness coefficient"
    )

with st.expander("Triangular Fuzzy Numbers"):
    st.markdown(
        'Instead of saying "this scores exactly 7", '
        "a **Triangular Fuzzy Number** lets you say "
        '"somewhere between 5 and 9, most likely 7". '
        "It captures the uncertainty in a simple way.\n\n"
        "A TFN $\\tilde{A} = (a, b, c)$ where $a \\leq b \\leq c$ "
        "has a triangular membership function:"
    )
    st.latex(
        r"\mu_{\tilde{A}}(x) = \begin{cases}"
        r"\dfrac{x - a}{b - a} & a \leq x \leq b \\[6pt]"
        r"\dfrac{c - x}{c - b} & b \leq x \leq c \\[6pt]"
        r"0 & \text{otherwise}"
        r"\end{cases}"
    )
    st.markdown(
        "The membership value $\\mu = 1$ at $x = b$ (the peak) "
        "and tapers linearly to $0$ at the endpoints $a$ and $c$."
    )

    st.markdown("**Arithmetic operations on TFNs:**")
    st.markdown(
        "Given $\\tilde{A} = (a_1, b_1, c_1)$ and $\\tilde{B} = (a_2, b_2, c_2)$:"
    )
    st.latex(r"\tilde{A} \times \tilde{B} \approx (a_1 a_2,\; b_1 b_2,\; c_1 c_2)")
    st.latex(
        r"\tilde{A} \div \tilde{B} \approx "
        r"\left(\frac{a_1}{c_2},\; \frac{b_1}{b_2},\; \frac{c_1}{a_2}\right)"
    )
    st.markdown(
        "Division inverts the order of the divisor's components to "
        "preserve the fuzzy interval correctly."
    )

with st.expander("The Math"):
    st.markdown("**Step 1 — Aggregating decision makers**")
    st.markdown(
        "Given $K$ decision makers, their fuzzy scores $\\tilde{x}_{ij}^k = "
        "(a_{ij}^k, b_{ij}^k, c_{ij}^k)$ "
        "are combined into a single TFN:"
    )
    st.latex(
        r"\tilde{x}_{ij} = \left("
        r"\min_k\, a_{ij}^k,\;"
        r"\frac{1}{K}\sum_{k=1}^{K} b_{ij}^k,\;"
        r"\max_k\, c_{ij}^k"
        r"\right)"
    )

    st.markdown("**Step 2 — Fuzzy normalization**")
    st.markdown("For **benefit** criteria (higher is better):")
    st.latex(
        r"\tilde{r}_{ij} = \left("
        r"\frac{a_{ij}}{c_j^*},\;"
        r"\frac{b_{ij}}{c_j^*},\;"
        r"\frac{c_{ij}}{c_j^*}"
        r"\right), \quad c_j^* = \max_i\, c_{ij}"
    )
    st.markdown("For **cost** criteria (lower is better):")
    st.latex(
        r"\tilde{r}_{ij} = \left("
        r"\frac{a_j^{-}}{c_{ij}},\;"
        r"\frac{a_j^{-}}{b_{ij}},\;"
        r"\frac{a_j^{-}}{a_{ij}}"
        r"\right), \quad a_j^{-} = \min_i\, a_{ij}"
    )

    st.markdown("**Step 3 — Weighted normalized fuzzy matrix**")
    st.latex(r"\tilde{v}_{ij} = \tilde{w}_j \times \tilde{r}_{ij}")
    st.markdown(
        "where $\\tilde{w}_j$ is the aggregated fuzzy weight for criterion $j$."
    )

    st.markdown("**Step 4 — Fuzzy ideal solutions**")
    st.latex(
        r"A^{+} = \left\{\tilde{v}_1^{+}, \ldots, \tilde{v}_n^{+}\right\}, \quad "
        r"\tilde{v}_j^{+} = \left("
        r"\max_i\, a_{ij},\; \max_i\, b_{ij},\; \max_i\, c_{ij}\right)"
    )
    st.latex(
        r"A^{-} = \left\{\tilde{v}_1^{-}, \ldots, \tilde{v}_n^{-}\right\}, \quad "
        r"\tilde{v}_j^{-} = \left("
        r"\min_i\, a_{ij},\; \min_i\, b_{ij},\; \min_i\, c_{ij}\right)"
    )

    st.markdown("**Step 5 — Distance from fuzzy ideal solutions**")
    st.markdown(
        "The Euclidean distance between two TFNs "
        "$\\tilde{A} = (a_1, b_1, c_1)$ and $\\tilde{B} = (a_2, b_2, c_2)$ is:"
    )
    st.latex(
        r"d(\tilde{A}, \tilde{B}) = "
        r"\sqrt{\frac{1}{3}\left["
        r"(a_1 - a_2)^2 + (b_1 - b_2)^2 + (c_1 - c_2)^2"
        r"\right]}"
    )
    st.markdown("Total distances for alternative $i$:")
    st.latex(r"D_i^{+} = \sum_{j=1}^{n} d(\tilde{v}_{ij},\, \tilde{v}_j^{+})")
    st.latex(r"D_i^{-} = \sum_{j=1}^{n} d(\tilde{v}_{ij},\, \tilde{v}_j^{-})")

    st.markdown("**Step 6 — Closeness coefficient**")
    st.latex(r"CC_i = \frac{D_i^{-}}{D_i^{+} + D_i^{-}}, \quad CC_i \in [0, 1]")
    st.markdown(
        "$CC_i = 1$ means the alternative perfectly matches the fuzzy ideal best. "
        "Alternatives are ranked in descending order of $CC_i$."
    )

with st.expander("References"):
    st.markdown(
        "El Alaoui, M. (2021). "
        '"Fuzzy TOPSIS: Logic, Approaches, and Case Studies". '
        "_New York: CRC Press_. "
        "[doi](https://en.wikipedia.org/wiki/Digital_object_identifier):"
        "[10.1201/9781003168416](https://doi.org/10.1201%2F9781003168416). "
        "ISBN 978-0-367-76748-8. S2CID 233525185."
    )

st.divider()

_EXAMPLE_OPTIONS = ["Laptop A", "Laptop B", "Laptop C"]
_EXAMPLE_CRITERIA = ["Price", "Quality", "Design"]
_EXAMPLE_IS_NEGATIVE = [True, False, False]

col_load, col_clear, _ = st.columns([3, 3, 6], gap="small")

with col_load:
    if st.button("Load example", width="stretch"):
        for key in list(st.session_state.keys()):
            if isinstance(key, str) and (
                key in ("fuzzy_options", "fuzzy_criteria")
                or key.startswith(("Weight", "Score"))
            ):
                del st.session_state[key]
        st.session_state["fuzzy_example"] = True
        st.session_state["dm_slider"] = 2
        st.rerun()

with col_clear:
    if st.button("Clear data", width="stretch"):
        for key in list(st.session_state.keys()):
            if isinstance(key, str) and (
                key in ("fuzzy_options", "fuzzy_criteria", "fuzzy_example")
                or key.startswith(("Weight", "Score"))
            ):
                del st.session_state[key]
        st.session_state.pop("dm_slider", None)
        st.rerun()

_use_example = st.session_state.get("fuzzy_example", False)

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
    key="fuzzy_options",
)

st.header("Step 2: Define Criteria")
st.caption(
    "Add the criteria for evaluation. "
    "Check **Is Negative** for cost-type criteria "
    "(lower is better, e.g. price, risk)."
)

if _use_example:
    criteria = pd.DataFrame(
        {
            "Criterion": _EXAMPLE_CRITERIA,
            "Is Negative": _EXAMPLE_IS_NEGATIVE,
        }
    )
else:
    criteria = pd.DataFrame(columns=["Criterion", "Is Negative"])
criteria["Is Negative"] = criteria["Is Negative"].astype(bool)

edited_criteria = st.data_editor(
    criteria,
    num_rows="dynamic",
    width="stretch",
    key="fuzzy_criteria",
)

st.header("Step 3: Number of Decision Makers")
st.caption("Select how many decision makers will provide independent assessments.")

number_of_decision_makers = st.slider(
    "Number of decision makers", 1, 5, key="dm_slider"
)

st.header("Step 4: Scores and Weights")
st.caption(
    "For each decision maker, enter **weights** "
    "(importance of each criterion) and **scores** "
    "(rating of each option per criterion) "
    "as Triangular Fuzzy Numbers (Min, Likely, Max)."
)

weights = edited_criteria.drop(columns="Is Negative")
weights["Min"] = None
weights["Likely"] = None
weights["Max"] = None

scores = edited_options.merge(edited_criteria, how="cross").drop(columns="Is Negative")
scores["Min"] = None
scores["Likely"] = None
scores["Max"] = None

for column in ["Min", "Likely", "Max"]:
    weights[column] = weights[column].astype(float)
    scores[column] = scores[column].astype(float)

_example_weights = {
    0: pd.DataFrame(
        {
            "Criterion": _EXAMPLE_CRITERIA,
            "Min": [7.0, 5.0, 3.0],
            "Likely": [8.0, 6.0, 4.0],
            "Max": [9.0, 7.0, 5.0],
        }
    ),
    1: pd.DataFrame(
        {
            "Criterion": _EXAMPLE_CRITERIA,
            "Min": [5.0, 7.0, 3.0],
            "Likely": [6.0, 8.0, 4.0],
            "Max": [7.0, 9.0, 5.0],
        }
    ),
}
_example_scores = {
    0: pd.DataFrame(
        {
            "Option": [
                "Laptop A",
                "Laptop A",
                "Laptop A",
                "Laptop B",
                "Laptop B",
                "Laptop B",
                "Laptop C",
                "Laptop C",
                "Laptop C",
            ],
            "Criterion": _EXAMPLE_CRITERIA * 3,
            "Min": [5.0, 7.0, 5.0, 3.0, 8.0, 6.0, 7.0, 4.0, 7.0],
            "Likely": [6.0, 8.0, 6.0, 4.0, 9.0, 7.0, 8.0, 5.0, 8.0],
            "Max": [7.0, 9.0, 7.0, 5.0, 10.0, 8.0, 9.0, 6.0, 9.0],
        }
    ),
    1: pd.DataFrame(
        {
            "Option": [
                "Laptop A",
                "Laptop A",
                "Laptop A",
                "Laptop B",
                "Laptop B",
                "Laptop B",
                "Laptop C",
                "Laptop C",
                "Laptop C",
            ],
            "Criterion": _EXAMPLE_CRITERIA * 3,
            "Min": [4.0, 6.0, 6.0, 2.0, 7.0, 5.0, 6.0, 5.0, 8.0],
            "Likely": [5.0, 7.0, 7.0, 3.0, 8.0, 6.0, 7.0, 6.0, 9.0],
            "Max": [6.0, 8.0, 8.0, 4.0, 9.0, 7.0, 8.0, 7.0, 10.0],
        }
    ),
}

weights_dict = {}
scores_dict = {}

dm_tabs = st.tabs([f"Decision Maker {i + 1}" for i in range(number_of_decision_makers)])

for decision_maker_number in range(number_of_decision_makers):
    with dm_tabs[decision_maker_number]:
        st.subheader("Weights")
        st.caption("How important is each criterion? Enter as (Min, Likely, Max).")

        if _use_example and decision_maker_number in _example_weights:
            dm_weights = _example_weights[decision_maker_number]
        else:
            dm_weights = weights

        weights_dict[decision_maker_number] = st.data_editor(
            dm_weights,
            key=f"Weight{decision_maker_number}",
            hide_index=True,
            width="stretch",
        )

        st.subheader("Scores")
        st.caption(
            "How does each option perform on each "
            "criterion? Enter as (Min, Likely, Max)."
        )

        if _use_example and decision_maker_number in _example_scores:
            dm_scores = _example_scores[decision_maker_number]
        else:
            dm_scores = scores

        scores_dict[decision_maker_number] = st.data_editor(
            dm_scores,
            key=f"Score{decision_maker_number}",
            hide_index=True,
            width="stretch",
        )

st.divider()

st.header("Step 5: Results")

if st.button("Calculate options preference", type="primary"):
    if edited_options.empty or edited_options["Option"].isna().all():
        st.error("Please add at least one option.")
    elif edited_criteria.empty or edited_criteria["Criterion"].isna().all():
        st.error("Please add at least one criterion.")
    else:
        decision_matrix = pd.DataFrame(
            columns=["Option", "Criterion", "Weight", "Score"]
        )
        for decision_maker_number in range(number_of_decision_makers):
            scores_dict[decision_maker_number]["Min"] = scores_dict[
                decision_maker_number
            ]["Min"].apply(lambda x: Decimal(str(x)))
            scores_dict[decision_maker_number]["Likely"] = scores_dict[
                decision_maker_number
            ]["Likely"].apply(lambda x: Decimal(str(x)))
            scores_dict[decision_maker_number]["Max"] = scores_dict[
                decision_maker_number
            ]["Max"].apply(lambda x: Decimal(str(x)))

            scores_dict[decision_maker_number]["Score"] = scores_dict[
                decision_maker_number
            ].apply(
                lambda row: TriangularFuzzyNumber(
                    row["Min"],
                    row["Likely"],
                    row["Max"],
                ),
                axis=1,
            )
            scores_dict[decision_maker_number] = scores_dict[
                decision_maker_number
            ].drop(columns=["Min", "Likely", "Max"])

            weights_dict[decision_maker_number]["Min"] = weights_dict[
                decision_maker_number
            ]["Min"].apply(lambda x: Decimal(str(x)))
            weights_dict[decision_maker_number]["Likely"] = weights_dict[
                decision_maker_number
            ]["Likely"].apply(lambda x: Decimal(str(x)))
            weights_dict[decision_maker_number]["Max"] = weights_dict[
                decision_maker_number
            ]["Max"].apply(lambda x: Decimal(str(x)))

            weights_dict[decision_maker_number]["Weight"] = weights_dict[
                decision_maker_number
            ].apply(
                lambda row: TriangularFuzzyNumber(
                    row["Min"],
                    row["Likely"],
                    row["Max"],
                ),
                axis=1,
            )

            weights_dict[decision_maker_number] = weights_dict[
                decision_maker_number
            ].drop(columns=["Min", "Likely", "Max"])

            merged = (
                scores_dict[decision_maker_number]
                .merge(weights_dict[decision_maker_number], on="Criterion", how="left")
                .merge(edited_criteria, on="Criterion", how="left")
            )

            decision_matrix = pd.concat([decision_matrix, merged])

        decision_matrix["Is Negative"] = (
            decision_matrix["Is Negative"].infer_objects(copy=False).fillna(False)
        )

        weighted_normalized = calculate_weighted_normalized_fuzzy_decision_matrix(
            calculate_normalized_fuzzy_decision_matrix(
                combine_decision_makers(decision_matrix.copy())
            )
        )

        fuzzy_topsis = calculate_fuzzy_topsis(decision_matrix)
        fuzzy_topsis = fuzzy_topsis.sort_values("Rank").reset_index(drop=True)

        st.success(
            f"Analysis complete — **{fuzzy_topsis.iloc[0]['Option']}** ranks first.",
            icon="🏆",
        )
        st.dataframe(fuzzy_topsis, hide_index=True, width="stretch")

        radar_data = weighted_normalized[
            ["Option", "Criterion", "WeightedNormalizedScore"]
        ].copy()
        radar_data["WeightedNormalizedScore"] = radar_data[
            "WeightedNormalizedScore"
        ].apply(lambda tfn: float(tfn.b))

        criteria_list = radar_data["Criterion"].unique().tolist()

        fig = go.Figure()
        for option in fuzzy_topsis["Option"]:
            option_data = radar_data[radar_data["Option"] == option]
            values = [
                option_data[option_data["Criterion"] == c][
                    "WeightedNormalizedScore"
                ].iloc[0]
                for c in criteria_list
            ]
            values.append(values[0])
            fig.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=[*criteria_list, criteria_list[0]],
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
