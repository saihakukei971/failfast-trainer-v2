
import pytest
import os
import sys
import datetime
from unittest.mock import patch, MagicMock

# テスト対象モジュールのインポート
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.simulator import InfraRiskSimulator
from app.state import SystemState
from app.probability import ProbabilityEngine

class TestInfraRiskSimulator:
    """InfraRiskSimulatorクラスのテスト"""

    @pytest.fixture
    def simulator(self):
        """テスト用シミュレータインスタンス"""
        # テスト用の一時CSVファイルを使用
        return InfraRiskSimulator()

    def test_initialization(self, simulator):
        """初期化が正しく行われるかテスト"""
        assert simulator.turn == 0
        assert simulator.max_turns == 10
        assert simulator.game_over == False
        assert isinstance(simulator.system_state, SystemState)
        assert isinstance(simulator.probability_engine, ProbabilityEngine)

    def test_start_scenario_with_id(self, simulator):
        """特定IDのシナリオ開始テスト"""
        # モックシナリオの準備
        mock_scenario = {
            "id": "S001",
            "name": "Test Scenario",
            "initial_cpu": 70,
            "initial_memory": 60,
            "initial_disk": 50,
            "initial_network": 40,
            "initial_services": 5,
            "difficulty": "NORMAL"
        }

        # EventManagerのget_scenario_by_idをモック
        simulator.event_manager.get_scenario_by_id = MagicMock(return_value=mock_scenario)

        # シナリオ開始
        result = simulator.start_scenario("S001")

        # 検証
        assert result == mock_scenario
        assert simulator.system_state.cpu == 70
        assert simulator.system_state.memory == 60
        assert simulator.system_state.disk == 50
        assert simulator.system_state.network == 40
        assert simulator.system_state.services == 5
        assert simulator.turn == 0
        assert len(simulator.history) > 0  # 履歴にエントリが追加されていること

    def test_start_scenario_random(self, simulator):
        """ランダムシナリオ開始テスト"""
        # モックシナリオの準備
        mock_scenario = {
            "id": "S002",
            "name": "Random Scenario",
            "initial_cpu": 50,
            "initial_memory": 40,
            "initial_disk": 30,
            "initial_network": 20,
            "initial_services": 4,
            "difficulty": "HARD"
        }

        # EventManagerのget_random_scenarioをモック
        simulator.event_manager.get_random_scenario = MagicMock(return_value=mock_scenario)

        # シナリオ開始（ID指定なし）
        result = simulator.start_scenario()

        # 検証
        assert result == mock_scenario
        assert simulator.system_state.cpu == 50
        assert simulator.system_state.memory == 40
        assert simulator.system_state.disk == 30
        assert simulator.system_state.network == 20
        assert simulator.system_state.services == 4

    def test_next_turn(self, simulator):
        """次のターンへの進行テスト"""
        # 事前準備：シナリオ開始
        mock_scenario = {
            "id": "S001",
            "name": "Test Scenario",
            "initial_cpu": 50,
            "initial_memory": 50,
            "initial_disk": 50,
            "initial_network": 50,
            "initial_services": 5,
            "difficulty": "NORMAL"
        }
        simulator.event_manager.get_scenario_by_id = MagicMock(return_value=mock_scenario)
        simulator.start_scenario("S001")

        # モックイベントの準備
        mock_event = {
            "id": "E001",
            "name": "Test Event",
            "description": "Test event description",
            "cpu_effect": 10,
            "memory_effect": 5,
            "disk_effect": 0,
            "network_effect": 0,
            "service_effect": 0,
            "alert_effect": 1,
            "sla_risk_effect": 5
        }
        simulator.event_manager.get_random_event = MagicMock(return_value=mock_event)

        # 次のターンへ
        result = simulator.next_turn()

        # 検証
        assert simulator.turn == 1
        assert result["game_over"] == False
        assert result["event"] == mock_event
        assert "state" in result
        assert result["state"]["cpu"] == 60  # 50(初期値) + 10(イベント効果)
        assert result["state"]["memory"] == 55  # 50(初期値) + 5(イベント効果)

    def test_next_turn_game_over_by_max_turns(self, simulator):
        """最大ターン数でのゲーム終了テスト"""
        # 事前準備：シナリオ開始
        mock_scenario = {"id": "S001", "name": "Test", "initial_cpu": 50, "initial_memory": 50,
                        "initial_disk": 50, "initial_network": 50, "initial_services": 5}
        simulator.event_manager.get_scenario_by_id = MagicMock(return_value=mock_scenario)
        simulator.start_scenario("S001")

        # ターン数を最大値に設定
        simulator.turn = simulator.max_turns

        # 次のターンへ
        result = simulator.next_turn()

        # 検証
        assert result["game_over"] == True
        assert "message" in result

    def test_next_turn_game_over_by_critical_state(self, simulator):
        """危機的状態でのゲーム終了テスト"""
        # 事前準備：シナリオ開始
        mock_scenario = {"id": "S001", "name": "Test", "initial_cpu": 50, "initial_memory": 50,
                        "initial_disk": 50, "initial_network": 50, "initial_services": 5}
        simulator.event_manager.get_scenario_by_id = MagicMock(return_value=mock_scenario)
        simulator.start_scenario("S001")

        # 危機的状態を設定
        simulator.system_state.is_critical = MagicMock(return_value=True)

        # イベントの設定
        mock_event = {"id": "E001", "name": "Critical Event", "description": "Critical event"}
        simulator.event_manager.get_random_event = MagicMock(return_value=mock_event)

        # 次のターンへ
        result = simulator.next_turn()

        # 検証
        assert result["game_over"] == True
        assert simulator.game_over == True
        assert "message" in result

    def test_get_available_actions(self, simulator):
        """利用可能なアクションの取得テスト"""
        # モックアクションの準備
        mock_actions = [
            {"id": "A001", "name": "Action 1", "base_success_rate": 0.8},
            {"id": "A002", "name": "Action 2", "base_success_rate": 0.7}
        ]
        simulator.action_manager.get_available_actions = MagicMock(return_value=mock_actions)

        # 成功確率計算のモック
        simulator.probability_engine.calculate_success_rate = MagicMock(return_value=0.75)

        # 利用可能なアクション取得
        result = simulator.get_available_actions()

        # 検証
        assert len(result) == 2
        assert result[0]["id"] == "A001"
        assert result[1]["id"] == "A002"
        assert "calculated_success_rate" in result[0]
        assert result[0]["calculated_success_rate"] == 0.75

    def test_take_action_success(self, simulator):
        """アクション実行成功のテスト"""
        # 事前準備：シナリオ開始
        mock_scenario = {"id": "S001", "name": "Test", "initial_cpu": 50, "initial_memory": 50,
                        "initial_disk": 50, "initial_network": 50, "initial_services": 5}
        simulator.event_manager.get_scenario_by_id = MagicMock(return_value=mock_scenario)
        simulator.start_scenario("S001")

        # モックアクションの準備
        mock_action = {
            "id": "A001",
            "name": "Test Action",
            "cpu_effect": -20,
            "memory_effect": -10,
            "cooldown": 2
        }
        simulator.action_manager.get_action_by_id = MagicMock(return_value=mock_action)

        # 成功確率と判定のモック
        simulator.probability_engine.calculate_success_rate = MagicMock(return_value=0.8)
        simulator.probability_engine.roll_success = MagicMock(return_value=True)

        # 状態変化のモック
        state_changes = {"cpu": -20, "memory": -10}
        simulator.system_state.apply_action = MagicMock(return_value=state_changes)
        simulator.system_state.is_critical = MagicMock(return_value=False)

        # アクション実行
        result = simulator.take_action("A001")

        # 検証
        assert result["success"] == True
        assert "message" in result
        assert result["state_changes"] == state_changes
        assert "state" in result
        assert result["game_over"] == False

    def test_take_action_failure(self, simulator):
        """アクション実行失敗のテスト"""
        # 事前準備：シナリオ開始
        mock_scenario = {"id": "S001", "name": "Test", "initial_cpu": 50, "initial_memory": 50,
                        "initial_disk": 50, "initial_network": 50, "initial_services": 5}
        simulator.event_manager.get_scenario_by_id = MagicMock(return_value=mock_scenario)
        simulator.start_scenario("S001")

        # モックアクションの準備
        mock_action = {
            "id": "A001",
            "name": "Test Action",
            "cpu_effect": -20,
            "memory_effect": -10,
            "cooldown": 2
        }
        simulator.action_manager.get_action_by_id = MagicMock(return_value=mock_action)

        # 成功確率と判定のモック（失敗）
        simulator.probability_engine.calculate_success_rate = MagicMock(return_value=0.8)
        simulator.probability_engine.roll_success = MagicMock(return_value=False)

        # 状態変化のモック
        state_changes = {"sla_risk": 15, "alerts": 1}
        simulator.system_state.apply_action = MagicMock(return_value=state_changes)
        simulator.system_state.is_critical = MagicMock(return_value=False)

        # アクション実行
        result = simulator.take_action("A001")

        # 検証
        assert result["success"] == False
        assert "message" in result
        assert result["state_changes"] == state_changes
        assert "state" in result
        assert result["game_over"] == False

    def test_take_action_critical(self, simulator):
        """アクション実行後に危機的状態になるテスト"""
        # 事前準備：シナリオ開始
        mock_scenario = {"id": "S001", "name": "Test", "initial_cpu": 50, "initial_memory": 50,
                        "initial_disk": 50, "initial_network": 50, "initial_services": 5}
        simulator.event_manager.get_scenario_by_id = MagicMock(return_value=mock_scenario)
        simulator.start_scenario("S001")

        # モックアクションの準備
        mock_action = {"id": "A001", "name": "Critical Action"}
        simulator.action_manager.get_action_by_id = MagicMock(return_value=mock_action)

        # 成功確率と判定のモック
        simulator.probability_engine.calculate_success_rate = MagicMock(return_value=0.5)
        simulator.probability_engine.roll_success = MagicMock(return_value=True)

        # 状態変化のモック（危機的状態に）
        state_changes = {"cpu": 50}  # CPU 100%に
        simulator.system_state.apply_action = MagicMock(return_value=state_changes)
        simulator.system_state.is_critical = MagicMock(return_value=True)

        # アクション実行
        result = simulator.take_action("A001")

        # 検証
        assert "state_changes" in result
        assert result["game_over"] == True
        assert simulator.game_over == True
        assert "critical_message" in result

    def test_calculate_score(self, simulator):
        """スコア計算テスト"""
        # システム状態を設定
        simulator.system_state.services = 4
        simulator.system_state.cpu = 50
        simulator.system_state.memory = 50
        simulator.system_state.sla_risk = 20
        simulator.turn = 5

        # スコア計算
        score = simulator.calculate_score()

        # 検証: 4*100 (基本スコア) + 50 (安定性ボーナス) + (10-5)*30 (速度ボーナス) - 20*5 (SLAペナルティ)
        expected_score = 400 + 50 + 150 - 100
        assert score == expected_score

    def test_log_event(self, simulator):
        """イベントログ記録テスト"""
        # 初期履歴数
        initial_history_count = len(simulator.history)

        # テスト用イベントデータ
        event_data = {
            "type": "test_event",
            "test_field": "test_value"
        }

        # ログ記録
        simulator.log_event(event_data)

        # 検証
        assert len(simulator.history) == initial_history_count + 1
        assert simulator.history[-1]["type"] == "test_event"
        assert simulator.history[-1]["test_field"] == "test_value"
        assert "timestamp" in simulator.history[-1]

    def test_get_game_summary(self, simulator):
        """ゲームサマリー取得テスト"""
        # 事前準備：シナリオ開始
        mock_scenario = {"id": "S001", "name": "Test Summary", "initial_cpu": 60, "initial_memory": 70,
                        "initial_disk": 40, "initial_network": 30, "initial_services": 5}
        simulator.event_manager.get_scenario_by_id = MagicMock(return_value=mock_scenario)
        simulator.start_scenario("S001")

        # ターン数とスコアをモック
        simulator.turn = 3
        simulator.calculate_score = MagicMock(return_value=450)

        # サマリー取得
        summary = simulator.get_game_summary()

        # 検証
        assert summary["scenario"] == mock_scenario
        assert summary["turn_count"] == 3
        assert summary["score"] == 450
        assert summary["game_over"] == False
        assert "final_state" in summary