# Multi-Criteria Decision Making

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://luxf3rre-mcdm.streamlit.app/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/LuxF3rre/mcdm)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/badge/type%20checker-ty-blue.svg)](https://github.com/astral-sh/ty)
[![Build](https://github.com/LuxF3rre/mcdm/actions/workflows/test.yml/badge.svg)](https://github.com/LuxF3rre/mcdm/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/LuxF3rre/mcdm/graph/badge.svg?token=OuwuSu1lm4)](https://codecov.io/gh/LuxF3rre/mcdm)

## Overview

We make decisions every day — some simple, some not. When multiple factors matter at once, it helps to have a structured way to think through your options. This tool provides multiple MCDM methods to help you do exactly that, powered by Python and Streamlit.

**TOPSIS** (*Technique for Order of Preference by Similarity to Ideal Solution*) ranks your options by how close each one is to the best possible outcome and how far it is from the worst. You give it scores and weights — it does the math.

**Fuzzy TOPSIS** adds fuzzy logic on top, so you can work with ranges instead of exact numbers. This is handy when scores are subjective or when several people are weighing in with different perspectives.

**PROMETHEE II** (*Preference Ranking Organization METHod for Enrichment Evaluations*) compares every pair of alternatives on each criterion using preference functions, producing a complete ranking based on net preference flows.

**Fuzzy PROMETHEE** extends PROMETHEE with Triangular Fuzzy Numbers, handling uncertainty from multiple decision makers while preserving the pairwise comparison logic.

**AHP** (*Analytic Hierarchy Process*) derives criterion weights from pairwise comparisons using Saaty's 1-9 scale, with a built-in consistency check to ensure judgments are logically coherent.

**Fuzzy AHP** extends AHP with Triangular Fuzzy Numbers for pairwise comparisons (Buckley's method), allowing multiple decision makers to express uncertainty in their judgments.

## Features

- [x] Built with **🐍Python**.
- [x] Web interface powered by **Streamlit**.
- [x] Implements **TOPSIS** and **Fuzzy TOPSIS** methods.
- [x] Implements **PROMETHEE II** and **Fuzzy PROMETHEE** methods.
- [x] Implements **AHP** and **Fuzzy AHP** (Buckley's method).

## Installation & Usage

### 1. Install uv

Follow the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) or use the one-liner:

```console
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and set up

```console
git clone https://github.com/LuxF3rre/mcdm
cd mcdm
uv sync
```

### 3. Run the app

```console
uv run streamlit run ./src/Home.py
```

Open <http://localhost:8501/> in your browser and you're good to go.

## References

### TOPSIS

- Hwang, C.L.; Lai, Y.J.; Liu, T.Y. (1993). "A new approach for multiple objective decision making". *Computers and Operational Research*. **20** (8): 889-899. [doi](https://en.wikipedia.org/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/0305-0548(93)90109-v](https://doi.org/10.1016%2F0305-0548%2893%2990109-v)
- El Alaoui, M. (2021). "Fuzzy TOPSIS: Logic, Approaches, and Case Studies". *New York: CRC Press*. [doi](https://en.wikipedia.org/wiki/Digital_object_identifier):[10.1201/9781003168416](https://doi.org/10.1201%2F9781003168416). ISBN 978-0-367-76748-8. S2CID 233525185.

### PROMETHEE

- Brans, J.P.; Vincke, Ph. (1985). "A preference ranking organisation method". *Management Science*. **31** (6): 647-656. [doi](https://en.wikipedia.org/wiki/Digital_object_identifier):[10.1287/mnsc.31.6.647](https://doi.org/10.1287%2Fmnsc.31.6.647)
- Goumas, M.; Lygerou, V. (2000). "An extension of the PROMETHEE method for decision making in fuzzy environment". *European Journal of Operational Research*. **123** (3): 606-613. [doi](https://en.wikipedia.org/wiki/Digital_object_identifier):[10.1016/S0377-2217(99)00093-4](https://doi.org/10.1016%2FS0377-2217%2899%2900093-4)

### AHP

- Saaty, T.L. (1980). "The Analytic Hierarchy Process". *New York: McGraw-Hill*. ISBN 978-0-07-054371-3.
- Saaty, T.L. (1987). "The analytic hierarchy process — what it is and how it is used". *Mathematical Modelling*. **9** (3-5): 161-176. [doi](https://en.wikipedia.org/wiki/Digital_object_identifier):[10.1016/0270-0255(87)90473-8](https://doi.org/10.1016%2F0270-0255%2887%2990473-8)
- Buckley, J.J. (1985). "Fuzzy hierarchical analysis". *Fuzzy Sets and Systems*. **17** (3): 233-247. [doi](https://en.wikipedia.org/wiki/Digital_object_identifier):[10.1016/0165-0114(85)90090-9](https://doi.org/10.1016%2F0165-0114%2885%2990090-9)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License
