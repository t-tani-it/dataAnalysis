# handover.md

## 方針（計画）

- 仮想 eVTOL 飛行試験データを使い、10 STEP の Streamlit 学習アプリを作る
- Python 3.11 + プロジェクト内 `.venv`
- 分析はコード表示 + 実行ボタン。自由移動。STEP10 は見本 + チェックリスト
- DB / 認証 / 外部API / 学習履歴保存は作らない

## 実装（実行）

- `src/data/generate.py` で seed=42 の before/after CSV を生成
- `src/analysis/step01.py` 〜 `step10.py` に分析関数
- `app.py` + `src/ui/` で日本語 UI
- `tests/` で再現性と STEP 実行を確認

## 結果

- 初版としてアプリ・CSV・テスト・GitHub public リポジトリまで到達

## 残タスク

- 実機運用での受け入れ確認（人間が `streamlit run` して通読する）
- 必要になった追加機能は実装前に確認する

## 実行コマンド

```text
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m src.data.generate
.venv\Scripts\python -m pytest
.venv\Scripts\streamlit run app.py
```
