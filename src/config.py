"""
Why: 学習アプリ全体の設定値を一箇所に集約する。
What: パス・乱数seed・試験ID・分析で使う閾値を定義する。
Assumption / Dependencies: リポジトリルート配下で実行する。
I/O: 定数のみ。入出力なし。
Caution: ローカル絶対パスや認証情報を書かない。
Future Work: STEP追加時は閾値をここに足す。
Change Log:
- 2026-08-30: 初版
"""

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = PROJECT_ROOT / "data"
CSV_BEFORE: Path = DATA_DIR / "flight_tests_before.csv"
CSV_AFTER: Path = DATA_DIR / "flight_tests_after.csv"

RANDOM_SEED: int = 42

BEFORE_TEST_IDS: tuple[str, ...] = ("FT-B01", "FT-B02", "FT-B03")
AFTER_TEST_IDS: tuple[str, ...] = ("FT-A01", "FT-A02", "FT-A03")

FLIGHT_DURATION_SEC: int = 780
SAMPLE_INTERVAL_SEC: int = 1

HIGH_SPEED_CRUISE_KMH: float = 180.0
MOTOR3_IQR_MULTIPLIER: float = 1.5

PHASES: tuple[str, ...] = (
    "takeoff",
    "climb",
    "cruise",
    "descent",
    "landing",
)

MOTOR_TEMP_COLS: tuple[str, ...] = (
    "motor_1_temp_c",
    "motor_2_temp_c",
    "motor_3_temp_c",
    "motor_4_temp_c",
)

NUMERIC_COLS: tuple[str, ...] = (
    "speed_kmh",
    "altitude_m",
    "acceleration_g",
    "motor_1_rpm",
    "motor_2_rpm",
    "motor_3_rpm",
    "motor_4_rpm",
    *MOTOR_TEMP_COLS,
    "battery_voltage_v",
    "battery_current_a",
    "outside_temp_c",
    "vibration_g",
)
