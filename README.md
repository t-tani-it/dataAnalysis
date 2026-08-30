# dataAnalysis

eVTOL試作機の**仮想飛行試験データ**を使い、Pythonでデータ分析実務を予習する学習アプリです。

実在企業のシステムや非公開データを再現したものではありません。数値は学習用の仮想値です。

## 目的

試験データの確認 → 品質確認 → 前処理 → 分析 → 傾向の発見 → 原因候補の整理 → 設計フィードバック → 改修後評価、までを疑似体験します。

アプリを高機能にすることが目的ではありません。

## 必要環境

- Windows
- Python 3.11
- プロジェクト内 `.venv`（他プロジェクトの conda 環境は使いません）

## 入手（GitHub から）

```text
git clone https://github.com/t-tani-it/dataAnalysis.git
cd dataAnalysis
```

## セットアップ（初回のみ）

```text
cd dataAnalysis
python -m venv .venv
.venv\Scripts\activate
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m src.data.generate
```

## 実行（セットアップ済みの場合）

```text
cd dataAnalysis
.venv\Scripts\activate
streamlit run app.py
```

- ブラウザで `http://localhost:8501` が開きます（開かない場合は URL を手動で開いてください）
- 終了は `Ctrl + C`

## テスト / データ再生成

```text
cd dataAnalysis
.venv\Scripts\python -m pytest
.venv\Scripts\python -m src.data.generate
```

## データ生成条件

| 項目 | 値 |
|------|-----|
| 乱数 seed | 42 |
| 改良前試験 | FT-B01, FT-B02, FT-B03 |
| 改良後試験 | FT-A01, FT-A02, FT-A03 |
| 1試験の長さ | 780 秒、1 秒間隔 |
| フェーズ | takeoff / climb / cruise / descent / landing |
| 物理関係（仮想） | 速度上昇 → 負荷上昇 → 電流上昇 → モーター温度上昇 |
| 学習用の仕込み | 高速巡航で Motor 3 の温度が相対的に高い。改良後は差が縮小 |
| 品質の仕込み | 欠損、重複、外れ値、センサー異常候補、負の速度 |
| 答え列 | なし（異常フラグ等は持たない） |

生成コードは `src/data/generate.py` です。同じ seed で再生成できます。生成済み CSV は `data/` にあります。

## 10 STEP

1. データを理解する
2. データ品質を確認する
3. 分析できる形にする
4. 全体像を把握する
5. いつ起きたか
6. 何が関係しているか（相関≠因果）
7. どの条件か
8. 異常かの判断（IQR / Z-score）
9. 設計変更の Before / After
10. 設計向けフィードバック（見本 + チェックリスト）

各 STEP は「課題 → 自分で考える → ヒント → コード表示と実行 → 結果 → 解説 → 実務上の意味」です。STEP 間は自由に移動できます。

## 使っているライブラリ

streamlit, pandas, numpy, matplotlib, seaborn, pytest

## 使わないもの

データベース、認証、クラウド、外部 API、学習履歴の保存、学習者コードの任意実行
