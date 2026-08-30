"""
Why: STEP7でどの条件で現象が起きるか見る。
What: フェーズ×速度帯の集計と箱ひげ図を返す。
Assumption / Dependencies: pandas, seaborn, src.analysis.common, src.config。
I/O: なし → 条件別表と図。
Caution: 条件分けの切り方で見え方が変わる。
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

df = pd.read_csv("data/flight_tests_before.csv")
df["high_speed"] = df["speed_kmh"] >= 180
print(df.groupby(["flight_phase", "high_speed"])["motor_3_temp_c"].mean())
'''


def execute_logic() -> dict[str, Any]:
    """条件別集計を返す。

    Returns:
        クロス集計と箱ひげ図。

    Raises:
        FileNotFoundError: CSVが無いとき。

    Side Effects:
        matplotlib Figure を生成する。

    Examples:
        >>> # execute_logic()["by_condition"]
    """
    df = prepare_for_analysis(load_raw("before"))
    df = df.copy()
    df["high_speed"] = df["speed_kmh"] >= HIGH_SPEED_CRUISE_KMH
    by_condition = (
        df.groupby(["flight_phase", "high_speed"], as_index=False)
        .agg(
            motor_3_mean=("motor_3_temp_c", "mean"),
            motor_3_max=("motor_3_temp_c", "max"),
            motor_1_mean=("motor_1_temp_c", "mean"),
            n=("motor_3_temp_c", "size"),
        )
        .sort_values(["flight_phase", "high_speed"])
    )
    by_condition["temp_gap"] = by_condition["motor_3_mean"] - by_condition["motor_1_mean"]

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=df, x="flight_phase", y="motor_3_temp_c", hue="high_speed", ax=ax)
    ax.set_title("フェーズ・速度帯別の Motor 3 温度")
    fig.tight_layout()

    return {"by_condition": by_condition, "figures": [fig]}
