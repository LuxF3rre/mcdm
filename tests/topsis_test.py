from decimal import Decimal

import pandas as pd

from mcdm.topsis import calculate_topsis

data_topsis_in = {
    "Criterion": [
        "C1",
        "C2",
        "C3",
        "C4",
        "C1",
        "C2",
        "C3",
        "C4",
        "C1",
        "C2",
        "C3",
        "C4",
        "C1",
        "C2",
        "C3",
        "C4",
        "C1",
        "C2",
        "C3",
        "C4",
    ],
    "Weight": [
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
        0.25,
    ],
    "Is Negative": [
        True,
        False,
        False,
        False,
        True,
        False,
        False,
        False,
        True,
        False,
        False,
        False,
        True,
        False,
        False,
        False,
        True,
        False,
        False,
        False,
    ],
    "Option": [
        "O1",
        "O1",
        "O1",
        "O1",
        "O2",
        "O2",
        "O2",
        "O2",
        "O3",
        "O3",
        "O3",
        "O3",
        "O4",
        "O4",
        "O4",
        "O4",
        "O5",
        "O5",
        "O5",
        "O5",
    ],
    "Score": [
        250.0,
        16.0,
        12.0,
        5.0,
        200.0,
        16.0,
        8.0,
        3.0,
        300.0,
        32.0,
        16.0,
        4.0,
        275.0,
        32.0,
        8.0,
        4.0,
        225.0,
        16.0,
        16.0,
        2.0,
    ],
}


data_topsis_out = {
    "Option": [
        "O1",
        "O2",
        "O3",
        "O4",
        "O5",
    ],
    "Performance Score": [
        "0.5342768571821002378794145649",
        "0.3083677687324685296169634011",
        "0.6916322312675314703830365993",
        "0.5347365844868379925786474865",
        "0.4010461215167861409302940826",
    ],
    "Rank": [
        3.0,
        5.0,
        1.0,
        2.0,
        4.0,
    ],
}

topsis_in = pd.DataFrame(data_topsis_in)
topsis_in["Score"] = topsis_in["Score"].apply(lambda x: Decimal(str(x)))  # type: ignore
topsis_in["Weight"] = topsis_in["Weight"].apply(lambda x: Decimal(str(x)))  # type: ignore

topsis_out = pd.DataFrame(data_topsis_out)
topsis_out["Performance Score"] = topsis_out["Performance Score"].apply(lambda x: Decimal(x))  # type: ignore


def test_calculate_topsis() -> None:
    assert calculate_topsis(topsis_in).equals(topsis_out)
