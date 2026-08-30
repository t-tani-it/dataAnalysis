"""
Why: 学習用の仮想飛行試験CSVを再現可能な条件で生成する。
What: 物理的に不自然でない関係を持つ before/after データを出力する。
Assumption / Dependencies: numpy, pandas, src.config。実在企業の内部データではない。
I/O: 入力なし。出力は data/flight_tests_before.csv と data/flight_tests_after.csv。
Caution: 値は学習用の仮想値。列に異常フラグ等の答えを書かない。
Future Work: 試験本数や欠損率を config 化してもよい。
Change Log:
- 2026-08-30: 初版
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import (
    AFTER_TEST_IDS,
    BEFORE_TEST_IDS,
    CSV_AFTER,
    CSV_BEFORE,
    DATA_DIR,
    FLIGHT_DURATION_SEC,
    PHASES,
    RANDOM_SEED,
    SAMPLE_INTERVAL_SEC,
)

COLUMNS: tuple[str, ...] = (
    "timestamp",
    "test_id",
    "flight_phase",
    "speed_kmh",
    "altitude_m",
    "acceleration_g",
    "motor_1_rpm",
    "motor_2_rpm",
    "motor_3_rpm",
    "motor_4_rpm",
    "motor_1_temp_c",
    "motor_2_temp_c",
    "motor_3_temp_c",
    "motor_4_temp_c",
    "battery_voltage_v",
    "battery_current_a",
    "outside_temp_c",
    "vibration_g",
)


def validate_input(seed: int, output_dir: Path) -> None:
    """生成条件が妥当か確認する。

    Args:
        seed: 乱数シード。
        output_dir: CSV出力先ディレクトリ。

    Returns:
        None

    Raises:
        ValueError: seed が負のとき。
        OSError: 出力先を作成できないとき。

    Side Effects:
        出力ディレクトリを作成する。

    Examples:
        >>> validate_input(42, Path("data"))
    """
    if seed < 0:
        raise ValueError("seed must be >= 0")
    output_dir.mkdir(parents=True, exist_ok=True)


def _phase_at(elapsed_sec: int) -> str:
    """経過秒から飛行フェーズを返す。"""
    if elapsed_sec < 60:
        return "takeoff"
    if elapsed_sec < 180:
        return "climb"
    if elapsed_sec < 540:
        return "cruise"
    if elapsed_sec < 700:
        return "descent"
    return "landing"


def _profile(elapsed_sec: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """速度・高度の飛行プロファイルを作る。"""
    speed = np.zeros_like(elapsed_sec, dtype=float)
    altitude = np.zeros_like(elapsed_sec, dtype=float)
    for i, t in enumerate(elapsed_sec):
        if t < 60:
            ratio = t / 60.0
            speed[i] = 80.0 * ratio
            altitude[i] = 50.0 * ratio
        elif t < 180:
            ratio = (t - 60) / 120.0
            speed[i] = 80.0 + 70.0 * ratio
            altitude[i] = 50.0 + 350.0 * ratio
        elif t < 540:
            cruise_t = t - 180
            # 解説: 巡航中盤で高速域に入り、Motor 3 の傾向を分析で発見できるようにする。
            high = 0.5 + 0.5 * np.sin((cruise_t - 80) / 90.0)
            speed[i] = 155.0 + 70.0 * max(0.0, high)
            altitude[i] = 400.0 + 8.0 * np.sin(cruise_t / 40.0)
        elif t < 700:
            ratio = (t - 540) / 160.0
            speed[i] = 160.0 - 80.0 * ratio
            altitude[i] = 400.0 - 350.0 * ratio
        else:
            ratio = (t - 700) / 80.0
            speed[i] = max(0.0, 80.0 * (1.0 - ratio))
            altitude[i] = max(0.0, 50.0 * (1.0 - ratio))
    return speed, altitude


def _simulate_one_flight(
    rng: np.random.Generator,
    test_id: str,
    start_time: pd.Timestamp,
    outside_temp_c: float,
    motor3_extra_c: float,
    inject_quality_issues: bool,
) -> pd.DataFrame:
    """1試験分の時系列を生成する。"""
    elapsed = np.arange(0, FLIGHT_DURATION_SEC, SAMPLE_INTERVAL_SEC)
    n = len(elapsed)
    phases = np.array([_phase_at(int(t)) for t in elapsed])
    speed, altitude = _profile(elapsed)
    speed = np.clip(speed + rng.normal(0.0, 1.8, n), 0.0, None)
    altitude = np.clip(altitude + rng.normal(0.0, 1.2, n), 0.0, None)

    accel = np.gradient(speed / 3.6) / 9.81
    accel = accel + rng.normal(0.0, 0.03, n)

    load = 0.25 + speed / 280.0 + np.clip(accel, 0.0, None) * 0.35
    current = 80.0 + load * 220.0 + rng.normal(0.0, 4.0, n)
    voltage = 403.0 - current * 0.045 + rng.normal(0.0, 0.4, n)

    rpm_base = 900.0 + speed * 18.0 + load * 400.0
    rpm = np.column_stack(
        [np.clip(rpm_base + rng.normal(0.0, 35.0, n), 0.0, None) for _ in range(4)]
    )

    cruise_high = (phases == "cruise") & (speed >= 180.0)
    extra = np.where(cruise_high, motor3_extra_c * ((speed - 180.0) / 40.0), 0.0)

    temp = np.zeros((n, 4), dtype=float)
    ambient = outside_temp_c + altitude * 0.002
    for i in range(n):
        heating = 18.0 + current[i] * 0.09 + load[i] * 12.0
        for m in range(4):
            prev = ambient[i] + 8.0 if i == 0 else temp[i - 1, m]
            target = ambient[i] + heating
            if m == 2:
                target += extra[i]
            temp[i, m] = prev * 0.94 + target * 0.06 + rng.normal(0.0, 0.12)

    vibration = 0.12 + load * 0.35 + rng.normal(0.0, 0.02, n)

    frame = pd.DataFrame(
        {
            "timestamp": start_time + pd.to_timedelta(elapsed, unit="s"),
            "test_id": test_id,
            "flight_phase": phases,
            "speed_kmh": speed,
            "altitude_m": altitude,
            "acceleration_g": accel,
            "motor_1_rpm": rpm[:, 0],
            "motor_2_rpm": rpm[:, 1],
            "motor_3_rpm": rpm[:, 2],
            "motor_4_rpm": rpm[:, 3],
            "motor_1_temp_c": temp[:, 0],
            "motor_2_temp_c": temp[:, 1],
            "motor_3_temp_c": temp[:, 2],
            "motor_4_temp_c": temp[:, 3],
            "battery_voltage_v": voltage,
            "battery_current_a": current,
            "outside_temp_c": outside_temp_c + rng.normal(0.0, 0.15, n),
            "vibration_g": vibration,
        }
    )

    if inject_quality_issues:
        frame = _inject_quality_issues(rng, frame)
    return frame


def _inject_quality_issues(rng: np.random.Generator, frame: pd.DataFrame) -> pd.DataFrame:
    """欠損・重複・外れ値・センサー異常候補を混入する。"""
    out = frame.copy()
    n = len(out)
    miss_cols = ["battery_current_a", "vibration_g", "motor_2_temp_c", "altitude_m"]
    for col in miss_cols:
        idx = rng.choice(n, size=max(4, n // 80), replace=False)
        out.loc[out.index[idx], col] = np.nan

    dup_at = int(n * 0.33)
    out = pd.concat([out.iloc[: dup_at + 1], out.iloc[[dup_at]], out.iloc[dup_at + 1 :]], ignore_index=True)

    spike = int(n * 0.72)
    out.loc[spike, "vibration_g"] = 3.8
    out.loc[int(n * 0.21), "motor_1_temp_c"] = 142.0
    out.loc[int(n * 0.55), "speed_kmh"] = -12.0
    return out


def execute_logic(seed: int = RANDOM_SEED) -> tuple[pd.DataFrame, pd.DataFrame]:
    """改良前・改良後の試験データを生成する。

    Args:
        seed: 乱数シード。

    Returns:
        (before, after) の DataFrame。

    Raises:
        ValueError: 生成行が空のとき。

    Side Effects:
        なし。

    Examples:
        >>> before, after = execute_logic(42)
        >>> set(before.columns) == set(COLUMNS)
        True
    """
    rng = np.random.default_rng(seed)
    before_frames: list[pd.DataFrame] = []
    after_frames: list[pd.DataFrame] = []

    outside_temps = (18.0, 22.0, 27.0)
    start_base = pd.Timestamp("2024-06-01 09:00:00")

    for i, test_id in enumerate(BEFORE_TEST_IDS):
        before_frames.append(
            _simulate_one_flight(
                rng=rng,
                test_id=test_id,
                start_time=start_base + pd.Timedelta(days=i),
                outside_temp_c=outside_temps[i],
                motor3_extra_c=18.0,
                inject_quality_issues=True,
            )
        )

    for i, test_id in enumerate(AFTER_TEST_IDS):
        after_frames.append(
            _simulate_one_flight(
                rng=rng,
                test_id=test_id,
                start_time=start_base + pd.Timedelta(days=14 + i),
                outside_temp_c=outside_temps[i],
                motor3_extra_c=5.0,
                inject_quality_issues=True,
            )
        )

    before = pd.concat(before_frames, ignore_index=True)
    after = pd.concat(after_frames, ignore_index=True)
    if before.empty or after.empty:
        raise ValueError("generated data is empty")
    return before, after


def format_output(before: pd.DataFrame, after: pd.DataFrame) -> tuple[Path, Path]:
    """CSV に保存し、パスを返す。

    Args:
        before: 改良前データ。
        after: 改良後データ。

    Returns:
        保存した before/after のパス。

    Raises:
        OSError: 書き込み失敗時。

    Side Effects:
        data 配下に CSV を上書きする。

    Examples:
        >>> # format_output(before, after)
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    before.to_csv(CSV_BEFORE, index=False)
    after.to_csv(CSV_AFTER, index=False)
    return CSV_BEFORE, CSV_AFTER


def main() -> None:
    """データ生成の入口。"""
    validate_input(RANDOM_SEED, DATA_DIR)
    before, after = execute_logic(RANDOM_SEED)
    before_path, after_path = format_output(before, after)
    print(f"wrote {before_path.name} rows={len(before)}")
    print(f"wrote {after_path.name} rows={len(after)}")


if __name__ == "__main__":
    main()
