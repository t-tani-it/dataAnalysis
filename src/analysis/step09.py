"""
Why: STEP9で設計変更の効果を before/after で見る。
What: 同条件（巡航かつ高速）での温度差と比較図を返す。
Assumption / Dependencies: pandas, seaborn, src.analysis.common, src.config。
I/O: なし → 比較表と図。
Caution: 条件が揃っていない比較は効果を過大評価しやすい。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.analysis.common import load_raw, prepare_for_analysis
from src.config import HIGH_SPEED_CRUISE_KMH

CODE_SAMPLE = '''import pandas as pd

before = pd.read_csv("data/flight_tests_before.csv")
after = pd.read_csv("data/flight_tests_after.csv")
cond = lambda d: (d["flight_phase"] == "cruise") & (d["speed_kmh"] >= 180)
b = before.loc[cond(before), "motor_3_temp_c"].mean()
a = after.loc[cond(after), "motor_3_temp_c"].mean()
print(b, a, (b - a) / b)
'''


def _high_cruise(frame: pd.DataFrame) -> pd.DataFrame:
    """高速巡航行に絞る。"""
    return frame[(frame["flight_phase"] == "cruise") & (frame["speed_kmh"] >= HIGH_SPEED_CRUISE_KMH)]


def execute_logic() -> dict[str, Any]:
    """Before/After 比較を返す。

    Returns:
        改善率テーブルと箱ひげ図。

    Raises:
        FileNotFoundError: CSVが無いとき。
        ZeroDivisionError: 改良前平均が0のとき。

    Side Effects:
        matplotlib Figure を生成する。

    Examples:
        >>> # execute_logic()["compare"]
    """
    before = _high_cruise(prepare_for_analysis(load_raw("before")))
    after = _high_cruise(prepare_for_analysis(load_raw("after")))
    b_mean = float(before["motor_3_temp_c"].mean())
    a_mean = float(after["motor_3_temp_c"].mean())
    b_gap = float(before["motor_3_temp_c"].mean() - before["motor_1_temp_c"].mean())
    a_gap = float(after["motor_3_temp_c"].mean() - after["motor_1_temp_c"].mean())
    if b_mean == 0:
        raise ZeroDivisionError("before mean is 0")
    compare = pd.DataFrame(
        {
            "metric": [
                "high_cruise_m3_mean_before",
                "high_cruise_m3_mean_after",
                "mean_reduction_rate",
                "m3_minus_m1_before",
                "m3_minus_m1_after",
            ],
            "value": [
                b_mean,
                a_mean,
                (b_mean - a_mean) / b_mean,
                b_gap,
                a_gap,
            ],
        }
    )

    plot_df = pd.concat(
        [
            before.assign(design="before")[["motor_3_temp_c", "design"]],
            after.assign(design="after")[["motor_3_temp_c", "design"]],
        ],
        ignore_index=True,
    )
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=plot_df, x="design", y="motor_3_temp_c", ax=ax)
    ax.set_title("高速巡航の Motor 3 温度（Before / After）")
    fig.tight_layout()

    return {"compare": compare, "figures": [fig]}
