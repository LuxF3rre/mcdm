from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.fuzzy_promethee import (
    calculate_fuzzy_aggregated_preference,
    calculate_fuzzy_deviations,
    calculate_fuzzy_flows,
    calculate_fuzzy_preference_degrees,
    calculate_fuzzy_promethee_ranking,
)
from mcdm.fuzzy_topsis import combine_decision_makers

st.set_page_config(page_title="Fuzzy PROMETHEE", page_icon="🧵", layout="wide")

st.title("🧵 Multi-Criteria Decision Making with Fuzzy PROMETHEE II")

st.markdown(
    "**Fuzzy PROMETHEE** combines the pairwise comparison "
    "logic of PROMETHEE with **Triangular Fuzzy Numbers**, "
    "handling uncertainty from multiple decision makers."
)

with st.expander("How It Works"):
    st.markdown(
        "Fuzzy PROMETHEE extends PROMETHEE II by replacing crisp "
        "scores with **Triangular Fuzzy Numbers (TFNs)**, allowing "
        "multiple decision makers to express uncertainty.\n\n"
        "The algorithm follows six steps:\n\n"
        "1. **Aggregate** fuzzy inputs from multiple decision makers\n"
        "2. **Calculate deviations** using defuzzified scores\n"
        "3. **Apply preference functions** on defuzzified deviations\n"
        "4. **Aggregate** weighted preferences into a pairwise index\n"
        "5. **Compute flows** — leaving, entering, and net flow\n"
        "6. **Rank** by net flow"
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

    st.markdown("**Step 2 — Defuzzified deviations**")
    st.markdown(
        "Scores are defuzzified using the centroid method, "
        "then pairwise deviations are computed:"
    )
    st.latex(r"\text{defuzz}(\tilde{A}) = \frac{a + b + c}{3}")
    st.latex(
        r"d_j(a, b) = \text{defuzz}(\tilde{x}_{aj})"
        r" - \text{defuzz}(\tilde{x}_{bj})"
    )

    st.markdown("**Step 3 — Preference function**")
    st.markdown("Applied on the defuzzified deviation, same as crisp PROMETHEE:")
    st.latex(
        r"P_j(a, b) = \begin{cases}"
        r"1 & \text{if } d_j > 0 \\"
        r"0 & \text{otherwise}"
        r"\end{cases}"
    )

    st.markdown("**Step 4 — Aggregated preference index**")
    st.latex(
        r"\pi(a, b) = \frac{\sum_{j=1}^{n} \hat{w}_j \cdot P_j(a, b)}"
        r"{\sum_{j=1}^{n} \hat{w}_j}"
    )
    st.markdown("where $\\hat{w}_j = \\text{defuzz}(\\tilde{w}_j)$.")

    st.markdown("**Steps 5-6 — Flows and ranking**")
    st.markdown("Same as crisp PROMETHEE II:")
    st.latex(r"\Phi(a) = \Phi^{+}(a) - \Phi^{-}(a)")

with st.expander("References"):
    st.markdown(
        "Goumas, M.; Lygerou, V. (2000). "
        '"An extension of the PROMETHEE method for '
        'decision making in fuzzy environment". '
        "_European Journal of Operational Research_. "
        "**123** (3): 606-613. "
        "[doi](https://en.wikipedia.org/wiki/Digital_object_identifier):"
        "[10.1016/S0377-2217(99)00093-4]"
        "(https://doi.org/10.1016%2FS0377-2217%2899%2900093-4)."
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
                key
                in (
                    "fuzzy_promethee_options",
                    "fuzzy_promethee_criteria",
                    "fuzzy_promethee_prefs",
                )
                or key.startswith(("FPWeight", "FPScore"))
            ):
                del st.session_state[key]
        st.session_state["fuzzy_promethee_example"] = True
        st.session_state["fp_dm_slider"] = 2
        st.rerun()

with col_clear:
    if st.button("Clear data", width="stretch"):
        for key in list(st.session_state.keys()):
            if isinstance(key, str) and (
                key
                in (
                    "fuzzy_promethee_options",
                    "fuzzy_promethee_criteria",
                    "fuzzy_promethee_prefs",
                    "fuzzy_promethee_example",
                )
                or key.startswith(("FPWeight", "FPScore"))
            ):
                del st.session_state[key]
        st.session_state.pop("fp_dm_slider", None)
        st.rerun()

_use_example = st.session_state.get("fuzzy_promethee_example", False)

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
    key="fuzzy_promethee_options",
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
    key="fuzzy_promethee_criteria",
)

st.header("Step 3: Number of Decision Makers")
st.caption("Select how many decision makers will provide independent assessments.")

number_of_decision_makers = st.slider(
    "Number of decision makers", 1, 5, key="fp_dm_slider"
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
            key=f"FPWeight{decision_maker_number}",
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
            key=f"FPScore{decision_maker_number}",
            hide_index=True,
            width="stretch",
        )

