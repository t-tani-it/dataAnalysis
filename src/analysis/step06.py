"""
Why: STEP6で変数間の関係を見る。相関と因果を混同しない。
What: 散布図と相関行列を返す。
Assumption / Dependencies: pandas, seaborn, matplotlib, src.analysis.common。
I/O: なし → 相関表と図。
Caution: 高い相関は「一緒に動く」ことであり、原因とは限らない。
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

CODE_SAMPLE = '''import pandas as pd
import seaborn as sns

df = pd.read_csv("data/flight_tests_before.csv")
cols = ["speed_kmh", "battery_current_a", "motor_3_temp_c", "vibration_g"]
print(df[cols].corr())
sns.heatmap(df[cols].corr(), annot=True)
'''


def execute_logic() -> dict[str, Any]:
    """相関分析の結果を返す。

    Returns:
        相関行列と散布図・ヒートマップ。

    Raises:
        FileNotFoundError: CSVが無いとき。

    Side Effects:
        matplotlib Figure を生成する。

    Examples:
        >>> # execute_logic()["corr"]
    """
    df = prepare_for_analysis(load_raw("before"))
    cols = ["speed_kmh", "battery_current_a", "motor_3_temp_c", "motor_1_temp_c", "vibration_g"]
    corr = df[cols].corr().reset_index().rename(columns={"index": "column"})

    fig_heat, ax_heat = plt.subplots(figsize=(6, 5))
    sns.heatmap(df[cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax_heat)
    ax_heat.set_title("相関行列（Pearson）")
    fig_heat.tight_layout()

    fig_sc, ax_sc = plt.subplots(figsize=(6, 4))
    sample = df.sample(n=min(800, len(df)), random_state=42)
    sns.scatterplot(data=sample, x="speed_kmh", y="motor_3_temp_c", hue="flight_phase", ax=ax_sc, s=12)
    ax_sc.set_title("速度と Motor 3 温度（標本）")
    fig_sc.tight_layout()

    return {"corr": corr, "figures": [fig_heat, fig_sc]}
