import json
import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

class ReportGenerator:
    def __init__(self, simulator):
        self.simulator = simulator

    def generate_summary(self):
        """プレイログからサマリーを生成"""
        summary = {
            "scenario": self.simulator.current_scenario["name"],
            "scenario_description": self.simulator.current_scenario["description"],
            "turns_played": self.simulator.turn,
            "final_state": self.simulator.system_state.get_state_dict(),
            "score": self.simulator.calculate_score(),
            "game_over_reason": "完了" if not self.simulator.game_over else "システムクリティカル",
            "actions_taken": []
        }

        # アクション履歴の抽出
        for event in self.simulator.history:
            if event.get("type") == "action":
                summary["actions_taken"].append({
                    "turn": event["turn"],
                    "action": event["action_name"],
                    "success": event["success"]
                })

        return summary

    def generate_text_report(self, filename=None):
        """テキスト形式のレポート生成"""
        summary = self.generate_summary()

        report_lines = [
            "===== インフラリスク管理シミュレータ - 対応レポート =====",
            f"日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"シナリオ: {summary['scenario']}",
            f"説明: {summary['scenario_description']}",
            f"プレイターン数: {summary['turns_played']}",
            f"最終スコア: {summary['score']}",
            f"結果: {summary['game_over_reason']}",
            "",
            "--- 最終システム状態 ---",
            f"CPU使用率: {summary['final_state']['cpu']}%",
            f"メモリ使用率: {summary['final_state']['memory']}%",
            f"ディスク使用率: {summary['final_state']['disk']}%",
            f"ネットワーク負荷: {summary['final_state']['network']}%",
            f"稼働サービス数: {summary['final_state']['services']}",
            f"アラート数: {summary['final_state']['alerts']}",
            f"SLAリスク値: {summary['final_state']['sla_risk']}%",
            "",
            "--- 対応アクション履歴 ---"
        ]

        for action in summary["actions_taken"]:
            result = "成功" if action["success"] else "失敗"
            report_lines.append(f"ターン {action['turn']}: {action['action']} - {result}")

        report_lines.append("")
        report_lines.append("--- 分析と改善提案 ---")

        # 分析と改善提案の生成
        improvement_tips = self.generate_improvement_tips(summary)
        for tip in improvement_tips:
            report_lines.append(f"・{tip}")

        report_text = "\n".join(report_lines)

        # ファイルに保存
        if filename:
            os.makedirs("data/reports", exist_ok=True)
            with open(f"data/reports/{filename}.txt", "w", encoding="utf-8") as f:
                f.write(report_text)

        return report_text

    def generate_pdf(self, filename=None):
        """PDF形式のレポート生成"""
        if not filename:
            filename = f"infra_report_{self.simulator.session_id}"

        os.makedirs("data/reports", exist_ok=True)
        pdf_path = f"data/reports/{filename}.pdf"

        summary = self.generate_summary()
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()

        # カスタムスタイル
        styles.add(ParagraphStyle(
            name='Title',
            fontName='Helvetica-Bold',
            fontSize=14,
            alignment=1,
            spaceAfter=10
        ))

        story = []

        # タイトル
        story.append(Paragraph("インフラリスク管理シミュレータ - 対応レポート", styles['Title']))
        story.append(Spacer(1, 12))

        # 基本情報
        story.append(Paragraph(f"日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"シナリオ: {summary['scenario']}", styles['Normal']))
        story.append(Paragraph(f"説明: {summary['scenario_description']}", styles['Normal']))
        story.append(Paragraph(f"プレイターン数: {summary['turns_played']}", styles['Normal']))
        story.append(Paragraph(f"最終スコア: {summary['score']}", styles['Normal']))
        story.append(Paragraph(f"結果: {summary['game_over_reason']}", styles['Normal']))
        story.append(Spacer(1, 12))

        # 最終システム状態
        story.append(Paragraph("最終システム状態", styles['Heading2']))
        state_data = [
            ["項目", "値"],
            ["CPU使用率", f"{summary['final_state']['cpu']}%"],
            ["メモリ使用率", f"{summary['final_state']['memory']}%"],
            ["ディスク使用率", f"{summary['final_state']['disk']}%"],
            ["ネットワーク負荷", f"{summary['final_state']['network']}%"],
            ["稼働サービス数", f"{summary['final_state']['services']}"],
            ["アラート数", f"{summary['final_state']['alerts']}"],
            ["SLAリスク値", f"{summary['final_state']['sla_risk']}%"]
        ]
        state_table = Table(state_data, colWidths=[200, 100])
        state_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(state_table)
        story.append(Spacer(1, 12))

        # 対応アクション履歴
        story.append(Paragraph("対応アクション履歴", styles['Heading2']))

        if summary["actions_taken"]:
            action_data = [["ターン", "アクション", "結果"]]
            for action in summary["actions_taken"]:
                result = "成功" if action["success"] else "失敗"
                action_data.append([str(action["turn"]), action["action"], result])

            action_table = Table(action_data, colWidths=[50, 250, 50])
            action_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (2, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (2, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (2, 0), 12),
                ('BACKGROUND', (0, 1), (2, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(action_table)
        else:
            story.append(Paragraph("アクション履歴なし", styles['Normal']))

        story.append(Spacer(1, 12))

        # 分析と改善提案
        story.append(Paragraph("分析と改善提案", styles['Heading2']))

        improvement_tips = self.generate_improvement_tips(summary)
        for tip in improvement_tips:
            story.append(Paragraph(f"・{tip}", styles['Normal']))
            story.append(Spacer(1, 6))

        try:
            doc.build(story)
            return pdf_path
        except Exception as e:
            print(f"PDFの生成に失敗しました: {e}")
            return None

    def generate_improvement_tips(self, summary):
        """改善提案の生成"""
        tips = []
        final_state = summary["final_state"]

        # CPU改善案
        if final_state["cpu"] > 80:
            tips.append("CPU使用率が高いままです。スケールアウトや負荷分散の検討が必要です。")

        # メモリ改善案
        if final_state["memory"] > 75:
            tips.append("メモリ使用率が高いままです。メモリリークの調査やプロセス最適化の検討が必要です。")

        # ディスク改善案
        if final_state["disk"] > 85:
            tips.append("ディスク使用率が危険域です。定期的なログクリーンアップの自動化やストレージ増設の検討が必要です。")

        # サービス改善案
        if final_state["services"] < summary.get("initial_services", 5):
            tips.append("一部のサービスが復旧していません。サービス自動復旧機能の実装を検討してください。")

        # SLAリスク改善案
        if final_state["sla_risk"] > 50:
            tips.append("SLA違反リスクが高いままです。障害検知の迅速化と初動対応の自動化を検討してください。")

        # アクション分析
        action_success_rate = 0
        if summary["actions_taken"]:
            success_count = sum(1 for a in summary["actions_taken"] if a["success"])
            action_success_rate = success_count / len(summary["actions_taken"])

            if action_success_rate < 0.7:
                tips.append(f"アクション成功率が低いです ({action_success_rate:.0%})。システム状態に応じた適切なアクション選択の訓練が必要です。")

        # 全体的な評価
        if summary["score"] < 300:
            tips.append("全体的なスコアが低いです。より迅速な初動対応と的確な判断力を養うトレーニングを継続してください。")
        elif summary["score"] > 600:
            tips.append("優れた対応結果です。この判断プロセスをチーム内で共有し、ベストプラクティスとして活用することを推奨します。")

        # 汎用的なアドバイス
        tips.append("障害対応プロセスをドキュメント化し、チーム内で共有することで、同様の障害への対応力を向上させましょう。")

        return tips