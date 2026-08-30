"""
Why: 学習アプリの入口。10 STEP を自由に移動できる。
What: サイドバーでSTEPを選び、共通UIを表示する。
Assumption / Dependencies: streamlit, src.ui.step_view。DB・認証なし。
I/O: ブラウザ操作 → 画面描画。
Caution: 学習履歴は保存しない。外部APIは呼ばない。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
"""

from __future__ import annotations

import streamlit as st

from src.ui.content import STEPS
from src.ui.step_view import execute_logic


def validate_input() -> None:
    """起動条件の確認。Streamlit実行を前提とする。

    Raises:
        RuntimeError: STEPS が空のとき。

    Side Effects:
        なし。
    """
    if not STEPS:
        raise RuntimeError("STEPS is empty")


def main() -> None:
    """アプリ本体。"""
    validate_input()
    st.set_page_config(page_title="eVTOL試験データ分析（学習用）", layout="wide")
    st.sidebar.title("学習STEP")
    st.sidebar.caption("順番は自由です。推奨は 1 から 10 です。")
    labels = [f"{n}. {STEPS[n]['title']}" for n in range(1, 11)]
    choice = st.sidebar.radio("移動", labels, index=0)
    step_no = labels.index(choice) + 1
    execute_logic(step_no)


if __name__ == "__main__":
    main()
