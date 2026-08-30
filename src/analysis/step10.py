"""
Why: STEP10で分析結果を設計向けの観点に再構成する。
What: 主要指標を1枚の要約表にまとめる。見本本文は UI 側。
Assumption / Dependencies: 他STEPの execute_logic を再利用する。
I/O: なし → 要約表。
Caution: これは学習用の整理であり、実機の設計判断そのものではない。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
"""

from __future__ import annotations

import pandas as pd

from src.analysis.step02 import execute_logic as step02
from src.analysis.step07 import execute_logic as step07
from src.analysis.step09 import execute_logic as step09

CODE_SAMPLE = '''# STEP1〜9の結果を、事実・解釈・仮説に分けて書き出す。
# 画面の見本とチェックリストを使って、自分で報告文を組み立てる。
'''


def execute_logic() -> dict[str, pd.DataFrame]:
    """設計フィードバック用の要約指標を返す。

    Returns:
        品質・発生条件・改善効果の要約。

    Raises:
        FileNotFoundError: CSVが無いとき。

    Side Effects:
        なし（下位関数が Figure を作る場合がある）。

    Examples:
        >>> # execute_logic()["summary"]
    """
    quality = step02()["duplicated"]
    cond = step07()["by_condition"]
    effect = step09()["compare"]
    cruise_high = cond[(cond["flight_phase"] == "cruise") & cond["high_speed"]]
    summary = pd.DataFrame(
        {
            "item": [
                "duplicated_rows",
                "high_cruise_m3_mean",
                "high_cruise_temp_gap_m3_m1",
                "after_mean_reduction_rate",
            ],
            "value": [
                float(quality.loc[quality["metric"] == "duplicated_rows", "value"].iloc[0]),
                float(cruise_high["motor_3_mean"].mean()) if not cruise_high.empty else float("nan"),
                float(cruise_high["temp_gap"].mean()) if not cruise_high.empty else float("nan"),
                float(effect.loc[effect["metric"] == "mean_reduction_rate", "value"].iloc[0]),
            ],
        }
    )
    return {"summary": summary}