st.header("Step 5: Preference Function Parameters")
st.caption(
    "Choose a preference function for each criterion. "
    "**Usual** gives strict preference for any positive deviation "
    "(q and p are ignored). "
    "**Linear** provides gradual preference between thresholds q and p."
)
st.markdown(
    "- **q (indifference):** the largest deviation that is "
    "considered negligible — below this, there is no preference "
    "at all. *Example: a $20 price difference may not matter.*\n"
    "- **p (preference):** the smallest deviation that gives "
    "full (strict) preference — at or above this, one option "
    "completely dominates the other. "
    "*Example: a $200 price gap is decisive.*\n"
    "- Between q and p, preference grows linearly from 0 to 1."
)

criteria_list_for_prefs = edited_criteria["Criterion"].dropna().tolist()
criteria_list_for_prefs = [c for c in criteria_list_for_prefs if c != ""]

if criteria_list_for_prefs:
    pref_data = pd.DataFrame(
        {
            "Criterion": criteria_list_for_prefs,
            "Preference Function": ["usual"] * len(criteria_list_for_prefs),
            "q (indifference)": [0.0] * len(criteria_list_for_prefs),
            "p (preference)": [0.0] * len(criteria_list_for_prefs),
        }
    )
else:
    pref_data = pd.DataFrame(
        columns=[
            "Criterion",
            "Preference Function",
            "q (indifference)",
            "p (preference)",
        ]
    )

edited_prefs = st.data_editor(
    pref_data,
    column_config={
        "Criterion": st.column_config.TextColumn(disabled=True),
        "Preference Function": st.column_config.SelectboxColumn(
            options=["usual", "linear"],
            default="usual",
        ),
        "q (indifference)": st.column_config.NumberColumn(min_value=0.0),
        "p (preference)": st.column_config.NumberColumn(min_value=0.0),
    },
    hide_index=True,
    width="stretch",
    key="fuzzy_promethee_prefs",
)

st.divider()

st.header("Step 6: Results")

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

        pref_funcs = None
        if not edited_prefs.empty:
            has_linear = (edited_prefs["Preference Function"] == "linear").any()
            if has_linear:
                pref_funcs = pd.DataFrame(
                    {
                        "Criterion": edited_prefs["Criterion"],
                        "PreferenceFunction": edited_prefs["Preference Function"],
                        "IndifferenceThreshold": edited_prefs["q (indifference)"].apply(
                            lambda x: Decimal(str(x))
                        ),
                        "PreferenceThreshold": edited_prefs["p (preference)"].apply(
                            lambda x: Decimal(str(x))
                        ),
                    }
                )

        combined = combine_decision_makers(decision_matrix)

        deviations = calculate_fuzzy_deviations(combined)
        preferences = calculate_fuzzy_preference_degrees(deviations, pref_funcs)
        aggregated = calculate_fuzzy_aggregated_preference(preferences)
        flows = calculate_fuzzy_flows(aggregated)

        result = calculate_fuzzy_promethee_ranking(flows)
        result = result.sort_values("Rank").reset_index(drop=True)

        st.success(
            f"Analysis complete — **{result.iloc[0]['Option']}** ranks first.",
            icon="🏆",
        )
        st.dataframe(result, hide_index=True, width="stretch")

        # Flow bar chart
        flow_data = flows.copy()
        flow_data["LeavingFlow"] = flow_data["LeavingFlow"].apply(float)
        flow_data["EnteringFlow"] = flow_data["EnteringFlow"].apply(lambda x: -float(x))
        flow_data["NetFlow"] = flow_data["NetFlow"].apply(float)

        fig_bar = go.Figure()
        fig_bar.add_trace(
            go.Bar(
                name="Leaving Flow (Φ+)",
                x=flow_data["Option"],
                y=flow_data["LeavingFlow"],
                marker_color="#a6da95",
            )
        )
        fig_bar.add_trace(
            go.Bar(
                name="Entering Flow (-Phi-)",
                x=flow_data["Option"],
                y=flow_data["EnteringFlow"],
                marker_color="#ed8796",
            )
        )
        fig_bar.add_trace(
            go.Scatter(
                name="Net Flow (Φ)",
                x=flow_data["Option"],
                y=flow_data["NetFlow"],
                mode="markers+lines",
                marker={"color": "#8aadf4", "size": 10},
                line={"color": "#8aadf4", "width": 2},
            )
        )
        fig_bar.update_layout(
            title="Fuzzy PROMETHEE II Flows",
            barmode="relative",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#cad3f5",
            yaxis_title="Flow Value",
            margin={"t": 60, "b": 30, "l": 60, "r": 60},
        )
        st.plotly_chart(fig_bar, width="stretch")

        # Radar chart using defuzzified scores
        radar_combined = combined[["Option", "Criterion", "Score"]].copy()
        radar_combined["Score"] = radar_combined["Score"].apply(
            lambda tfn: float(tfn.b)
        )
        criteria_list = radar_combined["Criterion"].unique().tolist()

        fig = go.Figure()
        for option in result["Option"]:
            option_data = radar_combined[radar_combined["Option"] == option]
            values = [
                option_data[option_data["Criterion"] == c]["Score"].iloc[0]
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
