# Multi-Criteria Decision Making

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://luxf3rre-mcdm.streamlit.app/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/LuxF3rre/mcdm)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/badge/type%20checker-ty-blue.svg)](https://github.com/astral-sh/ty)
[![Build](https://github.com/LuxF3rre/mcdm/actions/workflows/test.yml/badge.svg)](https://github.com/LuxF3rre/mcdm/actions/workflows/python-app.yml)
[![codecov](https://codecov.io/gh/LuxF3rre/mcdm/branch/main/graph/badge.svg)](https://codecov.io/gh/LuxF3rre/repo-mcdm)

## Overview

We make decisions every day — some simple, some not. When multiple factors matter at once, it helps to have a structured way to think through your options. This tool uses the TOPSIS method to help you do exactly that, powered by Python and Streamlit.

**TOPSIS** (*Technique for Order of Preference by Similarity to Ideal Solution*) ranks your options by how close each one is to the best possible outcome and how far it is from the worst. You give it scores and weights — it does the math.

**Fuzzy TOPSIS** adds fuzzy logic on top, so you can work with ranges instead of exact numbers. This is handy when scores are subjective or when several people are weighing in with different perspectives.

## Features

- [x] Built with **🐍Python**.
- [x] Web interface powered by **Streamlit**.
- [x] Implements the **TOPSIS** and **fuzzy TOPSIS** methods for decision making.

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

Open http://localhost:8501/ in your browser and you're good to go.

## References

For a deeper dive into the methodology and applications of TOPSIS:

- Hwang, C.L.; Lai, Y.J.; Liu, T.Y. (1993). "A new approach for multiple objective decision making". _Computers and Operational Research_. **20** (8): 889-899. [doi](https://en.wikipedia.org/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/0305-0548(93)90109-v](https://doi.org/10.1016%2F0305-0548%2893%2990109-v)
- El Alaoui, M. (2021). "Fuzzy TOPSIS: Logic, Approaches, and Case Studies". _New York: CRC Press_. [doi](https://en.wikipedia.org/wiki/Digital_object_identifier):[10.1201/9781003168416](https://doi.org/10.1201%2F9781003168416). ISBN 978-0-367-76748-8. S2CID 233525185.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License
