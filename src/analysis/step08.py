"""
Why: STEP8で統計的外れ値と機体異常の候補を区別する。
What: IQR と Z-score で Motor 3 を評価する。
Assumption / Dependencies: pandas, numpy, src.analysis.common。
I/O: なし → 外れ値件数と図。
Caution: 外れ値=故障ではない。運用条件の違いでも外れ値は出る。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.analysis.common import load_raw, prepare_for_analysis
from src.config import MOTOR3_IQR_MULTIPLIER

CODE_SAMPLE = '''import pandas as pd

s = pd.read_csv("data/flight_tests_before.csv")["motor_3_temp_c"]
q1, q3 = s.quantile(0.25), s.quantile(0.75)
iqr = q3 - q1
upper = q3 + 1.5 * iqr
print(upper, (s > upper).mean())
z = (s - s.mean()) / s.std()
print((z.abs() > 3).mean())
'''


def execute_logic() -> dict[str, Any]:
    """外れ値判定の結果を返す。

    Returns:
        IQR/Z-score の要約と分布図。

    Raises:
        FileNotFoundError: CSVが無いとき。

    Side Effects:
        matplotlib Figure を生成する。

    Examples:
        >>> # execute_logic()["summary"]
    """
    df = prepare_for_analysis(load_raw("before"))
    s = df["motor_3_temp_c"].dropna()
    q1 = float(s.quantile(0.25))
    q3 = float(s.quantile(0.75))
    iqr = q3 - q1
    upper = q3 + MOTOR3_IQR_MULTIPLIER * iqr
    lower = q1 - MOTOR3_IQR_MULTIPLIER * iqr
    z = (s - s.mean()) / s.std(ddof=0)
    summary = pd.DataFrame(
        {
            "metric": [
                "q1",
                "q3",
                "iqr",
                "iqr_upper",
                "iqr_outlier_rate",
                "z_abs_gt_3_rate",
            ],
            "value": [
                q1,
                q3,
                iqr,
                upper,
                float((s > upper).mean()),
                float((np.abs(z) > 3).mean()),
            ],
        }
    )
    by_test = (
        df.groupby("test_id")["motor_3_temp_c"]
        .agg(["mean", "max", "std"])
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(s, bins=30, ax=ax)
    ax.axvline(upper, color="red", linestyle="--", label="IQR上限")
    ax.axvline(lower, color="red", linestyle="--")
    ax.set_title("Motor 3 温度と IQR 範囲")
    ax.legend()
    fig.tight_layout()

    return {"summary": summary, "by_test": by_test, "figures": [fig]}
