from decimal import Decimal

import pandas as pd
import streamlit as st

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.fuzzy_topsis import calculate_fuzzy_topsis

st.set_page_config(page_title="Fuzzy TOPSIS", page_icon="🧶", layout="wide")

st.title("🧶 Multi-Criteria Decision Making with Fuzzy TOPSIS")

st.markdown(
    "**Fuzzy TOPSIS** (Technique for Order of Preference by Similarity to Ideal Solution) is an extension of "
    "the traditional TOPSIS method, incorporating fuzzy logic to handle uncertainty and imprecision in the "
    "decision-making process. This approach is particularly useful in situations where decision criteria "
    "are not clearly defined or are subject to human judgment and perception, which is often the case in "
    "complex decision-making scenarios."
)

with st.expander("About Triangular Fuzzy Numbers"):
    st.markdown(
        "**Triangular Fuzzy Numbers** (TFNs) are a fundamental concept in fuzzy logic and fuzzy mathematics, "
        "used to represent uncertain or imprecise data. They are particularly useful in scenarios where precise "
        "quantification is difficult, such as subjective assessments or estimations."
    )

    st.markdown(
        "A Triangular Fuzzy Number consists of three values **(a, b, c)** where a ≤ b ≤ c:\n"
        "\n"
        "- **a** — Lower bound: the minimum possible value\n"
        "- **b** — Peak: the most probable / representative value\n"
        "- **c** — Upper bound: the maximum possible value\n"
    )

with st.expander("References"):
    st.markdown(
        'El Alaoui, M. (2021). "Fuzzy TOPSIS: Logic, Approaches, and Case Studies". '
        "_New York: CRC Press_. [doi](https://en.wikipedia.org/wiki/Digital_object_identifier):"
        "[10.1201/9781003168416](https://doi.org/10.1201%2F9781003168416). ISBN 978-0-367-76748-8. S2CID 233525185."
    )

st.divider()

st.header("Step 1: Define Options")
st.caption("Add the alternatives you want to compare. Click the **+** button to add rows.")
options = pd.DataFrame(columns=["Option"])

edited_options = st.data_editor(options, num_rows="dynamic", use_container_width=True)

st.header("Step 2: Define Criteria")
st.caption(
    "Add the criteria for evaluation. "
    "Check **Is Negative** for cost-type criteria (lower is better, e.g. price, risk)."
)
criteria = pd.DataFrame(columns=["Criterion", "Is Negative"])
criteria["Is Negative"] = criteria["Is Negative"].astype(bool)

edited_criteria = st.data_editor(criteria, num_rows="dynamic", use_container_width=True)

st.header("Step 3: Number of Decision Makers")
st.caption("Select how many decision makers will provide independent assessments.")

number_of_decision_makers = st.slider("Number of decision makers", 1, 5)

st.header("Step 4: Scores and Weights")
st.caption(
    "For each decision maker, enter **weights** (importance of each criterion) "
    "and **scores** (rating of each option per criterion) as Triangular Fuzzy Numbers (a, b, c)."
)

weights = edited_criteria.drop(columns="Is Negative")
weights["a"] = None
weights["b"] = None
weights["c"] = None

scores = edited_options.merge(edited_criteria, how="cross").drop(columns="Is Negative")
scores["a"] = None
scores["b"] = None
scores["c"] = None

for column in ["a", "b", "c"]:
    weights[column] = weights[column].astype(float)
    scores[column] = scores[column].astype(float)

weights_dict = {}
scores_dict = {}

dm_tabs = st.tabs([f"Decision Maker {i + 1}" for i in range(number_of_decision_makers)])

for decision_maker_number in range(number_of_decision_makers):
    with dm_tabs[decision_maker_number]:
        st.subheader("Weights")
        st.caption("How important is each criterion? Enter as (a, b, c).")

        weights_dict[decision_maker_number] = st.data_editor(
            weights, key=f"Weight{decision_maker_number}", hide_index=True, use_container_width=True
        )

        st.subheader("Scores")
        st.caption("How does each option perform on each criterion? Enter as (a, b, c).")

        scores_dict[decision_maker_number] = st.data_editor(
            scores, key=f"Score{decision_maker_number}", hide_index=True, use_container_width=True
        )

st.divider()

st.header("Step 5: Results")

if st.button("Calculate options preference", type="primary"):
    if edited_options.empty or edited_options["Option"].isna().all():
        st.error("Please add at least one option.")
    elif edited_criteria.empty or edited_criteria["Criterion"].isna().all():
        st.error("Please add at least one criterion.")
    else:
        decision_matrix = pd.DataFrame(columns=["Option", "Criterion", "Weight", "Score"])
        for decision_maker_number in range(number_of_decision_makers):
            scores_dict[decision_maker_number]["a"] = scores_dict[decision_maker_number]["a"].apply(
                lambda x: Decimal(str(x))  # type: ignore
            )
            scores_dict[decision_maker_number]["b"] = scores_dict[decision_maker_number]["b"].apply(
                lambda x: Decimal(str(x))  # type: ignore
            )
            scores_dict[decision_maker_number]["c"] = scores_dict[decision_maker_number]["c"].apply(
                lambda x: Decimal(str(x))  # type: ignore
            )

            scores_dict[decision_maker_number]["Score"] = scores_dict[decision_maker_number].apply(
                lambda row: TriangularFuzzyNumber(
                    row["a"],
                    row["b"],
                    row["c"],
                ),
                axis=1,
            )
            scores_dict[decision_maker_number] = scores_dict[decision_maker_number].drop(columns=["a", "b", "c"])

            weights_dict[decision_maker_number]["a"] = weights_dict[decision_maker_number]["a"].apply(
                lambda x: Decimal(str(x))  # type: ignore
            )
            weights_dict[decision_maker_number]["b"] = weights_dict[decision_maker_number]["b"].apply(
                lambda x: Decimal(str(x))  # type: ignore
            )
            weights_dict[decision_maker_number]["c"] = weights_dict[decision_maker_number]["c"].apply(
                lambda x: Decimal(str(x))  # type: ignore
            )

            weights_dict[decision_maker_number]["Weight"] = weights_dict[decision_maker_number].apply(
                lambda row: TriangularFuzzyNumber(
                    row["a"],
                    row["b"],
                    row["c"],
                ),
                axis=1,
            )

            weights_dict[decision_maker_number] = weights_dict[decision_maker_number].drop(columns=["a", "b", "c"])

            merged = (
                scores_dict[decision_maker_number]
                .merge(weights_dict[decision_maker_number], on="Criterion", how="left")
                .merge(edited_criteria, on="Criterion", how="left")
            )

            decision_matrix = pd.concat([decision_matrix, merged])

        decision_matrix["Is Negative"] = decision_matrix["Is Negative"].fillna(False)

        fuzzy_topsis = calculate_fuzzy_topsis(decision_matrix)
        fuzzy_topsis = fuzzy_topsis.sort_values("Rank").reset_index(drop=True)

        st.success(f"Analysis complete — **{fuzzy_topsis.iloc[0]['Option']}** ranks first.", icon="🏆")
        st.dataframe(fuzzy_topsis, hide_index=True, use_container_width=True)

st.divider()

st.markdown("Made with ❤️ by Maurycy Blaszczak ([maurycyblaszczak.com](https://maurycyblaszczak.com/))")
