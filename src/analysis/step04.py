"""
Why: STEP4で試験全体の分布を把握する。
What: 記述統計とヒストグラム・箱ひげ図用データを返す。
Assumption / Dependencies: pandas, matplotlib, seaborn, src.analysis.common。
I/O: なし → 統計表と Figure。
Caution: 平均だけ見ると分布の歪みを見落とす。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure

from src.analysis.common import load_raw, motor_temp_summary, prepare_for_analysis
from src.config import MOTOR_TEMP_COLS

CODE_SAMPLE = '''import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("data/flight_tests_before.csv")
print(df[["motor_1_temp_c", "motor_2_temp_c", "motor_3_temp_c", "motor_4_temp_c"]].describe())
sns.boxplot(data=df[["motor_1_temp_c", "motor_2_temp_c", "motor_3_temp_c", "motor_4_temp_c"]])
plt.show()
'''


def execute_logic() -> dict[str, Any]:
    """全体像の統計と図を返す。

    Returns:
        describe結果と箱ひげ図・ヒストグラム。

    Raises:
        FileNotFoundError: CSVが無いとき。

    Side Effects:
        matplotlib Figure を生成する（ファイル保存はしない）。

    Examples:
        >>> # execute_logic()["describe"]
    """
    df = prepare_for_analysis(load_raw("before"))
    describe = motor_temp_summary(df).T.reset_index().rename(columns={"index": "column"})
    melted = df.loc[:, list(MOTOR_TEMP_COLS)].melt(var_name="motor", value_name="temp_c")

    fig_box, ax_box = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=melted, x="motor", y="temp_c", ax=ax_box)
    ax_box.set_title("モーター温度の箱ひげ図（改良前）")
    ax_box.set_ylabel("温度 [C]")
    fig_box.tight_layout()

    fig_hist, ax_hist = plt.subplots(figsize=(8, 4))
    for col in MOTOR_TEMP_COLS:
        sns.histplot(df[col].dropna(), bins=30, kde=False, ax=ax_hist, label=col, element="step")
    ax_hist.set_title("モーター温度のヒストグラム（改良前）")
    ax_hist.set_xlabel("温度 [C]")
    ax_hist.legend()
    fig_hist.tight_layout()

    return {
        "describe": describe,
        "figures": [fig_box, fig_hist],
    }
