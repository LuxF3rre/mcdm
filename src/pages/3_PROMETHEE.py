from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from mcdm.promethee import (
    calculate_aggregated_preference_index,
    calculate_deviations,
    calculate_flows,
    calculate_preference_degrees,
    calculate_promethee_ranking,
)

st.set_page_config(page_title="PROMETHEE", page_icon="📊", layout="wide")

st.title("📊 Multi-Criteria Decision Making with PROMETHEE II")

st.markdown(
    "**PROMETHEE II** ranks your options by comparing them "
    "pairwise on each criterion. It measures how much each "
    "option outperforms the others, producing a complete "
    "ranking based on net preference flows."
)

with st.expander("How It Works"):
    st.markdown(
        "PROMETHEE (Preference Ranking Organization METHod for "
        "Enrichment Evaluations) compares every pair of alternatives "
        "on each criterion using a **preference function**.\n\n"
        "The algorithm follows five steps:\n\n"
        "1. **Calculate deviations** between every pair of "
        "alternatives on each criterion\n"
        "2. **Apply a preference function** to convert deviations "
        "into preference degrees (0 to 1)\n"
        "3. **Aggregate** weighted preference degrees into an "
        "overall preference index for each pair\n"
        "4. **Compute flows** — leaving flow (how much an option "
        "dominates others), entering flow (how much it is dominated)\n"
        "5. **Rank** by net flow (leaving minus entering)"
    )

with st.expander("The Math"):
    st.markdown("**Step 1 — Deviations**")
    st.markdown("For each criterion $j$ and pair of alternatives $(a, b)$:")
    st.latex(r"d_j(a, b) = g_j(a) - g_j(b)")
    st.markdown(
        "where $g_j$ is the score on criterion $j$. "
        "For cost criteria the sign is reversed."
    )

    st.markdown("**Step 2 — Preference function**")
    st.markdown("**Usual (Type I):** strict preference if any positive deviation:")
    st.latex(
        r"P_j(a, b) = \begin{cases}"
        r"1 & \text{if } d_j(a, b) > 0 \\"
        r"0 & \text{otherwise}"
        r"\end{cases}"
    )
    st.markdown(
        "**Linear (Type V):** gradual preference between "
        "indifference threshold $q$ and preference threshold $p$:"
    )
    st.latex(
        r"P_j(a, b) = \begin{cases}"
        r"0 & \text{if } d_j \leq q \\"
        r"\dfrac{d_j - q}{p - q} & \text{if } q < d_j < p \\"
        r"1 & \text{if } d_j \geq p"
        r"\end{cases}"
    )

    st.markdown("**Step 3 — Aggregated preference index**")
    st.latex(
        r"\pi(a, b) = \frac{\sum_{j=1}^{n} w_j \cdot P_j(a, b)}"
        r"{\sum_{j=1}^{n} w_j}"
    )

    st.markdown("**Step 4 — Flows**")
    st.latex(
        r"\Phi^{+}(a) = \frac{1}{m-1} \sum_{b \neq a} \pi(a, b)"
        r"\quad \text{(leaving flow)}"
    )
    st.latex(
        r"\Phi^{-}(a) = \frac{1}{m-1} \sum_{b \neq a} \pi(b, a)"
        r"\quad \text{(entering flow)}"
    )

    st.markdown("**Step 5 — Net flow**")
    st.latex(r"\Phi(a) = \Phi^{+}(a) - \Phi^{-}(a)")
    st.markdown(
        "Alternatives are ranked in descending order of $\\Phi(a)$. "
        "A higher net flow means the alternative is more preferred overall."
    )

with st.expander("References"):
    st.markdown(
        "Brans, J.P.; Vincke, Ph. (1985). "
        '"A preference ranking organisation method". '
        "_Management Science_. "
        "**31** (6): 647-656. "
        "[doi](https://en.wikipedia.org/wiki/Digital_object_identifier):"
        "[10.1287/mnsc.31.6.647]"
        "(https://doi.org/10.1287%2Fmnsc.31.6.647)."
    )

st.divider()

_EXAMPLE_OPTIONS = ["Laptop A", "Laptop B", "Laptop C"]

col_load, col_clear, _ = st.columns([3, 3, 6], gap="small")

with col_load:
    if st.button("Load example", width="stretch"):
        for key in ("promethee_options", "promethee_criteria", "promethee_prefs"):
            st.session_state.pop(key, None)
        st.session_state["promethee_example"] = True
        st.rerun()

with col_clear:
    if st.button("Clear data", width="stretch"):
        for key in (
            "promethee_options",
            "promethee_criteria",
            "promethee_prefs",
            "promethee_example",
        ):
            st.session_state.pop(key, None)
        st.rerun()

_use_example = st.session_state.get("promethee_example", False)

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
    key="promethee_options",
)

st.header("Step 2: Criteria and Scores")

options_list = edited_options["Option"].tolist()

