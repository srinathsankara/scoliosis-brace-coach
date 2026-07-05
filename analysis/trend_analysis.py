import sqlite3
import json
from datetime import datetime, timedelta
from statistics import mean, stdev

TREND_DB = 'sessions.db'

PROGRESSION_THRESHOLDS = {
    'trunk_lean_angle': {'significant': 5.0, 'alert': 3.0},
    'shoulder_asymmetry': {'significant': 8.0, 'alert': 5.0},
    'hip_asymmetry': {'significant': 6.0, 'alert': 4.0},
    'rib_hump_proxy': {'significant': 5.0, 'alert': 3.0},
    'trunk_rotation_angle': {'significant': 4.0, 'alert': 2.5},
    'spine_deviation': {'significant': 8.0, 'alert': 5.0}
}

def get_session_history(session_id=None, mode=None, limit=100):
    with sqlite3.connect(TREND_DB) as con:
        if session_id:
            rows = con.execute(
                'SELECT job_id, created_at, mode, result_json FROM sessions WHERE job_id=?',
                (session_id,)
            ).fetchall()
        elif mode:
            rows = con.execute(
                'SELECT job_id, created_at, mode, result_json FROM sessions WHERE mode=? ORDER BY created_at DESC LIMIT ?',
                (mode, limit)
            ).fetchall()
        else:
            rows = con.execute(
                'SELECT job_id, created_at, mode, result_json FROM sessions ORDER BY created_at DESC LIMIT ?',
                (limit,)
            ).fetchall()

    sessions = []
    for r in rows:
        try:
            result = json.loads(r[3])
            sessions.append({
                'job_id': r[0],
                'created_at': r[1],
                'mode': r[2],
                'metrics': result.get('metrics', {}),
                'brace_detected': result.get('brace_detected', False)
            })
        except (json.JSONDecodeError, TypeError):
            continue
    return sessions

def compute_trends(sessions):
    """
    Compute longitudinal trends across multiple sessions.
    Returns per-metric trend direction, rate of change, and alerts.
    """
    if len(sessions) < 2:
        return {'status': 'insufficient_data', 'message': 'Need at least 2 sessions for trend analysis'}

    metric_series = {}
    for s in reversed(sessions):
        for key, value in s['metrics'].items():
            if isinstance(value, (int, float)):
                if key not in metric_series:
                    metric_series[key] = []
                metric_series[key].append({
                    'value': value,
                    'date': s['created_at'],
                    'session_id': s['job_id']
                })

    trends = {}
    alerts = []

    for metric_name, data_points in metric_series.items():
        if len(data_points) < 2:
            continue

        values = [d['value'] for d in data_points]
        dates = [d['date'] for d in data_points]

        # Simple linear regression for trend direction
        n = len(values)
        x = list(range(n))
        x_mean = mean(x)
        y_mean = mean(values)

        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
        denominator = sum((xi - x_mean) ** 2 for xi in x)

        slope = numerator / denominator if denominator != 0 else 0

        # Trend direction
        if abs(slope) < 0.1:
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'

        # Rate of change per session
        total_change = values[-1] - values[0]
        pct_change = (total_change / values[0] * 100) if values[0] != 0 else 0

        # Check against progression thresholds
        thresholds = PROGRESSION_THRESHOLDS.get(metric_name, {})
        if thresholds:
            if abs(total_change) >= thresholds.get('significant', float('inf')):
                alert_level = 'critical'
                alert_msg = f'Significant progression detected in {metric_name}: {total_change:+.1f} over {len(data_points)} sessions'
                alerts.append({'metric': metric_name, 'level': alert_level, 'message': alert_msg, 'change': round(total_change, 2)})
            elif abs(total_change) >= thresholds.get('alert', float('inf')):
                alert_level = 'warning'
                alert_msg = f'Worsening trend in {metric_name}: {total_change:+.1f} over {len(data_points)} sessions'
                alerts.append({'metric': metric_name, 'level': alert_level, 'message': alert_msg, 'change': round(total_change, 2)})

        # Standard deviation for variability
        variability = stdev(values) if len(values) > 1 else 0

        trends[metric_name] = {
            'direction': direction,
            'slope_per_session': round(slope, 3),
            'total_change': round(total_change, 2),
            'percent_change': round(pct_change, 1),
            'current_value': values[-1],
            'baseline_value': values[0],
            'variability': round(variability, 2),
            'session_count': n,
            'first_date': dates[0],
            'last_date': dates[-1]
        }

    return {
        'status': 'analyzed',
        'trends': trends,
        'alerts': alerts,
        'session_count': len(sessions),
        'date_range': {
            'first': sessions[0]['created_at'] if sessions else None,
            'last': sessions[-1]['created_at'] if sessions else None
        }
    }

def generate_progression_report(patient_id=None, mode=None):
    """
    Generate a comprehensive progression report for a patient.
    Includes trends, alerts, and recommendations.
    """
    sessions = get_session_history(mode=mode)
    if not sessions:
        return {'status': 'no_data', 'message': 'No sessions found'}

    trends = compute_trends(sessions)

    # Summary stats
    all_trunk_angles = [s['metrics'].get('trunk_lean_angle', 0) for s in sessions if 'trunk_lean_angle' in s['metrics']]
    all_shoulder = [s['metrics'].get('shoulder_asymmetry', 0) for s in sessions if 'shoulder_asymmetry' in s['metrics']]

    report = {
        'patient_id': patient_id,
        'generated_at': datetime.now().isoformat(),
        'total_sessions': len(sessions),
        'date_range': trends.get('date_range', {}),
        'summary': {
            'latest_trunk_angle': all_trunk_angles[-1] if all_trunk_angles else None,
            'avg_trunk_angle': round(mean(all_trunk_angles), 2) if all_trunk_angles else None,
            'latest_shoulder_asym': all_shoulder[-1] if all_shoulder else None,
            'avg_shoulder_asym': round(mean(all_shoulder), 2) if all_shoulder else None
        },
        'trends': trends,
        'recommendations': _generate_recommendations(trends)
    }
    return report

def _generate_recommendations(trends):
    recommendations = []
    if trends.get('status') != 'analyzed':
        return ['Insufficient data for recommendations. Continue regular monitoring.']

    for alert in trends.get('alerts', []):
        if alert['level'] == 'critical':
            recommendations.append(f"URGENT: {alert['message']}. Consult orthopedic specialist immediately.")
        elif alert['level'] == 'warning':
            recommendations.append(f"Review needed: {alert['message']}. Schedule follow-up with care team.")

    stable_metrics = [k for k, v in trends.get('trends', {}).items() if v['direction'] == 'stable']
    if stable_metrics:
        recommendations.append(f"Positive: {', '.join(stable_metrics)} are stable. Continue current treatment plan.")

    improving = [k for k, v in trends.get('trends', {}).items() if v['direction'] == 'decreasing' and 'asymmetry' in k or 'angle' in k or 'deviation' in k]
    if improving:
        recommendations.append(f"Improvement noted in: {', '.join(improving)}. Treatment appears effective.")

    if not recommendations:
        recommendations.append("Continue regular monitoring sessions. No significant changes detected.")

    return recommendations
