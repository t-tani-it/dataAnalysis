"""
Why: データ生成の再現性と列仕様を固定する。
What: seed固定、列名、before/after の差、答え列が無いことを検証する。
Assumption / Dependencies: pytest, pandas, src.data.generate。
I/O: なし。
Caution: 実ファイルを必須にしない。メモリ上の生成結果を使う。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
"""

from __future__ import annotations

import pandas as pd

from src.data.generate import COLUMNS, execute_logic


def test_reproducible_with_seed() -> None:
    """同じ seed なら同じデータになる。"""
    a1, b1 = execute_logic(42)
    a2, b2 = execute_logic(42)
    pd.testing.assert_frame_equal(a1, a2)
    pd.testing.assert_frame_equal(b1, b2)


def test_columns_match_spec() -> None:
    """列名が仕様どおりである。"""
    before, after = execute_logic(42)
    assert list(before.columns) == list(COLUMNS)
    assert list(after.columns) == list(COLUMNS)


def test_no_answer_columns() -> None:
    """答えが直接書かれた列を持たない。"""
    before, after = execute_logic(42)
    forbidden = {"is_anomaly", "label", "answer", "motor3_issue"}
    assert forbidden.isdisjoint(before.columns)
    assert forbidden.isdisjoint(after.columns)


def test_quality_issues_exist() -> None:
    """欠損と重複が学習用に含まれる。"""
    before, _ = execute_logic(42)
    assert before.isna().sum().sum() > 0
    assert int(before.duplicated().sum()) > 0


def test_motor3_hotter_in_high_cruise_before() -> None:
    """改良前の高速巡航で Motor 3 平均が Motor 1 より高い。"""
    before, _ = execute_logic(42)
    high = before[(before["flight_phase"] == "cruise") & (before["speed_kmh"] >= 180)]
    assert high["motor_3_temp_c"].mean() > high["motor_1_temp_c"].mean()


def test_after_cooler_than_before_on_same_condition() -> None:
    """同条件で after の Motor 3 平均が before より低い。"""
    before, after = execute_logic(42)
    cond = lambda d: (d["flight_phase"] == "cruise") & (d["speed_kmh"] >= 180)
    assert after.loc[cond(after), "motor_3_temp_c"].mean() < before.loc[cond(before), "motor_3_temp_c"].mean()
