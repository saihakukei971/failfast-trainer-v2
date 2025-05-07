import csv
import random

class EventManager:
    def __init__(self, scenarios_file="data/scenarios.csv"):
        self.scenarios = []
        self.events = []
        self.load_scenarios(scenarios_file)

    def load_scenarios(self, file_path):
        """CSVファイルからシナリオデータを読み込む"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 数値型の変換
                    for field in ['initial_cpu', 'initial_memory', 'initial_disk',
                                 'initial_network', 'initial_services']:
                        if field in row:
                            row[field] = int(row[field])

                    # シナリオとイベントを分ける
                    if row.get('id', '').startswith('S'):
                        self.scenarios.append(row)
                    else:
                        self.events.append(row)
        except Exception as e:
            print(f"シナリオデータの読み込みに失敗しました: {e}")
            # デフォルトのシナリオを追加
            self.scenarios = [{
                "id": "S001",
                "name": "Webサーバ過負荷",
                "category": "アプリケーション障害",
                "description": "大規模キャンペーンによるアクセス集中でWebサーバがCPU高負荷状態",
                "initial_cpu": 85,
                "initial_memory": 60,
                "initial_disk": 50,
                "initial_network": 75,
                "initial_services": 5,
                "difficulty": "NORMAL"
            }]
            self.events = [{
                "id": "E001",
                "name": "メモリリーク検知",
                "category": "アプリケーション障害",
                "description": "Javaアプリケーションでメモリリークが検知されました。",
                "cpu_effect": 5,
                "memory_effect": 20,
                "disk_effect": 0,
                "network_effect": 0,
                "service_effect": 0,
                "alert_effect": 2,
                "sla_risk_effect": 10
            }]

    def get_scenario_by_id(self, scenario_id):
        """IDによるシナリオの取得"""
        for scenario in self.scenarios:
            if scenario['id'] == scenario_id:
                return scenario
        return None

    def get_random_scenario(self):
        """ランダムなシナリオを取得"""
        if not self.scenarios:
            return {
                "id": "S000",
                "name": "Default Scenario",
                "category": "Default",
                "description": "Default scenario due to loading failure",
                "initial_cpu": 50,
                "initial_memory": 50,
                "initial_disk": 50,
                "initial_network": 50,
                "initial_services": 5,
                "difficulty": "NORMAL"
            }
        return random.choice(self.scenarios)

    def get_random_event(self):
        """ランダムなイベントを取得"""
        if not self.events:
            # イベントがない場合、デフォルトイベントを返す
            return {
                "id": "E000",
                "name": "Default Event",
                "category": "Default",
                "description": "Default event due to loading failure",
                "cpu_effect": 10,
                "memory_effect": 10,
                "disk_effect": 0,
                "network_effect": 0,
                "service_effect": 0,
                "alert_effect": 1,
                "sla_risk_effect": 5
            }

        # 実際のイベントからランダム選択
        event = random.choice(self.events)

        # 数値型の変換
        for field in ['cpu_effect', 'memory_effect', 'disk_effect',
                     'network_effect', 'service_effect', 'alert_effect',
                     'sla_risk_effect']:
            if field in event and event[field]:
                try:
                    event[field] = int(event[field])
                except (ValueError, TypeError):
                    event[field] = 0

        return event