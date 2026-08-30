"""
Why: テスト実行時の描画バックエンドを固定する。
What: matplotlib を Agg にする。
Assumption / Dependencies: matplotlib。
I/O: なし。
Caution: GUIは使わない。
Future Work: なし。
Change Log:
- 2026-08-30: 初版
"""

import matplotlib

matplotlib.use("Agg")
