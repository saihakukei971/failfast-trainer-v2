class SystemState:
    def __init__(self):
        # 基本状態
        self.cpu = 50        # CPU使用率 (%)
        self.memory = 50     # メモリ使用率 (%)
        self.disk = 50       # ディスク使用率 (%)
        self.network = 50    # ネットワーク負荷 (%)
        self.services = 5    # 稼働サービス数
        self.alerts = 0      # アラート数
        self.sla_risk = 0    # SLA違反リスク (0-100)

    def get_state_dict(self):
        """状態を辞書形式で取得"""
        return {
            "cpu": self.cpu,
            "memory": self.memory,
            "disk": self.disk,
            "network": self.network,
            "services": self.services,
            "alerts": self.alerts,
            "sla_risk": self.sla_risk
        }

    def is_critical(self):
        """システムが危機的状態かどうか判定"""
        if self.cpu >= 95 or self.memory >= 95 or self.disk >= 98:
            return True
        if self.services <= 1:  # ほとんどのサービスがダウン
            return True
        if self.sla_risk >= 90:  # SLA違反確実
            return True
        return False

    def natural_progression(self):
        """時間経過による自然な状態変化"""
        # 時間経過でSLAリスクは上昇する傾向
        self.sla_risk = min(100, self.sla_risk + 5)

        # 負荷の高いリソースはさらに悪化する傾向
        if self.cpu > 80:
            self.cpu = min(100, self.cpu + 3)
        if self.memory > 80:
            self.memory = min(100, self.memory + 2)
        if self.disk > 90:
            self.disk = min(100, self.disk + 1)

        # アラートは徐々に増加する傾向
        if self.cpu > 80 or self.memory > 80 or self.disk > 80:
            self.alerts = min(10, self.alerts + 1)

    def apply_event(self, event):
        """イベントの影響をシステム状態に適用"""
        changes = {}

        # CPUへの影響
        if "cpu_effect" in event:
            old_cpu = self.cpu
            self.cpu = max(0, min(100, self.cpu + event["cpu_effect"]))
            changes["cpu"] = self.cpu - old_cpu

        # メモリへの影響
        if "memory_effect" in event:
            old_memory = self.memory
            self.memory = max(0, min(100, self.memory + event["memory_effect"]))
            changes["memory"] = self.memory - old_memory

        # ディスクへの影響
        if "disk_effect" in event:
            old_disk = self.disk
            self.disk = max(0, min(100, self.disk + event["disk_effect"]))
            changes["disk"] = self.disk - old_disk

        # ネットワークへの影響
        if "network_effect" in event:
            old_network = self.network
            self.network = max(0, min(100, self.network + event["network_effect"]))
            changes["network"] = self.network - old_network

        # サービス数への影響
        if "service_effect" in event:
            old_services = self.services
            self.services = max(0, self.services + event["service_effect"])
            changes["services"] = self.services - old_services

        # アラート数への影響
        if "alert_effect" in event:
            old_alerts = self.alerts
            self.alerts = max(0, self.alerts + event["alert_effect"])
            changes["alerts"] = self.alerts - old_alerts

        # SLAリスクへの影響
        if "sla_risk_effect" in event:
            old_sla_risk = self.sla_risk
            self.sla_risk = max(0, min(100, self.sla_risk + event["sla_risk_effect"]))
            changes["sla_risk"] = self.sla_risk - old_sla_risk

        return changes

    def apply_action(self, action, success=True):
        """アクションの結果をシステム状態に適用"""
        changes = {}

        if success:
            # 成功時の影響を適用
            if "cpu_effect" in action:
                old_cpu = self.cpu
                self.cpu = max(0, min(100, self.cpu + action["cpu_effect"]))
                changes["cpu"] = self.cpu - old_cpu

            if "memory_effect" in action:
                old_memory = self.memory
                self.memory = max(0, min(100, self.memory + action["memory_effect"]))
                changes["memory"] = self.memory - old_memory

            if "disk_effect" in action:
                old_disk = self.disk
                self.disk = max(0, min(100, self.disk + action["disk_effect"]))
                changes["disk"] = self.disk - old_disk

            if "network_effect" in action:
                old_network = self.network
                self.network = max(0, min(100, self.network + action["network_effect"]))
                changes["network"] = self.network - old_network

            if "service_effect" in action:
                old_services = self.services
                self.services = max(0, self.services + action["service_effect"])
                changes["services"] = self.services - old_services

            if "alert_effect" in action:
                old_alerts = self.alerts
                self.alerts = max(0, self.alerts + action["alert_effect"])
                changes["alerts"] = self.alerts - old_alerts

            if "sla_risk_effect" in action:
                old_sla_risk = self.sla_risk
                self.sla_risk = max(0, min(100, self.sla_risk + action["sla_risk_effect"]))
                changes["sla_risk"] = self.sla_risk - old_sla_risk
        else:
            # 失敗時の影響を適用
            # 失敗時はSLAリスクと負荷が増加する
            old_sla_risk = self.sla_risk
            self.sla_risk = min(100, self.sla_risk + 15)
            changes["sla_risk"] = self.sla_risk - old_sla_risk

            # 特定のアクションに失敗すると状態が悪化する場合
            if "failure_effects" in action:
                failure = action["failure_effects"]

                if "cpu_effect" in failure:
                    old_cpu = self.cpu
                    self.cpu = max(0, min(100, self.cpu + failure["cpu_effect"]))
                    changes["cpu"] = self.cpu - old_cpu

                if "memory_effect" in failure:
                    old_memory = self.memory
                    self.memory = max(0, min(100, self.memory + failure["memory_effect"]))
                    changes["memory"] = self.memory - old_memory

                if "service_effect" in failure:
                    old_services = self.services
                    self.services = max(0, self.services + failure["service_effect"])
                    changes["services"] = self.services - old_services
            else:
                # デフォルトの失敗影響
                if "cpu_effect" in action and action["cpu_effect"] < 0:
                    # CPU負荷を軽減するアクションの失敗は、逆に負荷を増大させる可能性
                    old_cpu = self.cpu
                    self.cpu = min(100, self.cpu + 10)
                    changes["cpu"] = self.cpu - old_cpu

                # アラート増加
                old_alerts = self.alerts
                self.alerts = min(10, self.alerts + 1)
                changes["alerts"] = self.alerts - old_alerts

        return changes