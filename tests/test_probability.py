import pytest
import os
import sys
import math
import random

# テスト対象モジュールのインポート
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.probability import ProbabilityEngine
from app.state import SystemState

class TestProbabilityEngine:
    """ProbabilityEngineクラスのテスト"""

    @pytest.fixture
    def engine(self):
        """テスト用の確率計算エンジン"""
        return ProbabilityEngine()

    @pytest.fixture
    def default_state(self):
        """デフォルト状態のシステム"""
        state = SystemState()
        state.cpu = 50
        state.memory = 50
        state.disk = 50
        state.network = 50
        state.services = 5
        state.alerts = 0
        state.sla_risk = 10
        return state

    def test_calculate_success_rate_base(self, engine, default_state):
        """基本成功率計算テスト"""
        # 基本的なアクション
        action = {
            "id": "A001",
            "name": "Test Action",
            "category": "一般",
            "base_success_rate": 0.8
        }

        # 成功率計算
        rate = engine.calculate_success_rate(action, default_state)

        # 通常状態なら基本成功率のままのはず
        assert math.isclose(rate, 0.8, abs_tol=0.01)

    def test_calculate_success_rate_cpu_high(self, engine, default_state):
        """CPU高負荷時の成功率低下テスト"""
        # システム操作系アクション
        action = {
            "id": "A001",
            "name": "サーバ再起動",
            "category": "システム操作",
            "base_success_rate": 0.8
        }

        # 通常状態での成功率
        normal_rate = engine.calculate_success_rate(action, default_state)

        # CPU高負荷状態
        high_cpu_state = default_state
        high_cpu_state.cpu = 90

        # 高負荷時の成功率
        high_cpu_rate = engine.calculate_success_rate(action, high_cpu_state)

        # 高負荷時は成功率が下がるはず
        assert high_cpu_rate < normal_rate

    def test_calculate_success_rate_memory_high(self, engine, default_state):
        """メモリ高負荷時の成功率低下テスト"""
        # アプリケーション障害系アクション
        action = {
            "id": "A002",
            "name": "アプリケーション再起動",
            "category": "アプリケーション障害",
            "base_success_rate": 0.75
        }

        # 通常状態での成功率
        normal_rate = engine.calculate_success_rate(action, default_state)

        # メモリ高負荷状態
        high_memory_state = default_state
        high_memory_state.memory = 90

        # 高負荷時の成功率
        high_memory_rate = engine.calculate_success_rate(action, high_memory_state)

        # 高負荷時は成功率が下がるはず
        assert high_memory_rate < normal_rate

    def test_calculate_success_rate_disk_name(self, engine, default_state):
        """ディスク関連アクションの成功率テスト"""
        # ディスク操作系アクション（名前に「ディスク」が含まれる）
        action = {
            "id": "A003",
            "name": "ディスク容量確保",
            "category": "ストレージ",
            "base_success_rate": 0.9
        }

        # 通常状態での成功率
        normal_rate = engine.calculate_success_rate(action, default_state)

        # ディスク高使用率状態
        high_disk_state = default_state
        high_disk_state.disk = 95

        # 高使用率時の成功率
        high_disk_rate = engine.calculate_success_rate(action, high_disk_state)

        # 高使用率時は成功率が下がるはず
        assert high_disk_rate < normal_rate

    def test_calculate_success_rate_services_low(self, engine, default_state):
        """サービス停止多数時の成功率低下テスト"""
        # 一般アクション
        action = {
            "id": "A004",
            "name": "一般アクション",
            "category": "一般",
            "base_success_rate": 0.85
        }

        # 通常状態での成功率
        normal_rate = engine.calculate_success_rate(action, default_state)

        # サービス停止状態
        low_services_state = default_state
        low_services_state.services = 2

        # サービス停止多数時の成功率
        low_services_rate = engine.calculate_success_rate(action, low_services_state)

        # サービス停止多数時は成功率が下がるはず
        assert low_services_rate < normal_rate

    def test_calculate_success_rate_alerts_high(self, engine, default_state):
        """アラート多発時の成功率低下テスト"""
        # 一般アクション
        action = {
            "id": "A005",
            "name": "一般アクション",
            "category": "一般",
            "base_success_rate": 0.8
        }

        # 通常状態での成功率
        normal_rate = engine.calculate_success_rate(action, default_state)

        # アラート多発状態
        high_alerts_state = default_state
        high_alerts_state.alerts = 8

        # アラート多発時の成功率
        high_alerts_rate = engine.calculate_success_rate(action, high_alerts_state)

        # アラート多発時は成功率が下がるはず
        assert high_alerts_rate < normal_rate

    def test_calculate_success_rate_bounds(self, engine, default_state):
        """成功率の上下限テスト"""
        # 極端な基本成功率のアクション
        very_low_action = {
            "id": "A006",
            "name": "極低成功率アクション",
            "category": "一般",
            "base_success_rate": 0.05
        }

        very_high_action = {
            "id": "A007",
            "name": "極高成功率アクション",
            "category": "一般",
            "base_success_rate": 0.99
        }

        # 極端な状態
        extreme_state = default_state
        extreme_state.cpu = 95
        extreme_state.memory = 95
        extreme_state.disk = 95
        extreme_state.services = 1
        extreme_state.alerts = 10

        # 成功率計算
        low_rate = engine.calculate_success_rate(very_low_action, extreme_state)
        high_rate = engine.calculate_success_rate(very_high_action, default_state)

        # 下限は0.1、上限は0.99に収まるはず
        assert low_rate >= 0.1
        assert high_rate <= 0.99

    def test_roll_success(self, engine):
        """成功判定ロールテスト"""
        # random.randomをモック化してテスト結果を固定
        random.random = lambda: 0.5

        # 成功率0.6なら成功するはず
        assert engine.roll_success(0.6) == True

        # 成功率0.4なら失敗するはず
        assert engine.roll_success(0.4) == False

    def test_calculate_risk_expectation(self, engine, default_state):
        """リスク期待値計算テスト"""
        # CPU改善アクション
        cpu_action = {
            "id": "A008",
            "name": "CPU負荷軽減",
            "category": "システム操作",
            "base_success_rate": 0.8,
            "cpu_effect": -30,
            "memory_effect": 0
        }

        # メモリ改善アクション
        memory_action = {
            "id": "A009",
            "name": "メモリ解放",
            "category": "システム操作",
            "base_success_rate": 0.7,
            "cpu_effect": 0,
            "memory_effect": -25
        }

        # 成功確率計算をモック
        engine.calculate_success_rate = lambda action, state: action["base_success_rate"]

        # 期待値計算
        cpu_expectation = engine.calculate_risk_expectation(cpu_action, default_state)
        memory_expectation = engine.calculate_risk_expectation(memory_action, default_state)

        # CPU改善の方が期待値が高いはず（CPU効果が大きいため）
        assert cpu_expectation > memory_expectation

        # 両方とも正の期待値のはず（成功によるメリットが大きい）
        assert cpu_expectation > 0
        assert memory_expectation > 0

    def test_calculate_risk_expectation_service_restore(self, engine, default_state):
        """サービス復旧アクションの期待値テスト"""
        # サービス復旧アクション
        service_action = {
            "id": "A010",
            "name": "サービス復旧",
            "category": "復旧",
            "base_success_rate": 0.75,
            "service_effect": 1,
            "cpu_effect": 10
        }

        # CPU改善のみのアクション
        cpu_action = {
            "id": "A011",
            "name": "CPU改善のみ",
            "category": "システム操作",
            "base_success_rate": 0.8,
            "cpu_effect": -30
        }

        # 成功確率計算をモック
        engine.calculate_success_rate = lambda action, state: action["base_success_rate"]

        # 期待値計算
        service_expectation = engine.calculate_risk_expectation(service_action, default_state)
        cpu_expectation = engine.calculate_risk_expectation(cpu_action, default_state)

        # サービス復旧の方が期待値が高いはず（サービス復旧効果が重み付けされているため）
        assert service_expectation > cpu_expectation

    def test_calculate_risk_expectation_failure_penalty(self, engine, default_state):
        """失敗ペナルティを考慮した期待値テスト"""
        # 一般アクション
        normal_action = {
            "id": "A012",
            "name": "一般アクション",
            "category": "一般",
            "base_success_rate": 0.5,
            "cpu_effect": -20
        }

        # 失敗ペナルティが大きいアクション
        risky_action = {
            "id": "A013",
            "name": "危険なアクション",
            "category": "一般",
            "base_success_rate": 0.5,
            "cpu_effect": -40,
            "failure_effects": {
                "cpu_effect": 30,
                "service_effect": -1
            }
        }

        # 成功確率計算をモック
        engine.calculate_success_rate = lambda action, state: action["base_success_rate"]

        # 期待値計算
        normal_expectation = engine.calculate_risk_expectation(normal_action, default_state)
        risky_expectation = engine.calculate_risk_expectation(risky_action, default_state)

        # 失敗ペナルティが大きいアクションの方が期待値が低いはず
        assert normal_expectation > risky_expectation