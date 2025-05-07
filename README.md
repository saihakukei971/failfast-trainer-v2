# Infra Risk Simulator

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

インフラエンジニア/SRE向けの障害対応訓練・評価ツールです。確率論とリスク管理を応用し、クラウド・オンプレミス問わず現場判断力を再現・向上できます。

---

## 🌟 特徴

- **現実的な障害シナリオ**：AWS/Azure/オンプレを問わない20+種のイベント
- **確率ベースの判断モデル**：状態変化に応じて成功率が自動変動
- **リスク対応戦略の訓練**：短期復旧と長期安定性のバランスを判断
- **数値評価付きパフォーマンス**：成功率・リカバリ速度・選択傾向をスコア化

---

## 🧠 設計思想

本ツールは選択肢クイズではありません。ブラックジャックの「引く／止まる」の期待値計算を応用し、インフラ状態に基づいた動的成功率・意思決定の緊張感を体験できます。

### 例：

- CPU負荷 > 90%：サーバ再起動成功率が 70% → 40% に低下
- アラート多数時：対応判断の失敗リスク上昇
- 状況に応じて「控える」判断が最適なケースも出現

---

## 📋 機能概要

- シナリオシミュレーション（20件以上）
- 状態連動の成功率計算ロジック
- CLI / Web 両対応（FlaskベースUI）
- ログ保存・レポート自動生成
- CSVによるカスタム定義可能（イベント・アクション）

---

## 🚀 クイックスタート

```bash
# クローン
$ git clone https://github.com/yourusername/infra-risk-simulator.git
$ cd infra-risk-simulator

# 依存関係インストール
$ pip install -r requirements.txt

# データディレクトリ作成
$ mkdir -p data/logs data/reports
CLI版起動
bash
コピーする
編集する
$ python cli/main.py
# 特定シナリオ指定
$ python cli/main.py --scenario S001
Web版起動
bash
コピーする
編集する
$ python web/app.py
# アクセス
http://127.0.0.1:5000/
📊 サンプルシナリオ
ID	名前	概要	難易度
S001	Webサーバ過負荷	キャンペーン集中によりCPU高負荷に	NORMAL
S007	AWS RDS高負荷	レプリケーション遅延により応答が鈍化	NORMAL
S010	SSL証明書期限切れ	HTTPS接続が不可能に	NORMAL
S014	K8s Pod起動エラー	ConfigMapミスによるPod連続失敗	HARD
S020	地震による障害	UPS切替と再起動対応が同時発生	EXPERT

🧪 テストと開発
bash
コピーする
編集する
# ユニットテスト
pytest

# カバレッジ付きテスト
pytest --cov=app
シナリオCSV：data/scenarios.csv

アクションCSV：data/actions.csv

使用Python：3.8 以上

使用FW：Flask（Web版）

出力：テキスト／PDFレポート

📈 将来の展望
シナリオエディタ搭載（GUI/CSV編集）

チーム対応モード（複数役割で対応）

スマホUI対応

AI補助による最適アクション提案

Slack/Discord通知連携

🧩 応用・活用シーン
新人インフラ研修（想定外状況への訓練）

SRE選考試験・社内昇格評価

BCP演習（地震/火災後対応訓練）

提案用デモ（リスク管理可視化の提案）

🔧 非機能要件
区分	内容
パフォーマンス	CLI応答1秒以内 / Web表示2秒以内（同時接続10人想定）
セキュリティ	セッション管理 / 自動クリーンアップ（2h） / 保存なし
拡張性	UIとロジック分離 / CSV+プラグイン方式で柔軟追加可能

📂 ディレクトリ構成
bash
コピーする
編集する
infra-risk-simulator/
├── app/            # ロジック本体（状態/確率/レポート）
├── cli/            # CLI表示・操作
├── web/            # Web UI (Flask)
├── data/           # シナリオCSV・アクションCSV・ログ
├── tests/          # テストスクリプト
├── docs/           # 設計書、UI画像
├── requirements.txt
├── README.md
└── .gitignore
🧠 ブラックジャック理論の応用
ブラックジャック	本ツールでの対応
引く/止まる	アクションを実行 / 控える判断
バースト	SLA違反・システムダウン
点数を見て判断	状態スコア（CPU/MEM/ネットワーク等）
デッキ制限	ターン数上限・確率補正
勝ちパターンの見極め	安定復旧 vs 短期リスク回避の判断

このシミュレータは、現場スキルを元に開発された「即採用ポートフォリオ」にも活用できる技術教育・訓練ツールです。ゲーム感覚と業務実践を高次元で融合しています。
