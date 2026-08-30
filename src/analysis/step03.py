"""
Why: STEP3で分析できる形へ整える。
What: 重複削除、timestamp変換、負の速度の欠損化、groupby例を示す。
Assumption / Dependencies: pandas, src.analysis.common。
I/O: なし → 処理前後の件数と比較表。
Caution: 欠損の埋め方は一つではない。ここでは学習用の一例。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
"""

from __future__ import annotations

import pandas as pd

from src.analysis.common import load_raw, prepare_for_analysis

CODE_SAMPLE = '''import pandas as pd

df = pd.read_csv("data/flight_tests_before.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.drop_duplicates()
df.loc[df["speed_kmh"] < 0, "speed_kmh"] = pd.NA
phase_mean = df.groupby("flight_phase")["motor_3_temp_c"].mean()
print(df.shape)
print(phase_mean)
'''


def execute_logic() -> dict[str, pd.DataFrame]:
    """前処理の前後比較を返す。

    Returns:
        件数比較とフェーズ別平均。

    Raises:
        FileNotFoundError: CSVが無いとき。

    Side Effects:
        なし。

    Examples:
        >>> # execute_logic()["counts"]
    """
    raw = load_raw("before")
    clean = prepare_for_analysis(raw)
    counts = pd.DataFrame(
        {
            "state": ["raw", "prepared"],
            "rows": [len(raw), len(clean)],
            "missing_cells": [int(raw.isna().sum().sum()), int(clean.isna().sum().sum())],
            "duplicated_rows": [int(raw.duplicated().sum()), int(clean.duplicated().sum())],
        }
    )
    phase_mean = (
        clean.groupby("flight_phase", as_index=False)[
            ["motor_1_temp_c", "motor_2_temp_c", "motor_3_temp_c", "motor_4_temp_c"]
        ]
        .mean()
        .sort_values("flight_phase")
    )
    return {"counts": counts, "phase_mean": phase_mean, "head": clean.head(8)}
