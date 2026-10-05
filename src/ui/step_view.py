"""
Why: 各STEPの画面を共通レイアウトで描画する。
What: STEP 1〜9は課題→ヒント→固定分析→結果を表示し、STEP 10は見本とチェックリストを表示する。
Assumption / Dependencies: streamlit, 各 step モジュール, src.ui.content。
I/O: STEP番号 → 画面描画。
Caution: 学習者コードの eval はしない。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
- 2026-10-05: 表示コードと分析結果の対応を明示し、STEP 10を見本・チェックリスト表示に限定
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from matplotlib.figure import Figure

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
from src.ui.content import STEPS

STEP_MODULES = {
    1: step01,
    2: step02,
    3: step03,
    4: step04,
    5: step05,
    6: step06,
    7: step07,
    8: step08,
    9: step09,
}


def validate_input(step_no: int) -> None:
    """STEP番号が定義済みか確認する。

    Args:
        step_no: 1〜10。

    Returns:
        None

    Raises:
        KeyError: 未定義のSTEP。

    Side Effects:
        なし。

    Examples:
        >>> validate_input(1)
    """
    if step_no not in STEPS:
        raise KeyError(f"unknown step: {step_no}")


def _show_result_value(value: Any) -> None:
    """分析結果の1要素を表示する。"""
    if isinstance(value, pd.DataFrame):
        st.dataframe(value, use_container_width=True)
        return
    if isinstance(value, list) and value and isinstance(value[0], Figure):
        for fig in value:
            st.pyplot(fig, clear_figure=True)
        return
    if isinstance(value, Figure):
        st.pyplot(value, clear_figure=True)
        return
    st.write(value)


def execute_logic(step_no: int) -> None:
    """1 STEP 分の画面を描画する。

    Args:
        step_no: 表示するSTEP。

    Returns:
        None

    Raises:
        KeyError: STEP未定義。

    Side Effects:
        Streamlit にウィジェットを描画する。

    Examples:
        >>> # execute_logic(1)
    """
    validate_input(step_no)
    content = STEPS[step_no]

    st.header(str(content["title"]))
    st.caption("数値は学習用の仮想値です。実在企業の試験データではありません。")

    st.subheader("1. 業務課題")
    st.write(str(content["task"]))

    st.subheader("2. 自分で考える")
    for q in content["think"]:
        st.markdown(f"- {q}")

    st.subheader("3. ヒント")
    hints = list(content["hints"])
    for i, hint in enumerate(hints, start=1):
        with st.expander(f"Hint {i}", expanded=False):
            st.write(hint)

    if step_no == 10:
        st.subheader("報告見本（12項目）")
        for i, line in enumerate(content["report_sample"], start=1):
            st.markdown(f"{i}. {line}")
        st.subheader("チェックリスト")
        for item in content["checklist"]:
            st.markdown(f"- {item}")
        return

    module = STEP_MODULES[step_no]
    st.subheader("4. 分析")
    st.caption(
        "表示コードと同等の固定分析処理を実行します。"
        "表示コード自体や学習者が入力したコードは実行しません。"
    )
    st.code(module.CODE_SAMPLE, language="python")
    run = st.button("表示コードに対応する分析を実行する", key=f"run_{step_no}")

    st.subheader("5. 結果")
    if run:
        try:
            result = module.execute_logic()
        except FileNotFoundError as exc:
            st.error(f"データがありません。生成スクリプトを実行してください。 {exc}")
            return
        except (ValueError, KeyError, ZeroDivisionError) as exc:
            st.error(f"分析に失敗しました: {exc}")
            return
        for name, value in result.items():
            if name in {"figures", "sample_test_id"}:
                continue
            st.markdown(f"**{name}**")
            _show_result_value(value)
        if "figures" in result:
            _show_result_value(result["figures"])
    else:
        st.info("コードを読んだあと、実行ボタンを押すと分析結果が表示されます。")

    st.subheader("6. 解説")
    st.write(str(content["explain"]))

    st.subheader("7. 実務上の意味")
    st.write(str(content["practice"]))

    st.markdown("**事実 / 解釈 / 仮説**")
    st.markdown(f"- 事実: {content['fact']}")
    st.markdown(f"- 解釈: {content['interpretation']}")
    st.markdown(f"- 仮説: {content['hypothesis']}")


def format_output(_unused: None = None) -> None:
    """このモジュールは描画専用のため整形出力はない。"""
