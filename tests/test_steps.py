"""
Why: 各STEPの分析関数が例外なく動き、画面に出す結果仕様を保つ。
What: STEP 1〜9の表・図・コード例の基本契約を検証する。
Assumption / Dependencies: pytest, 生成済みCSV。
I/O: data/*.csv を読む。
Caution: 図を閉じないとプロセスが残るため close する。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
- 2026-10-05: STEP別の出力契約とコード例の構文検証を追加
"""

from __future__ import annotations

from collections.abc import Iterator

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from src.analysis import (
    step01,
    step02,
    step03,
    step04,
    step05,
    step06,
    step07,
    step08,
    step09,
)
from src.analysis.common import load_raw, prepare_for_analysis
from src.config import CSV_AFTER, CSV_BEFORE, HIGH_SPEED_CRUISE_KMH


@pytest.fixture(scope="module", autouse=True)
def require_csv() -> None:
    """CSVが無ければスキップする。"""
    if not CSV_BEFORE.is_file() or not CSV_AFTER.is_file():
        pytest.skip("CSV not generated")


@pytest.fixture(autouse=True)
def close_figures() -> Iterator[None]:
    """各テストの描画結果を後続テストへ残さない。"""
    yield
    plt.close("all")


@pytest.mark.parametrize(
    ("module", "expected_keys", "figure_count"),
    [
        (step01, {"shape", "dtypes", "head", "describe", "unique_phase", "unique_test"}, 0),
        (step02, {"missing", "duplicated", "ranges"}, 0),
        (step03, {"counts", "phase_mean", "head"}, 0),
        (step04, {"describe", "figures"}, 2),
        (step05, {"phase_mean", "figures", "sample_test_id"}, 1),
        (step06, {"corr", "figures"}, 2),
        (step07, {"by_condition", "figures"}, 1),
        (step08, {"summary", "by_test", "figures"}, 1),
        (step09, {"compare", "figures"}, 1),
    ],
)
def test_step_output_contract(module: object, expected_keys: set[str], figure_count: int) -> None:
    """各STEPの表・図が画面表示の契約どおり返る。"""
    try:
        result = module.execute_logic()
        assert set(result) == expected_keys
        assert len(result.get("figures", [])) == figure_count
        for value in result.values():
            if isinstance(value, pd.DataFrame):
                assert not value.empty
    finally:
        plt.close("all")


@pytest.mark.parametrize(
    "module",
    [step01, step02, step03, step04, step05, step06, step07, step08, step09],
)
def test_displayed_code_sample_is_valid_python(module: object) -> None:
    """画面に表示する固定コード例の構文が正しい。"""
    compile(module.CODE_SAMPLE, f"{module.__name__}.CODE_SAMPLE", "exec")


def test_step01_preview_matches_code_sample() -> None:
    """STEP 1の表示行数がコード例と同じ8行である。"""
    result = step01.execute_logic()
    assert len(result["head"]) == 8


def test_step02_range_table_matches_code_sample() -> None:
    """STEP 2の範囲表にコード例と同じ統計量がある。"""
    result = step02.execute_logic()
    assert list(result["ranges"].columns) == ["column", "min", "max", "mean"]
    assert result["duplicated"]["metric"].tolist() == ["rows", "duplicated_rows", "duplicate_rate"]


def test_step03_phase_table_contains_all_motors() -> None:
    """STEP 3のフェーズ別表に4モーターの温度列がある。"""
    result = step03.execute_logic()
    assert list(result["phase_mean"].columns) == [
        "flight_phase",
        "motor_1_temp_c",
        "motor_2_temp_c",
        "motor_3_temp_c",
        "motor_4_temp_c",
    ]


def test_step05_phase_table_and_plot_match_code_sample() -> None:
    """STEP 5の表と図に4モーター平均と3本の時系列がある。"""
    try:
        result = step05.execute_logic()
        assert list(result["phase_mean"].columns) == [
            "flight_phase",
            "motor_1_temp_c",
            "motor_2_temp_c",
            "motor_3_temp_c",
            "motor_4_temp_c",
        ]
        assert len(result["figures"][0].axes[0].lines) == 3
    finally:
        plt.close("all")


def test_step07_reports_valid_motor3_observation_count() -> None:
    """STEP 7の件数列がMotor 3温度の有効値数を示す。"""
    result = step07.execute_logic()
    actual = result["by_condition"]
    assert list(actual.columns) == [
        "flight_phase",
        "high_speed",
        "motor_3_mean",
        "motor_3_max",
        "motor_1_mean",
        "motor_3_valid_n",
        "temp_gap",
    ]
    frame = prepare_for_analysis(load_raw("before")).copy()
    frame["high_speed"] = frame["speed_kmh"] >= HIGH_SPEED_CRUISE_KMH
    expected_counts = frame.groupby(["flight_phase", "high_speed"])["motor_3_temp_c"].count()
    for row in actual.itertuples(index=False):
        assert row.motor_3_valid_n == expected_counts.loc[(row.flight_phase, row.high_speed)]


def test_step08_iqr_rate_includes_both_tails() -> None:
    """STEP 8のIQR外れ値率が下限・上限の両方を対象にする。"""
    result = step08.execute_logic()
    summary = result["summary"].set_index("metric")["value"]
    df = prepare_for_analysis(load_raw("before"))
    values = df["motor_3_temp_c"].dropna()
    expected_rate = float(((values < summary["iqr_lower"]) | (values > summary["iqr_upper"])).mean())
    assert summary["iqr_outlier_rate"] == pytest.approx(expected_rate)
    z = (values - values.mean()) / values.std(ddof=0)
    assert summary["z_abs_gt_3_rate"] == pytest.approx(float((z.abs() > 3).mean()))


def test_step09_comparison_table_matches_code_sample() -> None:
    """STEP 9の比較表にコード例と同じ5指標がある。"""
    result = step09.execute_logic()
    assert result["compare"]["metric"].tolist() == [
        "high_cruise_m3_mean_before",
        "high_cruise_m3_mean_after",
        "mean_reduction_rate",
        "m3_minus_m1_before",
        "m3_minus_m1_after",
    ]
