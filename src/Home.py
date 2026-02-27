import streamlit as st

st.set_page_config(
    page_title="Multi-Criteria Decision Making", page_icon="🏠", layout="centered"
)

st.title("🏠 Multi-Criteria Decision Making")

st.markdown(
    "We make decisions every day — some simple, some not. "
    "When multiple factors matter at once, it helps to have "
    "a structured way to think through your options. "
    "This tool offers multiple MCDM methods to help you do "
    "exactly that, right in your browser."
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🎯 TOPSIS")
    st.markdown(
        "The classic **Technique for Order of Preference "
        "by Similarity to Ideal Solution**. "
        "Ranks by closeness to the ideal best."
    )
    st.markdown(
        "**Use when you have:**\n"
        "- Precise numerical scores\n"
        "- A single decision maker\n"
        "- Well-defined criteria"
    )

with col2:
    st.subheader("🧶 Fuzzy TOPSIS")
    st.markdown(
        "An extension of TOPSIS using **fuzzy logic** "
        "to handle uncertainty and imprecision. "
        "Best for group decisions."
    )
    st.markdown(
        "**Use when you have:**\n"
        "- Uncertain or imprecise data\n"
        "- Multiple decision makers\n"
        "- Subjective criteria"
    )

with col3:
    st.subheader("📊 PROMETHEE")
    st.markdown(
        "**Preference Ranking Organization Method** — "
        "compares options pairwise with customizable "
        "preference functions."
    )
    st.markdown(
        "**Use when you have:**\n"
        "- Precise numerical scores\n"
        "- A single decision maker\n"
        "- Preference thresholds"
    )

col4, col5, col6 = st.columns(3)

with col4:
    st.subheader("🧵 Fuzzy PROMETHEE")
    st.markdown(
        "Combines PROMETHEE pairwise logic with "
        "**Triangular Fuzzy Numbers** for uncertain "
        "or multi-expert evaluations."
    )
    st.markdown(
        "**Use when you have:**\n"
        "- Uncertain or imprecise data\n"
        "- Multiple decision makers\n"
        "- Preference thresholds"
    )

with col5:
    st.subheader("⚖️ AHP")
    st.markdown(
        "The **Analytic Hierarchy Process** derives "
        "weights from pairwise comparisons on Saaty's "
        "1-9 scale with consistency check."
    )
    st.markdown(
        "**Use when you have:**\n"
        "- Criteria hard to weight directly\n"
        "- A single decision maker\n"
        "- Need for consistency validation"
    )

with col6:
    st.subheader("🪢 Fuzzy AHP")
    st.markdown(
        "Extends AHP with **Triangular Fuzzy Numbers** "
        "for pairwise comparisons, using Buckley's "
        "geometric mean method."
    )
    st.markdown(
        "**Use when you have:**\n"
        "- Vague pairwise judgments\n"
        "- Multiple decision makers\n"
        "- Need for consistency validation"
    )

st.divider()

st.info("Select an algorithm from the **sidebar** to get started.")

st.markdown(
    "<div style='text-align: center'>Made with ❤ by Maurycy Blaszczak"
    " (<a href='https://maurycyblaszczak.com/'>maurycyblaszczak.com</a>)</div>",
    unsafe_allow_html=True,
)
