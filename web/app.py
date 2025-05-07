from flask import Flask, render_template, request, jsonify, session
import sys
import os
import json
import uuid
import datetime

# パスの調整（実行ディレクトリに関わらず動作するように）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.simulator import InfraRiskSimulator
from app.report import ReportGenerator

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_simulator')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=2)

# シミュレータのインスタンスを保持する辞書
simulators = {}

@app.route('/')
def index():
    """トップページの表示"""
    # 新しいセッションID生成
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    return render_template('index.html')

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """利用可能なシナリオ一覧を取得"""
    # 一時的なシミュレータインスタンスからシナリオ一覧を取得
    temp_simulator = InfraRiskSimulator()
    scenarios = temp_simulator.event_manager.scenarios
    return jsonify(scenarios)

@app.route('/api/start', methods=['POST'])
def start_scenario():
    """シナリオを開始する"""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({"error": "セッションが無効です"}), 400

    data = request.get_json()
    scenario_id = data.get('scenario_id')

    # 新しいシミュレータインスタンス作成
    simulator = InfraRiskSimulator()

    # シナリオ開始
    scenario = simulator.start_scenario(scenario_id)

    # シミュレータをセッションIDで保存
    simulators[session_id] = simulator

    return jsonify({
        "success": True,
        "scenario": scenario,
        "state": simulator.system_state.get_state_dict(),
        "turn": simulator.turn
    })

@app.route('/api/next-turn', methods=['POST'])
def next_turn():
    """次のターンに進む"""
    session_id = session.get('session_id')
    if not session_id or session_id not in simulators:
        return jsonify({"error": "セッションが無効か期限切れです"}), 400

    simulator = simulators[session_id]
    turn_result = simulator.next_turn()

    return jsonify(turn_result)

@app.route('/api/actions', methods=['GET'])
def get_actions():
    """利用可能なアクションを取得"""
    session_id = session.get('session_id')
    if not session_id or session_id not in simulators:
        return jsonify({"error": "セッションが無効か期限切れです"}), 400

    simulator = simulators[session_id]
    actions = simulator.get_available_actions()

    return jsonify(actions)

@app.route('/api/take-action', methods=['POST'])
def take_action():
    """アクションを実行"""
    session_id = session.get('session_id')
    if not session_id or session_id not in simulators:
        return jsonify({"error": "セッションが無効か期限切れです"}), 400

    data = request.get_json()
    action_id = data.get('action_id')

    simulator = simulators[session_id]
    result = simulator.take_action(action_id)

    return jsonify(result)

@app.route('/api/report', methods=['GET'])
def get_report():
    """結果レポートを取得"""
    session_id = session.get('session_id')
    if not session_id or session_id not in simulators:
        return jsonify({"error": "セッションが無効か期限切れです"}), 400

    simulator = simulators[session_id]
    report_generator = ReportGenerator(simulator)

    # テキストレポート生成
    text_report = report_generator.generate_text_report()

    # PDFレポート生成
    pdf_filename = f"infra_report_{simulator.session_id}"
    pdf_path = report_generator.generate_pdf(pdf_filename)

    # 相対パスに変換
    if pdf_path:
        pdf_url = f"/reports/{os.path.basename(pdf_path)}"
    else:
        pdf_url = None

    return jsonify({
        "text_report": text_report,
        "pdf_url": pdf_url,
        "score": simulator.calculate_score()
    })

@app.route('/reports/<path:filename>')
def download_report(filename):
    """レポートのダウンロード"""
    directory = os.path.abspath("data/reports")
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/api/clean-session', methods=['POST'])
def clean_session():
    """セッションクリーンアップ"""
    session_id = session.get('session_id')
    if session_id and session_id in simulators:
        del simulators[session_id]
    session.clear()
    return jsonify({"success": True})

# 古いセッションの定期的なクリーンアップ (実際の実装ではバックグラウンドタスクが望ましい)
@app.before_request
def cleanup_old_sessions():
    current_time = datetime.datetime.now()
    sessions_to_remove = []

    for sess_id, simulator in simulators.items():
        # 2時間以上前のセッションをクリーンアップ
        created_time = datetime.datetime.strptime(simulator.session_id, "%Y%m%d_%H%M%S")
        if (current_time - created_time).total_seconds() > 7200:
            sessions_to_remove.append(sess_id)

    for sess_id in sessions_to_remove:
        del simulators[sess_id]

if __name__ == '__main__':
    # ディレクトリ作成
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/reports", exist_ok=True)

    # 開発環境ではデバッグモード有効
    app.run(debug=True)