import random
import csv
import json
import datetime
from app.state import SystemState
from app.probability import ProbabilityEngine
from app.events import EventManager
from app.actions import ActionManager

class InfraRiskSimulator:
    def __init__(self, scenarios_file="data/scenarios.csv", actions_file="data/actions.csv"):
        self.system_state = SystemState()
        self.event_manager = EventManager(scenarios_file)
        self.action_manager = ActionManager(actions_file)
        self.probability_engine = ProbabilityEngine()
        self.turn = 0
        self.max_turns = 10
        self.history = []
        self.current_scenario = None
        self.current_event = None
        self.game_over = False
        self.score = 0
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def start_scenario(self, scenario_id=None):
        """シナリオを開始し、初期状態を設定"""
        if scenario_id:
            self.current_scenario = self.event_manager.get_scenario_by_id(scenario_id)
        else:
            self.current_scenario = self.event_manager.get_random_scenario()

        # 初期状態の設定
        self.system_state.cpu = self.current_scenario["initial_cpu"]
        self.system_state.memory = self.current_scenario["initial_memory"]
        self.system_state.disk = self.current_scenario["initial_disk"]
        self.system_state.network = self.current_scenario["initial_network"]
        self.system_state.services = self.current_scenario["initial_services"]
        self.system_state.alerts = 0
        self.system_state.sla_risk = 10

        # 履歴初期化
        self.turn = 0
        self.history = []
        self.game_over = False

        # 初期イベントの発生
        self.log_event({
            "type": "scenario_start",
            "scenario_id": self.current_scenario["id"],
            "scenario_name": self.current_scenario["name"],
            "description": self.current_scenario["description"]
        })

        return self.current_scenario

    def next_turn(self):
        """次のターンに進み、イベントを発生させる"""
        if self.game_over:
            return {"game_over": True, "message": "ゲームは既に終了しています"}

        self.turn += 1

        # 最大ターン数チェック
        if self.turn > self.max_turns:
            self.game_over = True
            return {"game_over": True, "message": "最大ターン数に達しました"}

        # システム状態の自然変化（ターン経過による変化）
        self.system_state.natural_progression()

        # ランダムイベントの発生
        self.current_event = self.event_manager.get_random_event()
        event_effect = self.system_state.apply_event(self.current_event)

        # 危機的状態のチェック
        if self.system_state.is_critical():
            self.game_over = True
            self.log_event({
                "type": "critical_state",
                "turn": self.turn,
                "state": self.system_state.get_state_dict()
            })
            return {
                "game_over": True,
                "message": "システムが危機的状態になりました",
                "event": self.current_event,
                "state": self.system_state.get_state_dict()
            }

        # イベントのログ記録
        self.log_event({
            "type": "event",
            "turn": self.turn,
            "event_id": self.current_event["id"],
            "event_name": self.current_event["name"],
            "description": self.current_event["description"],
            "effect": event_effect
        })

        return {
            "game_over": False,
            "turn": self.turn,
            "event": self.current_event,
            "state": self.system_state.get_state_dict()
        }

    def get_available_actions(self):
        """現在選択可能なアクションのリストを取得"""
        available_actions = self.action_manager.get_available_actions()

        # 各アクションの成功確率を計算
        for action in available_actions:
            success_rate = self.probability_engine.calculate_success_rate(
                action, self.system_state
            )
            action["calculated_success_rate"] = success_rate

        return available_actions

    def take_action(self, action_id):
        """指定されたアクションを実行し、結果を返す"""
        if self.game_over:
            return {"success": False, "message": "ゲームは既に終了しています"}

        action = self.action_manager.get_action_by_id(action_id)
        if not action:
            return {"success": False, "message": "指定されたアクションが見つかりません"}

        # 成功確率の計算と成功判定
        success_rate = self.probability_engine.calculate_success_rate(
            action, self.system_state
        )
        is_success = self.probability_engine.roll_success(success_rate)

        # アクションの結果をシステム状態に適用
        state_changes = self.system_state.apply_action(action, is_success)

        # アクションをクールダウン状態に
        self.action_manager.set_cooldown(action_id, action.get("cooldown", 0))

        # 危機的状態のチェック
        critical = self.system_state.is_critical()
        if critical:
            self.game_over = True

        # アクションのログ記録
        self.log_event({
            "type": "action",
            "turn": self.turn,
            "action_id": action["id"],
            "action_name": action["name"],
            "success": is_success,
            "success_rate": success_rate,
            "state_changes": state_changes,
            "state_after": self.system_state.get_state_dict()
        })

        return {
            "success": is_success,
            "message": f"アクション '{action['name']}' を実行しました: {'成功' if is_success else '失敗'}",
            "state_changes": state_changes,
            "state": self.system_state.get_state_dict(),
            "game_over": critical,
            "critical_message": "システムが危機的状態になりました" if critical else None
        }

    def calculate_score(self):
        """現在のスコアを計算"""
        # 基本スコア: サービス稼働数 x 100
        base_score = self.system_state.services * 100

        # 安定性ボーナス: 低負荷維持でボーナス
        stability_bonus = 0
        if self.system_state.cpu < 60 and self.system_state.memory < 60:
            stability_bonus = 50

        # 対応速度ボーナス: ターン数が少ないほど高得点
        speed_bonus = max(0, (10 - self.turn) * 30)

        # SLAリスクによるペナルティ
        sla_penalty = self.system_state.sla_risk * 5

        self.score = base_score + stability_bonus + speed_bonus - sla_penalty
        return self.score

    def log_event(self, event_data):
        """イベントをログに記録"""
        event_data["timestamp"] = datetime.datetime.now().isoformat()
        self.history.append(event_data)

        # ログファイルに書き込み
        log_file = f"data/logs/{self.session_id}.json"
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(event_data) + "\n")
        except Exception as e:
            print(f"ログの書き込みに失敗しました: {e}")

    def get_game_summary(self):
        """ゲームの要約を取得"""
        return {
            "scenario": self.current_scenario,
            "turn_count": self.turn,
            "final_state": self.system_state.get_state_dict(),
            "score": self.calculate_score(),
            "game_over": self.game_over
        }