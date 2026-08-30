"""
Why: 各STEPの分析関数が例外なく動くことを確認する。
What: 生成CSVがある前提で execute_logic を呼ぶ。
Assumption / Dependencies: pytest, 生成済みCSV。
I/O: data/*.csv を読む。
Caution: 図を閉じないとプロセスが残るため close する。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
"""

from __future__ import annotations

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
    step10,
)
from src.config import CSV_AFTER, CSV_BEFORE


@pytest.fixture(scope="module", autouse=True)
def require_csv() -> None:
    """CSVが無ければスキップする。"""
    if not CSV_BEFORE.is_file() or not CSV_AFTER.is_file():
        pytest.skip("CSV not generated")


@pytest.mark.parametrize(
    "module",
    [step01, step02, step03, step04, step05, step06, step07, step08, step09, step10],
)
def test_step_execute_logic_runs(module: object) -> None:
    """各STEPの execute_logic が辞書を返す。"""
    result = module.execute_logic()
    assert isinstance(result, dict)
    assert result
    plt.close("all")
    for value in result.values():
        if isinstance(value, pd.DataFrame):
            assert not value.empty
