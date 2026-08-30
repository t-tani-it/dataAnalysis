"""
Why: 各STEPが同じCSVを同じルールで読めるようにする。
What: CSV読込・前処理済みフレーム作成・図の日本語フォント設定。
Assumption / Dependencies: pandas, matplotlib, src.config。
I/O: CSVパス → DataFrame。
Caution: 学習用仮想データのみを対象とする。
Future Work: キャッシュ方針を変える場合はここを変更する。
Change Log:
- 2026-08-30: 初版
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.config import CSV_AFTER, CSV_BEFORE, MOTOR_TEMP_COLS, NUMERIC_COLS

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "MS Gothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def validate_input(csv_path: Path) -> None:
    """CSVが存在することを確認する。

    Args:
        csv_path: 読み込むCSVパス。

    Returns:
        None

    Raises:
        FileNotFoundError: ファイルが無いとき。

    Side Effects:
        なし。

    Examples:
        >>> # validate_input(CSV_BEFORE)
    """
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path.name}")


def load_raw(which: str = "before") -> pd.DataFrame:
    """生成済みCSVをそのまま読む。

    Args:
        which: "before" または "after"。

    Returns:
        生データの DataFrame。

    Raises:
        ValueError: which が不正なとき。
        FileNotFoundError: CSVが無いとき。

    Side Effects:
        なし。

    Examples:
        >>> # df = load_raw("before")
    """
    path = CSV_BEFORE if which == "before" else CSV_AFTER
    if which not in {"before", "after"}:
        raise ValueError("which must be 'before' or 'after'")
    validate_input(path)
    return pd.read_csv(path)


def prepare_for_analysis(frame: pd.DataFrame) -> pd.DataFrame:
    """分析用に最低限の前処理をする。

    Args:
        frame: 生データ。

    Returns:
        timestamp型変換・重複削除・負の速度を欠損化した DataFrame。

    Raises:
        KeyError: 必須列が無いとき。

    Side Effects:
        なし。元の frame は変更しない。

    Examples:
        >>> # clean = prepare_for_analysis(load_raw("before"))
    """
    out = frame.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"])
    out = out.drop_duplicates()
    if "speed_kmh" in out.columns:
        out.loc[out["speed_kmh"] < 0, "speed_kmh"] = pd.NA
    return out.reset_index(drop=True)


def motor_temp_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """モーター温度列の記述統計を返す。

    Args:
        frame: 分析用 DataFrame。

    Returns:
        describe() 結果。

    Raises:
        KeyError: 温度列が無いとき。

    Side Effects:
        なし。

    Examples:
        >>> # motor_temp_summary(df)
    """
    return frame.loc[:, list(MOTOR_TEMP_COLS)].describe()


def numeric_columns() -> tuple[str, ...]:
    """数値列名を返す。"""
    return NUMERIC_COLS
