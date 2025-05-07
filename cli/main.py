#!/usr/bin/env python3
import sys
import os
import argparse
import time

# パスの調整（実行ディレクトリに関わらず動作するように）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.simulator import InfraRiskSimulator
from app.report import ReportGenerator
from cli.display import CliDisplay

def parse_args():
    parser = argparse.ArgumentParser(description='インフラリスク管理シミュレータ')
    parser.add_argument('--scenario', type=str, help='使用するシナリオID')
    parser.add_argument('--actions-file', type=str, default='data/actions.csv', help='アクションデータファイル')
    parser.add_argument('--scenarios-file', type=str, default='data/scenarios.csv', help='シナリオデータファイル')
    return parser.parse_args()

def main():
    args = parse_args()

    # シミュレータの初期化
    simulator = InfraRiskSimulator(
        scenarios_file=args.scenarios_file,
        actions_file=args.actions_file
    )

    # CLIディスプレイの初期化
    display = CliDisplay()

    # タイトル表示
    display.show_title()

    # シナリオの選択
    if args.scenario:
        scenario = simulator.start_scenario(args.scenario)
    else:
        available_scenarios = simulator.event_manager.scenarios
        selected_index = display.select_scenario(available_scenarios)
        scenario = simulator.start_scenario(available_scenarios[selected_index]["id"])

    # シナリオ情報表示
    display.show_scenario_info(scenario)
    display.wait_for_key()

    # ゲームループ
    while not simulator.game_over and simulator.turn < simulator.max_turns:
        # 次のターンへ
        turn_result = simulator.next_turn()
        if turn_result["game_over"]:
            display.show_message(turn_result["message"])
            break

        # 状態表示
        display.show_state(turn_result["state"], simulator.turn, simulator.max_turns)
        display.show_event(turn_result["event"])

        # アクション選択
        available_actions = simulator.get_available_actions()
        selected_index = display.select_action(available_actions)

        # キャンセル処理
        if selected_index < 0:
            if display.confirm("シミュレーションを終了しますか？"):
                break
            continue

        # アクション実行
        action_result = simulator.take_action(available_actions[selected_index]["id"])
        display.show_action_result(action_result)

        if action_result["game_over"]:
            display.show_message(action_result["critical_message"])
            display.wait_for_key()
            break

        # 次のターンへの一時停止
        display.wait_for_key()

    # ゲーム終了表示
    display.show_game_over(simulator.calculate_score())

    # レポート生成
    report_generator = ReportGenerator(simulator)

    # テキストレポート表示
    display.show_message("\n===== 対応レポート =====")
    text_report = report_generator.generate_text_report()
    print(text_report)

    # PDFレポートの生成確認
    if display.confirm("対応レポートをPDFで保存しますか？"):
        pdf_path = report_generator.generate_pdf()
        if pdf_path:
            display.show_message(f"PDFレポートを保存しました: {pdf_path}")

    display.show_message("シミュレーションを終了します。お疲れ様でした！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nシミュレータを終了します。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")