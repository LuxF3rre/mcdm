from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from mcdm.topsis import calculate_normalized_weighted_scores, calculate_topsis

st.set_page_config(page_title="TOPSIS", page_icon="🎯", layout="wide")

st.title("🎯 Multi-Criteria Decision Making with TOPSIS")

st.markdown(
    "**TOPSIS** ranks your options by measuring how close "
    "each one is to the best possible outcome and how far "
    "it is from the worst. Give it your scores and weights "
    "— it does the math."
)

with st.expander("References"):
    st.markdown(
        "Hwang, C.L.; Lai, Y.J.; Liu, T.Y. (1993). "
        '"A new approach for multiple objective '
        'decision making". '
        "_Computers and Operational Research_. "
        "**20** (8): 889-899. "
        "[doi](https://en.wikipedia.org/wiki/"
        "Digital_object_identifier):"
        "[10.1016/0305-0548(93)90109-v]"
        "(https://doi.org/10.1016%2F0305-0548"
        "%2893%2990109-v)."
    )

st.divider()

_EXAMPLE_OPTIONS = ["Laptop A", "Laptop B", "Laptop C"]

col_load, col_clear, _ = st.columns([3, 3, 6], gap="small")

with col_load:
    if st.button("Load example", width="stretch"):
        for key in ("topsis_options", "topsis_criteria"):
            st.session_state.pop(key, None)
        st.session_state["topsis_example"] = True
        st.rerun()

with col_clear:
    if st.button("Clear data", width="stretch"):
        for key in ("topsis_options", "topsis_criteria", "topsis_example"):
            st.session_state.pop(key, None)
        st.rerun()

_use_example = st.session_state.get("topsis_example", False)

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
    key="topsis_options",
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
    key="topsis_criteria",
)

st.divider()

st.header("Step 3: Results")

if st.button("Calculate options preference", type="primary"):
    if edited_options.empty or edited_options["Option"].isna().all():
        st.error("Please add at least one option.")
    elif edited_criteria_scores.empty:
        st.error("Please add at least one criterion with scores.")
    else:
        data_for_topsis = edited_criteria_scores.melt(
            id_vars=["Criterion", "Weight", "Is Negative"],
            var_name="Option",
            value_name="Score",
        )
        if (
            data_for_topsis["Weight"].isna().any()
            or data_for_topsis["Score"].isna().any()
        ):
            st.error("Please fill out all Weights and Scores before calculating.")
        elif (
            data_for_topsis["Criterion"].isna() | (data_for_topsis["Criterion"] == "")
        ).any():
            st.error("Please provide a name for each criterion.")
        else:
            data_for_topsis["Score"] = data_for_topsis["Score"].apply(
                lambda x: Decimal(str(x))
            )
            data_for_topsis["Weight"] = data_for_topsis["Weight"].apply(
                lambda x: Decimal(str(x))
            )
            data_for_topsis["Is Negative"] = (
                data_for_topsis["Is Negative"].fillna(False).infer_objects(copy=False)
            )

            normalized_weighted = calculate_normalized_weighted_scores(
                data_for_topsis.copy()
            )

            topsis = calculate_topsis(data_for_topsis)
            topsis = topsis.sort_values("Rank").reset_index(drop=True)

            st.success(
                f"Analysis complete — **{topsis.iloc[0]['Option']}** ranks first.",
                icon="🏆",
            )
            st.dataframe(topsis, hide_index=True, width="stretch")

            radar_data = normalized_weighted[
                ["Option", "Criterion", "NormalizedWeightedScore"]
            ].copy()
            radar_data["NormalizedWeightedScore"] = radar_data[
                "NormalizedWeightedScore"
            ].apply(float)

            criteria_list = radar_data["Criterion"].unique().tolist()

            fig = go.Figure()
            for option in topsis["Option"]:
                option_data = radar_data[radar_data["Option"] == option]
                values = [
                    option_data[option_data["Criterion"] == c][
                        "NormalizedWeightedScore"
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
    "Made with ❤️ by Maurycy Blaszczak ([maurycyblaszczak.com](https://maurycyblaszczak.com/))"
)
