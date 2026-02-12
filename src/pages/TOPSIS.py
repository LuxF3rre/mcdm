from decimal import Decimal

import pandas as pd
import streamlit as st

from mcdm.topsis import calculate_topsis

st.set_page_config(page_title="TOPSIS", page_icon="🎯", layout="wide")

st.title("🎯 Multi-Criteria Decision Making with TOPSIS")

st.markdown(
    "**TOPSIS**, or the Technique for Order of Preference by Similarity to Ideal Solution, "
    "is a multi-criteria decision analysis method. This method is used to determine the best solution "
    "from a set of alternatives, based on multiple criteria or attributes. "
    "The basic idea behind TOPSIS is to identify solutions that are closest to the ideal solution "
    "and furthest from the anti-ideal or negative-ideal solution."
)

with st.expander("References"):
    st.markdown(
        'Hwang, C.L.; Lai, Y.J.; Liu, T.Y. (1993). "A new approach for multiple objective decision making". '
        "_Computers and Operational Research_. **20** (8): 889-899. [doi](https://en.wikipedia.org/wiki/Digital_object_identifier):"
        "[10.1016/0305-0548(93)90109-v](https://doi.org/10.1016%2F0305-0548%2893%2990109-v)."
    )

st.divider()

st.header("Step 1: Define Options")
st.caption("Add the alternatives you want to compare. Click the **+** button to add rows.")
options = pd.DataFrame(columns=["Option"])

edited_options = st.data_editor(options, num_rows="dynamic", use_container_width=True)

st.header("Step 2: Criteria and Scores")

options_list = edited_options["Option"].tolist()

criteria_scores = pd.DataFrame(columns=["Criterion", "Weight", "Is Negative", *options_list])
criteria_scores["Criterion"] = criteria_scores["Criterion"].astype(str)
criteria_scores["Weight"] = criteria_scores["Weight"].astype(float)
criteria_scores["Is Negative"] = criteria_scores["Is Negative"].astype(bool)

st.caption(
    "Add criteria, assign weights, and provide scores for each option. "
    "Check **Is Negative** for cost-type criteria (lower is better, e.g. price, risk)."
)

edited_criteria_scores = st.data_editor(criteria_scores, num_rows="dynamic", use_container_width=True)

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
        if data_for_topsis["Weight"].isna().any() or data_for_topsis["Score"].isna().any():
            st.error("Please fill out all Weights and Scores before calculating.")
        elif (data_for_topsis["Criterion"].isna() | (data_for_topsis["Criterion"] == "")).any():
            st.error("Please provide a name for each criterion.")
        else:
            data_for_topsis["Score"] = data_for_topsis["Score"].apply(lambda x: Decimal(str(x)))  # type: ignore
            data_for_topsis["Weight"] = data_for_topsis["Weight"].apply(lambda x: Decimal(str(x)))  # type: ignore
            data_for_topsis["Is Negative"] = data_for_topsis["Is Negative"].fillna(False)

            topsis = calculate_topsis(data_for_topsis)
            topsis = topsis.sort_values("Rank").reset_index(drop=True)

            st.success(f"Analysis complete — **{topsis.iloc[0]['Option']}** ranks first.", icon="🏆")
            st.dataframe(topsis, hide_index=True, use_container_width=True)

st.divider()

st.markdown("Made with ❤️ by Maurycy Blaszczak ([maurycyblaszczak.com](https://maurycyblaszczak.com/))")
