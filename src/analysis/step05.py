"""
Why: STEP5で温度上昇がいつ起きたかを見る。
What: 時系列・移動平均・フェーズ別平均を返す。
Assumption / Dependencies: pandas, matplotlib, src.analysis.common。
I/O: なし → 表と時系列図。
Caution: 1試験だけでなく複数試験を重ねて見る。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
- 2026-10-05: 表示コードの移動平均条件とフェーズ集計を整合
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt

from src.analysis.common import load_raw, prepare_for_analysis
from src.config import MOTOR_TEMP_COLS

CODE_SAMPLE = '''import matplotlib.pyplot as plt

from src.analysis.common import load_raw, prepare_for_analysis
from src.config import MOTOR_TEMP_COLS

df = prepare_for_analysis(load_raw("before"))
first_id = str(df["test_id"].iloc[0])
one = df[df["test_id"] == first_id].sort_values("timestamp").copy()
one["motor_3_ma20"] = one["motor_3_temp_c"].rolling(20, min_periods=1).mean()
phase_mean = (
    df.groupby("flight_phase", as_index=False)[list(MOTOR_TEMP_COLS)]
    .mean()
    .sort_values("flight_phase")
)
print("phase_mean")
print(phase_mean)

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(one["timestamp"], one["motor_3_temp_c"], alpha=0.45, label="Motor 3")
ax.plot(one["timestamp"], one["motor_1_temp_c"], alpha=0.45, label="Motor 1")
ax.plot(one["timestamp"], one["motor_3_ma20"], label="Motor 3 移動平均20")
ax.set_title(f"温度の時系列（{first_id}）")
ax.set_ylabel("温度 [C]")
ax.legend()
fig.tight_layout()
plt.show()
'''


def execute_logic() -> dict[str, Any]:
    """時系列分析の結果を返す。

    Returns:
        フェーズ別平均と時系列図。

    Raises:
        FileNotFoundError: CSVが無いとき。

    Side Effects:
        matplotlib Figure を生成する。

    Examples:
        >>> # execute_logic()["phase_mean"]
    """
    df = prepare_for_analysis(load_raw("before"))
    first_id = str(df["test_id"].iloc[0])
    one = df[df["test_id"] == first_id].sort_values("timestamp").copy()
    one["motor_3_ma20"] = one["motor_3_temp_c"].rolling(20, min_periods=1).mean()

    phase_mean = (
        df.groupby("flight_phase", as_index=False)[list(MOTOR_TEMP_COLS)]
        .mean()
        .sort_values("flight_phase")
    )

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(one["timestamp"], one["motor_3_temp_c"], alpha=0.45, label="Motor 3")
    ax.plot(one["timestamp"], one["motor_1_temp_c"], alpha=0.45, label="Motor 1")
    ax.plot(one["timestamp"], one["motor_3_ma20"], label="Motor 3 移動平均20")
    ax.set_title(f"温度の時系列（{first_id}）")
    ax.set_ylabel("温度 [C]")
    ax.legend()
    fig.tight_layout()

    return {"phase_mean": phase_mean, "figures": [fig], "sample_test_id": first_id}
