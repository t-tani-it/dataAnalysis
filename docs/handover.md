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
- 2026-09-07: seaborn boxplotのiteritemsエラーを解消。pandas 3.0.5 + seaborn 0.13.2では広形式boxplotが失敗するため、requirementsをpandas<3.0に修正しpandas 2.3.3で16テスト通過を確認
- 2026-10-05: STEP 1〜9のヒント・コード例・固定分析処理の計算条件と出力項目を整合。STEP 8のIQR外れ値率は上下両側を対象とし、STEP 7の件数はMotor 3温度の有効測定数に変更
- 2026-10-05: STEP 10から分析実行・集計表を除き、報告見本とチェックリストのみを表示。出力仕様テストを追加し、32テスト通過。Ruffも全チェック通過
- 2026-10-05: Streamlit AppTestでSTEP 1〜9の分析実行と表表示、STEP 10の分析UI非表示を確認。各STEPで例外なし

## 残タスク

- 実機運用での受け入れ確認（人間が `streamlit run` して通読する）
- 今回の表示修正後、ブラウザ上で各STEPのヒント・コード例・表・グラフを通読する
- 必要になった追加機能は実装前に確認する

## 実行コマンド

```text
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m src.data.generate
.venv\Scripts\python -m pytest
.venv\Scripts\streamlit run app.py
```
