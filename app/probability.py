import random

class ProbabilityEngine:
    @staticmethod
    def calculate_success_rate(action, system_state):
        """システム状態に基づく成功確率計算"""
        # 基本成功率 (0.0〜1.0)
        base_rate = action.get("base_success_rate", 0.7)

        # 状態による補正
        modifiers = []

        # CPUによる補正
        if action.get("category") == "システム操作" and system_state.cpu > 80:
            # CPU高負荷時はシステム操作系の成功率が下がる
            modifiers.append(0.7)
        elif action.get("category") == "システム操作" and system_state.cpu < 40:
            # CPU低負荷時はシステム操作系の成功率が上がる
            modifiers.append(1.2)

        # メモリによる補正
        if action.get("category") == "アプリケーション障害" and system_state.memory > 85:
            # メモリ圧迫時はアプリケーション関連の成功率が下がる
            modifiers.append(0.6)

        # ディスクによる補正
        if "ディスク" in action.get("name", "") and system_state.disk > 90:
            # ディスク関連操作はディスク使用率が高いと困難
            modifiers.append(0.5)

        # サービス状態による補正
        if system_state.services < 3:
            # サービスが多く停止している場合は復旧難易度上昇
            modifiers.append(0.8)

        # アラート数による補正
        if system_state.alerts > 7:
            # アラートが多すぎると判断ミスの可能性
            modifiers.append(0.85)

        # 修正子の適用
        final_rate = base_rate
        for modifier in modifiers:
            final_rate *= modifier

        # 最小・最大範囲の適用
        return max(0.1, min(0.99, final_rate))

    @staticmethod
    def roll_success(rate):
        """成功判定ロール
        rate: 成功確率 (0.0〜1.0)
        戻り値: 成功(True)または失敗(False)
        """
        return random.random() < rate

    @staticmethod
    def calculate_risk_expectation(action, system_state):
        """アクションのリスク期待値計算
        - 成功時の効果と失敗時の効果を加重平均
        - 期待値が高いほど理論上有利な選択肢
        """
        success_rate = ProbabilityEngine.calculate_success_rate(action, system_state)

        # 成功時の状態改善度
        success_value = 0

        # CPU改善
        if action.get("cpu_effect", 0) < 0:
            success_value += min(30, abs(action["cpu_effect"])) * 2

        # メモリ改善
        if action.get("memory_effect", 0) < 0:
            success_value += min(30, abs(action["memory_effect"])) * 1.5

        # ディスク改善
        if action.get("disk_effect", 0) < 0:
            success_value += min(30, abs(action["disk_effect"])) * 1

        # サービス復旧
        if action.get("service_effect", 0) > 0:
            success_value += action["service_effect"] * 50

        # アラート削減
        if action.get("alert_effect", 0) < 0:
            success_value += abs(action["alert_effect"]) * 10

        # SLAリスク軽減
        if action.get("sla_risk_effect", 0) < 0:
            success_value += abs(action["sla_risk_effect"]) * 3

        # 失敗時のペナルティ (デフォルト値として仮定)
        failure_penalty = 30

        # 特別なペナルティがある場合
        if "failure_effects" in action:
            failure = action["failure_effects"]
            if "cpu_effect" in failure and failure["cpu_effect"] > 0:
                failure_penalty += min(50, failure["cpu_effect"] * 2)
            if "service_effect" in failure and failure["service_effect"] < 0:
                failure_penalty += abs(failure["service_effect"]) * 50

        # 期待値の計算: (成功率 × 成功時価値) - (失敗率 × 失敗ペナルティ)
        expectation = (success_rate * success_value) - ((1 - success_rate) * failure_penalty)

        return expectation