if _use_example and options_list == _EXAMPLE_OPTIONS:
    criteria_scores = pd.DataFrame(
        {
            "Criterion": ["Price ($)", "Performance", "Battery (hrs)"],
            "Weight": [0.4, 0.35, 0.25],
            "Is Negative": [True, False, False],
            "Laptop A": [999.0, 85.0, 8.0],
            "Laptop B": [1299.0, 95.0, 6.0],
            "Laptop C": [799.0, 70.0, 10.0],
        }
    )
else:
    criteria_scores = pd.DataFrame(
        columns=[
            "Criterion",
            "Weight",
            "Is Negative",
            *options_list,
        ]
    )
criteria_scores["Criterion"] = criteria_scores["Criterion"].astype(str)
criteria_scores["Weight"] = criteria_scores["Weight"].astype(float)
criteria_scores["Is Negative"] = criteria_scores["Is Negative"].astype(bool)

st.caption(
    "Add criteria, assign weights, and provide "
    "scores for each option. Check **Is Negative** "
    "for cost-type criteria "
    "(lower is better, e.g. price, risk)."
)

edited_criteria_scores = st.data_editor(
    criteria_scores,
    num_rows="dynamic",
    width="stretch",
    key="promethee_criteria",
)

st.header("Step 3: Preference Function Parameters")
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

criteria_list_for_prefs = edited_criteria_scores["Criterion"].dropna().tolist()
criteria_list_for_prefs = [c for c in criteria_list_for_prefs if c != ""]

if _use_example and criteria_list_for_prefs:
    pref_data = pd.DataFrame(
        {
            "Criterion": criteria_list_for_prefs,
            "Preference Function": ["usual"] * len(criteria_list_for_prefs),
            "q (indifference)": [0.0] * len(criteria_list_for_prefs),
            "p (preference)": [0.0] * len(criteria_list_for_prefs),
        }
    )
elif criteria_list_for_prefs:
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
    key="promethee_prefs",
)

st.divider()

st.header("Step 4: Results")

if st.button("Calculate options preference", type="primary"):
    if edited_options.empty or edited_options["Option"].isna().all():
        st.error("Please add at least one option.")
    elif edited_criteria_scores.empty:
        st.error("Please add at least one criterion with scores.")
    else:
        data = edited_criteria_scores.melt(
            id_vars=["Criterion", "Weight", "Is Negative"],
            var_name="Option",
            value_name="Score",
        )
        if data["Weight"].isna().any() or data["Score"].isna().any():
            st.error("Please fill out all Weights and Scores before calculating.")
        elif (data["Criterion"].isna() | (data["Criterion"] == "")).any():
            st.error("Please provide a name for each criterion.")
        else:
            data["Score"] = data["Score"].apply(lambda x: Decimal(str(x)))
            data["Weight"] = data["Weight"].apply(lambda x: Decimal(str(x)))
            data["Is Negative"] = (
                data["Is Negative"].fillna(False).infer_objects(copy=False)
            )

            pref_funcs = None
            if not edited_prefs.empty:
                has_linear = (edited_prefs["Preference Function"] == "linear").any()
                if has_linear:
                    pref_funcs = pd.DataFrame(
                        {
                            "Criterion": edited_prefs["Criterion"],
                            "PreferenceFunction": edited_prefs["Preference Function"],
                            "IndifferenceThreshold": edited_prefs[
                                "q (indifference)"
                            ].apply(lambda x: Decimal(str(x))),
                            "PreferenceThreshold": edited_prefs["p (preference)"].apply(
                                lambda x: Decimal(str(x))
                            ),
                        }
                    )

            deviations = calculate_deviations(data)
            preferences = calculate_preference_degrees(deviations, pref_funcs)
            aggregated = calculate_aggregated_preference_index(preferences)
            flows = calculate_flows(aggregated)

            result = calculate_promethee_ranking(flows)
            result = result.sort_values("Rank").reset_index(drop=True)

            st.success(
                f"Analysis complete — **{result.iloc[0]['Option']}** ranks first.",
                icon="🏆",
            )
            st.dataframe(result, hide_index=True, width="stretch")

            # Flow bar chart
            flow_data = flows.copy()
            flow_data["LeavingFlow"] = flow_data["LeavingFlow"].apply(float)
            flow_data["EnteringFlow"] = flow_data["EnteringFlow"].apply(
                lambda x: -float(x)
            )
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
                title="PROMETHEE II Flows",
                barmode="relative",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cad3f5",
                yaxis_title="Flow Value",
                margin={"t": 60, "b": 30, "l": 60, "r": 60},
            )
            st.plotly_chart(fig_bar, width="stretch")

            # Radar chart
            radar_data = data[["Option", "Criterion", "Score"]].copy()
            radar_data["Score"] = radar_data["Score"].apply(float)
            criteria_list = radar_data["Criterion"].unique().tolist()

            fig = go.Figure()
            for option in result["Option"]:
                option_data = radar_data[radar_data["Option"] == option]
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
