import time
import json
import sqlite3
from datetime import datetime, timedelta

CORRECTION_POINTS = {
    'upper_support': {'zone': 'upper_lateral', 'ideal_range': (40, 60), 'unit': 'kPa'},
    'middle_pressure': {'zone': 'apex', 'ideal_range': (50, 70), 'unit': 'kPa'},
    'lower_support': {'zone': 'lower_lateral', 'ideal_range': (35, 55), 'unit': 'kPa'}
}

COMPLIANCE_DB = 'compliance.db'

def init_compliance_db():
    with sqlite3.connect(COMPLIANCE_DB) as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS wear_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                started_at TEXT,
                ended_at TEXT,
                total_minutes INTEGER,
                temperature_readings TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        con.execute('''
            CREATE TABLE IF NOT EXISTS pressure_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                upper_support REAL,
                middle_pressure REAL,
                lower_support REAL,
                skin_temp REAL,
                brace_detected INTEGER
            )
        ''')

def parse_pressure_data(sensor_payload):
    """
    Parse pressure data from smart brace BLE payload.
    Expected format: JSON with pressure readings at correction points.
    Compatible with ScolioSense, Boston Sensor, and generic BLE braces.
    """
    if isinstance(sensor_payload, str):
        try:
            sensor_payload = json.loads(sensor_payload)
        except json.JSONDecodeError:
            return None

    required_keys = ['upper_support', 'middle_pressure', 'lower_support']
    if not all(k in sensor_payload for k in required_keys):
        return None

    readings = {
        'upper_support': float(sensor_payload['upper_support']),
        'middle_pressure': float(sensor_payload['middle_pressure']),
        'lower_support': float(sensor_payload['lower_support']),
        'skin_temp': float(sensor_payload.get('skin_temp', 0)),
        'timestamp': sensor_payload.get('timestamp', datetime.now().isoformat())
    }
    return readings

def evaluate_pressure(readings):
    """
    Evaluate brace pressure readings against ideal correction ranges.
    Returns per-point analysis and overall brace effectiveness score.
    """
    if not readings:
        return {'status': 'no_data', 'points': {}, 'score': 0}

    points = {}
    total_score = 0

    for point_name, config in CORRECTION_POINTS.items():
        value = readings.get(point_name, 0)
        ideal_min, ideal_max = config['ideal_range']

        if ideal_min <= value <= ideal_max:
            status = 'optimal'
            score = 100
        elif value < ideal_min * 0.7 or value > ideal_max * 1.3:
            status = 'critically_off'
            score = 20
        elif value < ideal_min:
            status = 'too_low'
            score = 50
        else:
            status = 'too_high'
            score = 50

        points[point_name] = {
            'value': value,
            'unit': config['unit'],
            'ideal_range': config['ideal_range'],
            'status': status,
            'score': score,
            'zone': config['zone']
        }
        total_score += score

    avg_score = total_score / len(CORRECTION_POINTS)

    return {
        'status': 'analyzed',
        'points': points,
        'score': round(avg_score, 1),
        'summary': _pressure_summary(points)
    }

def _pressure_summary(points):
    optimal = sum(1 for p in points.values() if p['status'] == 'optimal')
    total = len(points)
    if optimal == total:
        return 'All correction points are at optimal pressure. Brace is applying corrective force correctly.'
    elif optimal >= total * 0.6:
        return 'Most correction points are adequate. Minor adjustments may improve fit.'
    else:
        return 'Significant pressure deviations detected. Brace may need professional adjustment.'

def detect_wear_from_temperature(readings, baseline_skin_temp=33.0):
    """
    Detect if brace is being worn based on skin temperature.
    When a brace is worn, trapped heat raises local skin temperature.
    Returns True if brace-worn likely.
    """
    if not readings or 'skin_temp' not in readings:
        return False
    temp = readings['skin_temp']
    return temp > baseline_skin_temp + 1.5

def start_compliance_session(session_id):
    init_compliance_db()
    with sqlite3.connect(COMPLIANCE_DB) as con:
        con.execute(
            'INSERT INTO wear_sessions (session_id, started_at, status) VALUES (?, ?, ?)',
            (session_id, datetime.now().isoformat(), 'active')
        )

def log_pressure_reading(session_id, readings, brace_detected):
    init_compliance_db()
    with sqlite3.connect(COMPLIANCE_DB) as con:
        con.execute(
            '''INSERT INTO pressure_log
               (session_id, timestamp, upper_support, middle_pressure, lower_support, skin_temp, brace_detected)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (session_id, datetime.now().isoformat(),
             readings.get('upper_support', 0), readings.get('middle_pressure', 0),
             readings.get('lower_support', 0), readings.get('skin_temp', 0),
             1 if brace_detected else 0)
        )

def end_compliance_session(session_id):
    init_compliance_db()
    with sqlite3.connect(COMPLIANCE_DB) as con:
        row = con.execute(
            'SELECT started_at FROM wear_sessions WHERE session_id=? AND status=?',
            (session_id, 'active')
        ).fetchone()
        if row:
            started = datetime.fromisoformat(row[0])
            elapsed = int((datetime.now() - started).total_seconds() / 60)
            con.execute(
                'UPDATE wear_sessions SET ended_at=?, total_minutes=?, status=? WHERE session_id=?',
                (datetime.now().isoformat(), elapsed, 'completed', session_id)
            )

def get_compliance_summary(session_id, prescribed_hours=23):
    init_compliance_db()
    with sqlite3.connect(COMPLIANCE_DB) as con:
        rows = con.execute(
            'SELECT total_minutes FROM wear_sessions WHERE session_id=?',
            (session_id,)
        ).fetchall()

    total_minutes = sum(r[0] or 0 for r in rows)
    prescribed_minutes = prescribed_hours * 60
    compliance_pct = round((total_minutes / prescribed_minutes) * 100, 1) if prescribed_minutes > 0 else 0

    return {
        'total_wear_minutes': total_minutes,
        'total_wear_hours': round(total_minutes / 60, 1),
        'prescribed_hours': prescribed_hours,
        'compliance_percentage': compliance_pct,
        'status': 'adequate' if compliance_pct >= 80 else 'suboptimal' if compliance_pct >= 50 else 'poor'
    }

def get_pressure_history(session_id, limit=50):
    init_compliance_db()
    with sqlite3.connect(COMPLIANCE_DB) as con:
        rows = con.execute(
            'SELECT timestamp, upper_support, middle_pressure, lower_support, skin_temp, brace_detected FROM pressure_log WHERE session_id=? ORDER BY timestamp DESC LIMIT ?',
            (session_id, limit)
        ).fetchall()

    return [
        {
            'timestamp': r[0], 'upper_support': r[1], 'middle_pressure': r[2],
            'lower_support': r[3], 'skin_temp': r[4], 'brace_detected': bool(r[5])
        }
        for r in rows
    ]

init_compliance_db()
