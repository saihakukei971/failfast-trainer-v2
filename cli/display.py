import os
import sys
import time

class CliDisplay:
    def __init__(self):
        self.width = 80
        self.bar_width = 50

    def clear_screen(self):
        """画面をクリア"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_title(self):
        """タイトル表示"""
        self.clear_screen()
        title = "インフラリスク管理シミュレータ"
        print("=" * self.width)
        print(title.center(self.width))
        print("=" * self.width)
        print("インフラエンジニアのための障害対応トレーニングツール\n")

    def select_scenario(self, scenarios):
        """シナリオ選択画面"""
        print("シナリオを選択してください:")
        for i, scenario in enumerate(scenarios):
            print(f"{i+1}. {scenario['name']} ({scenario['difficulty']}) - {scenario['description']}")

        while True:
            try:
                choice = int(input("\n選択 (番号): ")) - 1
                if 0 <= choice < len(scenarios):
                    return choice
                else:
                    print("有効な番号を入力してください")
            except ValueError:
                print("数字を入力してください")

    def show_scenario_info(self, scenario):
        """シナリオ情報表示"""
        self.clear_screen()
        print("=" * self.width)
        print(f"シナリオ: {scenario['name']}".center(self.width))
        print("=" * self.width)
        print(f"\n{scenario['description']}\n")
        print(f"難易度: {scenario['difficulty']}")
        print(f"カテゴリ: {scenario['category']}")
        print("\n初期システム状態:")
        print(f"CPU使用率: {scenario['initial_cpu']}%")
        print(f"メモリ使用率: {scenario['initial_memory']}%")
        print(f"ディスク使用率: {scenario['initial_disk']}%")
        print(f"ネットワーク負荷: {scenario['initial_network']}%")
        print(f"稼働サービス数: {scenario['initial_services']}")
        print("\nEnterキーを押すとシミュレーションを開始します...")

    def wait_for_key(self):
        """キー入力待ち"""
        input("\nEnterキーを押して続行...")

    def show_progress_bar(self, value, max_value=100, width=None):
        """プログレスバー表示"""
        if width is None:
            width = self.bar_width

        filled_width = int(width * value / max_value)
        bar = '█' * filled_width + '░' * (width - filled_width)
        return bar

    def show_state(self, state, turn, max_turns):
        """システム状態表示"""
        self.clear_screen()

        print("=" * self.width)
        print(f"インフラリスク管理シミュレータ [ターン: {turn}/{max_turns}]".center(self.width))
        print("=" * self.width)

        print("\n📊 システム状態:")
        print(f" - CPU使用率: {self.show_progress_bar(state['cpu'])} {state['cpu']}%")
        print(f" - メモリ使用率: {self.show_progress_bar(state['memory'])} {state['memory']}%")
        print(f" - ディスク使用率: {self.show_progress_bar(state['disk'])} {state['disk']}%")
        print(f" - ネットワーク負荷: {self.show_progress_bar(state['network'])} {state['network']}%")
        print(f" - 稼働サービス: {state['services']}/5 ({5-state['services']}サービスダウン中)")
        print(f" - アラート数: {state['alerts']}件")
        print(f" - SLAリスク: {self.show_progress_bar(state['sla_risk'])} {state['sla_risk']}%")

    def show_event(self, event):
        """イベント表示"""
        print("\n⚠️ イベント発生:")
        print(f"「{event['description']}」")

    def select_action(self, actions):
        """アクション選択画面"""
        print("\n対応を選択してください:")

        for i, action in enumerate(actions):
            success_rate = action.get("calculated_success_rate", 0.5) * 100
            print(f"{i+1}. {action['name']} (成功率: {success_rate:.0f}%)")
            print(f"   {action['description']}")

        print("0. キャンセル")

        while True:
            try:
                choice = int(input("\n選択 (番号): "))
                if choice == 0:
                    return -1
                if 1 <= choice <= len(actions):
                    return choice - 1
                else:
                    print("有効な番号を入力してください")
            except ValueError:
                print("数字を入力してください")

    def show_action_result(self, result):
        """アクション結果表示"""
        if result["success"]:
            print(f"\n✅ {result['message']}")
        else:
            print(f"\n❌ {result['message']}")

        # 状態変化の表示
        if "state_changes" in result and result["state_changes"]:
            print("\n状態変化:")
            for key, value in result["state_changes"].items():
                if value != 0:
                    change_str = f"+{value}" if value > 0 else f"{value}"
                    print(f" - {key}: {change_str}")

    def show_message(self, message):
        """メッセージ表示"""
        print(f"\n{message}")

    def show_game_over(self, score):
        """ゲーム終了表示"""
        print("\n" + "=" * self.width)
        print("シミュレーション終了".center(self.width))
        print("=" * self.width)
        print(f"\n最終スコア: {score}点")

        # スコアに応じた評価
        if score < 300:
            print("評価: C (改善の余地あり)")
        elif score < 500:
            print("評価: B (標準的な対応)")
        elif score < 700:
            print("評価: A (優れた対応)")
        else:
            print("評価: S (卓越した対応)")

    def confirm(self, message):
        """確認ダイアログ"""
        while True:
            choice = input(f"\n{message} (y/n): ").lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            print("y または n で答えてください")