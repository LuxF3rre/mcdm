from decimal import Decimal

import pandas as pd
import streamlit as st

from fuzzy_numbers import TriangularFuzzyNumber
from mcdm.fuzzy_topsis import calculate_fuzzy_topsis

st.set_page_config(page_title="Fuzzy TOPSIS", page_icon="🧶", layout="wide")

st.title("🧶 Multi-Criteria Decision Making with Fuzzy TOPSIS")

st.markdown(
    "**Fuzzy TOPSIS** works like regular TOPSIS, but lets "
    "you use ranges instead of exact numbers. This is useful "
    "when scores are subjective or when several people are "
    "weighing in with different perspectives."
)

with st.expander("About Triangular Fuzzy Numbers"):
    st.markdown(
        'Instead of saying "this scores exactly 7", '
        "a **Triangular Fuzzy Number** lets you say "
        '"somewhere between 5 and 9, most likely 7". '
        "It captures the uncertainty in a simple way."
    )

    st.markdown(
        "A Triangular Fuzzy Number consists of three "
        "values **(Min, Likely, Max)** "
        "where Min ≤ Likely ≤ Max:\n"
        "\n"
        "- **Min** — the minimum possible value\n"
        "- **Likely** — the most probable value\n"
        "- **Max** — the maximum possible value\n"
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

col_load, col_clear, _ = st.columns([1, 1, 4])

with col_load:
    if st.button("Load example"):
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
    if st.button("Clear data"):
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
            decision_matrix["Is Negative"].fillna(False).infer_objects(copy=False)
        )

        fuzzy_topsis = calculate_fuzzy_topsis(decision_matrix)
        fuzzy_topsis = fuzzy_topsis.sort_values("Rank").reset_index(drop=True)

        st.success(
            f"Analysis complete — **{fuzzy_topsis.iloc[0]['Option']}** ranks first.",
            icon="🏆",
        )
        st.dataframe(fuzzy_topsis, hide_index=True, width="stretch")

st.divider()

st.markdown(
    "Made with ❤️ by Maurycy Blaszczak ([maurycyblaszczak.com](https://maurycyblaszczak.com/))"
)
