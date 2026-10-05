"""
Why: STEP 10を見本とチェックリストだけの画面に保つ。
What: STEP 10で分析コードや計算結果を表示・実行しないことを確認する。
Assumption / Dependencies: pytest, src.ui.step_view。
I/O: なし。
Caution: Streamlit UIは記録用の軽量スタブで確認する。
Future Work: UIの表示要件を変える場合は本テストも更新する。
Change Log:
- 2026-10-05: 初版
"""

from __future__ import annotations

from contextlib import nullcontext
from typing import Any

from src.ui import step_view


class StreamlitRecorder:
    """Streamlit呼び出し名と引数を記録するスタブ。"""

    def __init__(self) -> None:
        """記録先を初期化する。"""
        self.calls: list[tuple[str, tuple[Any, ...]]] = []

    def __getattr__(self, name: str) -> Any:
        """Streamlitの各呼び出しを記録する関数を返す。"""
        if name == "expander":
            return lambda *args, **kwargs: nullcontext()

        def record(*args: Any, **kwargs: Any) -> bool | None:
            self.calls.append((name, args))
            if name == "button":
                return False
            return None

        return record


def test_step10_shows_only_report_sample_and_checklist(monkeypatch: Any) -> None:
    """STEP 10に分析実行ボタン・結果表示を出さない。"""
    recorder = StreamlitRecorder()
    monkeypatch.setattr(step_view, "st", recorder)

    step_view.execute_logic(10)

    call_names = {name for name, _ in recorder.calls}
    assert not {"code", "button", "dataframe", "pyplot"}.intersection(call_names)
    assert 10 not in step_view.STEP_MODULES

    rendered_text = [str(argument) for _, args in recorder.calls for argument in args]
    assert "報告見本（12項目）" in rendered_text
    assert "チェックリスト" in rendered_text
    assert "4. 分析" not in rendered_text
    assert "5. 結果" not in rendered_text
