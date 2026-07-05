import os
import uuid
import json
import sqlite3
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from analysis.video_processor import process_media
from sensors.ble_scanner import get_available_sensors
from sensors.brace_pressure import (
    parse_pressure_data, evaluate_pressure, detect_wear_from_temperature,
    start_compliance_session, log_pressure_reading, end_compliance_session,
    get_compliance_summary, get_pressure_history
)
from analysis.trend_analysis import get_session_history, compute_trends, generate_progression_report
from analysis.clinician_report import get_patient_summary, generate_pdf_report

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

jobs = {}
DB_PATH = 'sessions.db'

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                job_id TEXT PRIMARY KEY,
                created_at TEXT,
                mode TEXT,
                result_json TEXT
            )
        ''')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'media' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['media']
    mode = request.form.get('mode', 'standing_no_brace')
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in ('.jpg', '.jpeg', '.png', '.mp4', '.mov'):
        return jsonify({'error': 'Unsupported format'}), 400

    job_id = str(uuid.uuid4())[:8]
    path = os.path.join(app.config['UPLOAD_FOLDER'], f'{job_id}{ext}')
    file.save(path)

    jobs[job_id] = {'status': 'processing', 'progress': 0}
    threading.Thread(target=run_analysis, args=(job_id, path, mode, request.form.get('age_group', 'under15')), daemon=True).start()
    return jsonify({'job_id': job_id})

def run_analysis(job_id, path, mode, age_group):
    try:
        result = process_media(path, mode, age_group)
        if result.get('status') == 'error':
            jobs[job_id] = {'status': 'error', 'message': result.get('message', 'Analysis failed')}
        else:
            jobs[job_id] = {'status': 'done', 'result': result}
            with sqlite3.connect(DB_PATH) as con:
                con.execute('INSERT INTO sessions (job_id, created_at, mode, result_json) VALUES (?, ?, ?, ?)',
                            (job_id, datetime.now().isoformat(), mode, json.dumps(result)))
    except Exception as e:
        jobs[job_id] = {'status': 'error', 'message': str(e)}

@app.route('/status/<job_id>')
def status(job_id):
    return jsonify(jobs.get(job_id, {'error': 'Not found'}))

@app.route('/results/<job_id>')
def results(job_id):
    job = jobs.get(job_id)
    if not job:
        return "Result not found", 404
    if job['status'] == 'error':
        return render_template('results.html', result={'status': 'error', 'message': job.get('message', 'Unknown error')}, job_id=job_id)
    if job['status'] != 'done':
        return "Result not ready", 404
    return render_template('results.html', result=job['result'], job_id=job_id)

@app.route('/sensors')
def sensors_page():
    devices = []
    try:
        devices = get_available_sensors()
    except Exception:
        pass
    return render_template('sensors.html', devices=devices)

@app.route('/history')
def history():
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute('SELECT job_id, created_at, mode FROM sessions ORDER BY created_at DESC').fetchall()
    return render_template('history.html', sessions=rows)

@app.route('/compare')
def compare_page():
    with sqlite3.connect(DB_PATH) as con:
        sessions = con.execute('SELECT job_id, created_at, mode FROM sessions ORDER BY created_at DESC').fetchall()
    return render_template('compare.html', sessions=sessions)

@app.route('/api/session/<job_id>')
def get_session(job_id):
    with sqlite3.connect(DB_PATH) as con:
        row = con.execute('SELECT result_json FROM sessions WHERE job_id=?', (job_id,)).fetchone()
    if row:
        return jsonify(json.loads(row[0]))
    return jsonify({'error': 'Not found'}), 404

@app.route('/dashboard')
def clinician_dashboard():
    summary = get_patient_summary()
    return render_template('dashboard.html', summary=summary)

@app.route('/api/trends')
def api_trends():
    mode = request.args.get('mode')
    sessions = get_session_history(mode=mode)
    trends = compute_trends(sessions)
    return jsonify(trends)

@app.route('/api/progression-report')
def api_progression_report():
    report = generate_progression_report()
    return jsonify(report)

@app.route('/api/pdf-report')
def api_pdf_report():
    pdf_bytes = generate_pdf_report()
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment; filename=scoliosis_report.pdf'}
    )

@app.route('/api/pressure/evaluate', methods=['POST'])
def api_pressure_evaluate():
    data = request.get_json()
    readings = parse_pressure_data(data)
    if not readings:
        return jsonify({'error': 'Invalid pressure data format'}), 400
    evaluation = evaluate_pressure(readings)
    return jsonify(evaluation)

@app.route('/api/compliance/start', methods=['POST'])
def api_compliance_start():
    data = request.get_json()
    session_id = data.get('session_id', str(uuid.uuid4())[:8])
    start_compliance_session(session_id)
    return jsonify({'session_id': session_id, 'status': 'started'})

@app.route('/api/compliance/log', methods=['POST'])
def api_compliance_log():
    data = request.get_json()
    session_id = data.get('session_id')
    readings = parse_pressure_data(data)
    brace_detected = data.get('brace_detected', False)
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400
    log_pressure_reading(session_id, readings or {}, brace_detected)
    return jsonify({'status': 'logged'})

@app.route('/api/compliance/end', methods=['POST'])
def api_compliance_end():
    data = request.get_json()
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400
    end_compliance_session(session_id)
    summary = get_compliance_summary(session_id)
    return jsonify(summary)

@app.route('/api/compliance/summary/<session_id>')
def api_compliance_summary(session_id):
    summary = get_compliance_summary(session_id)
    return jsonify(summary)

@app.route('/api/pressure/history/<session_id>')
def api_pressure_history(session_id):
    history = get_pressure_history(session_id)
    return jsonify(history)

@app.route('/trends')
def trends_page():
    return render_template('trends.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
