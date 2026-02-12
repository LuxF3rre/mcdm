import streamlit as st

st.set_page_config(page_title="Multi-Criteria Decision Making", page_icon="🏠", layout="centered")

st.title("🏠 Multi-Criteria Decision Making")

st.markdown(
    "In today's complex world, inundated with countless choices, making informed decisions is more critical than ever. "
    "This project introduces a multi-criteria decision analysis tool powered by Python and Streamlit, "
    "harnessing the potential of the TOPSIS method."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 TOPSIS")
    st.markdown(
        "The classic **Technique for Order of Preference by Similarity to Ideal Solution**. "
        "Best for decisions with clearly quantifiable criteria and precise data."
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
        "An extension of TOPSIS using **fuzzy logic** to handle uncertainty and imprecision. "
        "Best for subjective assessments or group decisions."
    )
    st.markdown(
        "**Use when you have:**\n"
        "- Uncertain or imprecise data\n"
        "- Multiple decision makers\n"
        "- Subjective criteria"
    )

st.divider()

st.info("Select an algorithm from the **sidebar** to get started.")

st.markdown("Made with ❤️ by Maurycy Blaszczak ([maurycyblaszczak.com](https://maurycyblaszczak.com/))")
