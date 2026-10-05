"""
Why: STEP2で分析前にデータ品質を確認する習慣を付ける。
What: 欠損・重複・範囲・欠損率を集計する。
Assumption / Dependencies: pandas, src.analysis.common。
I/O: なし → 品質テーブル。
Caution: ここでは値を直さない。発見のみ。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
- 2026-10-05: 表示コードを欠損・重複・範囲テーブルと整合
"""

from __future__ import annotations

import pandas as pd

from src.analysis.common import load_raw

CODE_SAMPLE = '''import pandas as pd

from src.analysis.common import load_raw

df = load_raw("before")
missing = (
    pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": df.isna().sum().to_numpy(),
            "missing_rate": df.isna().mean().to_numpy(),
        }
    )
    .sort_values("missing_count", ascending=False)
    .reset_index(drop=True)
)
duplicated = pd.DataFrame(
    {
        "metric": ["rows", "duplicated_rows", "duplicate_rate"],
        "value": [len(df), int(df.duplicated().sum()), float(df.duplicated().mean())],
    }
)
ranges = (
    df.select_dtypes(include="number")
    .agg(["min", "max", "mean"])
    .T.reset_index()
    .rename(columns={"index": "column"})
)

for name, table in {
    "missing": missing,
    "duplicated": duplicated,
    "ranges": ranges,
}.items():
    print(name)
    print(table)
'''


def execute_logic() -> dict[str, pd.DataFrame]:
    """品質確認の集計を返す。

    Returns:
        欠損・重複・範囲のテーブル。

    Raises:
        FileNotFoundError: CSVが無いとき。

    Side Effects:
        なし。

    Examples:
        >>> # "missing" in execute_logic()
    """
    df = load_raw("before")
    missing = (
        pd.DataFrame(
            {
                "column": df.columns,
                "missing_count": df.isna().sum().to_numpy(),
                "missing_rate": df.isna().mean().to_numpy(),
            }
        )
        .sort_values("missing_count", ascending=False)
        .reset_index(drop=True)
    )
    duplicated = pd.DataFrame(
        {
            "metric": ["rows", "duplicated_rows", "duplicate_rate"],
            "value": [
                len(df),
                int(df.duplicated().sum()),
                float(df.duplicated().mean()),
            ],
        }
    )
    numeric = df.select_dtypes(include="number")
    ranges = numeric.agg(["min", "max", "mean"]).T.reset_index().rename(columns={"index": "column"})
    return {"missing": missing, "duplicated": duplicated, "ranges": ranges}
