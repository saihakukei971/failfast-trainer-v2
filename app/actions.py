import csv
import random

class ActionManager:
    def __init__(self, actions_file="data/actions.csv"):
        self.actions = []
        self.cooldowns = {}  # アクションID: 残りクールダウン
        self.load_actions(actions_file)

    def load_actions(self, file_path):
        """CSVファイルからアクションデータを読み込む"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 数値型の変換
                    for field in ['cpu_effect', 'memory_effect', 'disk_effect',
                                 'network_effect', 'service_effect', 'alert_effect',
                                 'base_success_rate', 'cooldown']:
                        if field in row and row[field]:
                            try:
                                if field == 'base_success_rate':
                                    row[field] = float(row[field])
                                else:
                                    row[field] = int(row[field])
                            except (ValueError, TypeError):
                                if field == 'base_success_rate':
                                    row[field] = 0.7
                                else:
                                    row[field] = 0

                    # 失敗時の影響はデフォルトは未設定
                    if 'failure_effects' not in row:
                        row['failure_effects'] = {}

                    self.actions.append(row)
        except Exception as e:
            print(f"アクションデータの読み込みに失敗しました: {e}")
            # デフォルトのアクションを追加
            self.actions = [{
                "id": "A001",
                "name": "サーバ再起動",
                "category": "システム操作",
                "description": "問題のあるサーバを再起動して初期状態に戻す",
                "cpu_effect": -30,
                "memory_effect": -25,
                "disk_effect": 0,
                "network_effect": 0,
                "service_effect": 0,
                "alert_effect": 0,
                "base_success_rate": 0.8,
                "cooldown": 2,
                "skill_tag": "運用/Linux"
            }, {
                "id": "A002",
                "name": "ログローテーション実行",
                "category": "メンテナンス",
                "description": "肥大化したログファイルの削除・圧縮を行う",
                "cpu_effect": 0,
                "memory_effect": 0,
                "disk_effect": -35,
                "network_effect": 0,
                "service_effect": 0,
                "alert_effect": 0,
                "base_success_rate": 0.95,
                "cooldown": 1,
                "skill_tag": "運用/ログ管理"
            }]

    def get_action_by_id(self, action_id):
        """IDによるアクションの取得"""
        for action in self.actions:
            if action['id'] == action_id:
                return action
        return None

    def get_available_actions(self, max_actions=5):
        """現在選択可能なアクションのリストを取得"""
        # クールダウン減少
        cooldown_keys = list(self.cooldowns.keys())
        for action_id in cooldown_keys:
            self.cooldowns[action_id] -= 1
            if self.cooldowns[action_id] <= 0:
                del self.cooldowns[action_id]

        # クールダウン中でないアクションのみ抽出
        available = [a for a in self.actions if a['id'] not in self.cooldowns]

        # ランダム選択（実際の実装では全て選べるようにするか、状況に応じて選びやすくする）
        if len(available) > max_actions:
            return random.sample(available, max_actions)
        return available

    def set_cooldown(self, action_id, cooldown_turns):
        """アクションをクールダウン状態に設定"""
        if cooldown_turns > 0:
            self.cooldowns[action_id] = cooldown_turns