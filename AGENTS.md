# AGENTS.md（dataAnalysis）

## 概要
このプロジェクトは、eVTOL試作機の**仮想飛行試験データ**を使い、
Pythonで「試験データ集約→分析→考察→設計フィードバック」を予習する学習アプリである。
実在企業の内部データ・非公開仕様を再現したものではない。数値は学習用の仮想値である。

OpenCode はこの AGENTS.md を参照して作業を行う。

## 開発環境
- OS：Windows を前提とする
- Python：3.11（プロジェクト内 `.venv`。他プロジェクトの conda env は使わない）
- GPU：使用しない（CPU）

## セキュリティ・公開禁止情報
以下の情報はコード・設定ファイル・ログに絶対に含めないこと：
- ローカルパス（例：C:\Users\...）
- APIキー
- GitHub 操作に必要な個人IDやトークン
- 認証情報全般

## GitHub 運用ルール
- GitHub を使用してバージョン管理を行う
- コード生成・修正時は公開禁止情報が含まれていないか必ずチェックする
- GitHub へ push する前に、禁止情報が含まれていない場合は
  「公開禁止情報は含まれていません」と表示すること

### GitHub 認証・リポジトリ方式
- リモートは HTTPS方式、認証は gh CLI
- リポジトリは public
- 作成コマンド例：`gh repo create dataAnalysis --public --source . --remote origin`
- 認証情報はコードや AGENTS.md に直接記述しない
- ブランチ：`main`

### コミット粒度
- 成果は論理的な区切りごとに分割してコミットする
  （骨格 / データ生成 / 分析 / UI / テスト）
- 1コミットにまとめない

### ハンドオーバー運用（フェーズ完了時・必須）
- フェーズ完了時に `docs/handover.md` を必ず更新する
- 記載内容：方針（計画）→ 実装（実行）→ 結果 → 残タスク → 実行コマンド

## 技術スタック
- Python 3.11
- Streamlit
- pandas / numpy / matplotlib / seaborn
- pytest
- DBなし、認証なし、外部APIなし、クラウドなし

## ディレクトリ構造
- app.py              → Streamlit 入口
- src/config.py       → 設定値
- src/data/generate.py → 仮想試験データの生成
- src/analysis/       → STEP1〜10 の分析
- src/ui/             → 画面と教材テキスト
- data/               → 生成済み CSV
- tests/              → pytest
- docs/handover.md    → 再開用メモ

## コーディング規約

### 1. ファイル先頭コメント（必須）
各ファイルの冒頭に以下をコメントとして記載すること：
- このファイルの目的（Why）
- 実装する機能の仕様（What）
- 前提条件・依存関係（Assumption / Dependencies）
- 入出力の定義（I/O）
- 注意点（Caution）
- 今後の拡張ポイント（Future Work）
- 変更履歴（Change Log）

### 2. 設定値ブロック
- 設定値は src/config.py に集約する
- 乱数 seed は固定する（42）

### 3. 関数構成
- `main()`: 全体の流れ
- `validate_input()`: 入力チェック
- `execute_logic()`: ビジネスロジック
- `format_output()`: 出力整形
- 型ヒント必須、単一責務、副作用を避ける（描画・ファイル出力は明示）

### 4. コード内コメント
- なぜこの処理が必要なのかを書く
- 複雑な箇所は「解説：」で補う

### 5. 出力形式
- PEP8
- 関数に docstring（要約、詳細、Args、Returns、Raises、Side Effects、Examples）
- コメントは“なぜ”、docstring は“何を”

## 学習アプリの制約
- データ分析の学習を最優先する。高機能化しない
- 最低限を超える機能は実装前に確認する
- 学習者コードの eval はしない（コード表示 + 実行ボタン）
- 10 STEP はサイドバーから自由移動
- STEP 10 は見本 + チェックリスト（保存・出力なし）
- 事実 / 解釈 / 仮説を混同しない。相関＝因果と教えない
- 実在企業の内部データである表現をしない

## ビルド・実行・テスト
- 仮想環境：`python -m venv .venv`
- 依存：`.venv\Scripts\pip install -r requirements.txt`
- データ生成：`.venv\Scripts\python -m src.data.generate`
- アプリ：`.venv\Scripts\streamlit run app.py`
- テスト：`.venv\Scripts\python -m pytest`
- Lint：必要なら `ruff`

## OpenCodeへの指示
- コード生成時はこの規約に従うこと
- 新規ファイルは適切なディレクトリに配置すること
- 修正時は差分を明確に示すこと
- 対象はこのフォルダのみ
