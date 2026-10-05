"""
Why: STEP1でデータの意味と構造を確認する。
What: CSV読込、info相当、describe、ユニーク値を返す。
Assumption / Dependencies: pandas, src.analysis.common。
I/O: なし → 概要テーブル類。
Caution: ここでは品質判断や前処理をしない。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
- 2026-10-05: 表示コードを画面の各出力テーブルと整合
"""

from __future__ import annotations

import pandas as pd

from src.analysis.common import load_raw

CODE_SAMPLE = '''import pandas as pd

from src.analysis.common import load_raw

df = load_raw("before")
shape = pd.DataFrame(
    {"metric": ["rows", "columns"], "value": [df.shape[0], df.shape[1]]}
)
dtypes = (
    df.dtypes.astype(str)
    .rename("dtype")
    .reset_index()
    .rename(columns={"index": "column"})
)
head = df.head(8)
describe = (
    df.describe(include="all")
    .T.reset_index()
    .rename(columns={"index": "column"})
)
unique_phase = pd.DataFrame({"flight_phase": sorted(df["flight_phase"].dropna().unique())})
unique_test = pd.DataFrame(
    {"test_id": sorted(df["test_id"].dropna().unique())}
)

for name, table in {
    "shape": shape,
    "dtypes": dtypes,
    "head": head,
    "describe": describe,
    "unique_phase": unique_phase,
    "unique_test": unique_test,
}.items():
    print(name)
    print(table)
'''


def execute_logic() -> dict[str, pd.DataFrame]:
    """データ構造の確認結果を返す。

    Returns:
        shape, dtypes, head, describe, unique を含む辞書。

    Raises:
        FileNotFoundError: CSVが無いとき。

    Side Effects:
        なし。

    Examples:
        >>> # execute_logic()["head"].shape[0] > 0
    """
    df = load_raw("before")
    dtypes = df.dtypes.astype(str).rename("dtype").reset_index().rename(columns={"index": "column"})
    unique_phase = pd.DataFrame({"flight_phase": sorted(df["flight_phase"].dropna().unique())})
    unique_test = pd.DataFrame({"test_id": sorted(df["test_id"].dropna().unique())})
    shape = pd.DataFrame({"metric": ["rows", "columns"], "value": [df.shape[0], df.shape[1]]})
    return {
        "shape": shape,
        "dtypes": dtypes,
        "head": df.head(8),
        "describe": df.describe(include="all").T.reset_index().rename(columns={"index": "column"}),
        "unique_phase": unique_phase,
        "unique_test": unique_test,
    }
