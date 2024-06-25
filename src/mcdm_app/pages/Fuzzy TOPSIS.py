from decimal import Decimal

import pandas as pd
import streamlit as st

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.fuzzy_topsis import calculate_fuzzy_topsis

st.set_page_config(page_title="Fuzzy TOPSIS", page_icon="🧶")

st.title("🧶Multi-Criteria Decision Making with Fuzzy TOPSIS")

st.markdown(
    "**Fuzzy TOPSIS** (Technique for Order of Preference by Similarity to Ideal Solution) is an extension of "
    "the traditional TOPSIS method, incorporating fuzzy logic to handle uncertainty and imprecision in the "
    "decision-making process. This approach is particularly useful in situations where decision criteria "
    "are not clearly defined or are subject to human judgment and perception, which is often the case in "
    "complex decision-making scenarios."
)

st.write("For more information see:")

st.markdown(
    'El Alaoui, M. (2021). "Fuzzy TOPSIS: Logic, Approaches, and Case Studies". '
    "_New York: CRC Press_. [doi](https://en.wikipedia.org/wiki/Digital_object_identifier):"
    "[10.1201/9781003168416](https://doi.org/10.1201%2F9781003168416). ISBN 978-0-367-76748-8. S2CID 233525185."
)

st.header("Fuzzy Numbers")

st.markdown(
    "**Triangular Fuzzy Numbers** (TFNs) are a fundamental concept in fuzzy logic and fuzzy mathematics, "
    "used to represent uncertain or imprecise data. They are particularly useful in scenarios where precise "
    "quantification is difficult, such as subjective assessments or estimations."
)

st.markdown(
    "Triangular Fuzzy Number consists of three variables *a*, *b*, *c*.\n"
    "\n"
    "- *a*: The lower limit (or the leftmost point of the triangle), "
    "representing the minimum value that the fuzzy number can take.\n"
    "- *b*: The peak of the triangle, indicating the most probable or most "
    "representative value of the fuzzy number.\n"
    "- *c*: The upper limit (or the rightmost point of the triangle), "
    "representing the maximum value that the fuzzy number can take.\n"
)

st.header("Options")
options = pd.DataFrame(columns=["Option"])
st.write("Add options in the table below.")

edited_options = st.data_editor(options, num_rows="dynamic")

st.header("Criteria")
criteria = pd.DataFrame(columns=["Criterion", "Is Negative"])
criteria["Is Negative"] = criteria["Is Negative"].astype(bool)
st.write("Add criteria in the table below.")

edited_criteria = st.data_editor(criteria, num_rows="dynamic")

st.header("Number of Decision Makers")
st.write("Set number of decision makers.")

number_of_decision_makers = st.slider("Pick a number", 1, 5)

st.header("Scores and Weights")
st.write("Add scores to options and weights per decision maker.")

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
for decision_maker_number in range(number_of_decision_makers):
    st.markdown(f"### Decision maker no. {decision_maker_number + 1}")
    st.markdown("#### Weights")

    weights_dict[decision_maker_number] = st.data_editor(weights, key=f"Weight{decision_maker_number}", hide_index=True)

    st.markdown("#### Scores")

    scores_dict[decision_maker_number] = st.data_editor(scores, key=f"Score{decision_maker_number}", hide_index=True)

st.header("Options Preference")

if st.button("Calculate options preference"):
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
    st.dataframe(fuzzy_topsis, hide_index=True)

st.markdown("Made with ❤️ by Maurycy Blaszczak ([maurycyblaszczak.com](https://maurycyblaszczak.com/))")
