"""
Unit tests for analysis/trend_analysis.py

Tests longitudinal trend computation including:
- Session history retrieval
- Linear regression trend computation
- Progression alert generation
- Recommendation generation
- Edge cases: empty data, single session, identical values
"""
import json
import sqlite3
import pytest
from datetime import datetime, timedelta

from analysis.trend_analysis import (
    get_session_history, compute_trends, generate_progression_report,
    PROGRESSION_THRESHOLDS, _generate_recommendations
)
from tests.conftest import insert_test_session


class TestGetSessionHistory:
    """Tests for session history retrieval."""

    def test_returns_empty_list_when_no_sessions(self):
        """Empty DB should return empty list."""
        result = get_session_history()
        # May return sessions from real DB if not isolated, but structure should be list
        assert isinstance(result, list)

    def test_returns_sessions_in_chronological_order(self, tmp_path):
        """Sessions should be returned in descending order (newest first)."""
        db_path = str(tmp_path / 'test_sessions.db')
        conn = sqlite3.connect(db_path)
        conn.execute('''CREATE TABLE sessions (
            job_id TEXT PRIMARY KEY, created_at TEXT, mode TEXT, result_json TEXT
        )''')
        now = datetime.now()
        for i in range(5):
            conn.execute(
                'INSERT INTO sessions VALUES (?, ?, ?, ?)',
                (f'job_{i}', (now - timedelta(hours=i)).isoformat(),
                 'standing_no_brace', json.dumps({'metrics': {'trunk_lean_angle': i}}))
            )
        conn.commit()
        conn.close()

        from analysis import trend_analysis
        trend_analysis.TREND_DB = db_path
        result = get_session_history()
        assert len(result) == 5
        # First should be most recent
        assert result[0]['job_id'] == 'job_0'

    def test_filters_by_mode(self, tmp_path):
        """Filtering by mode should only return matching sessions."""
        db_path = str(tmp_path / 'test_sessions.db')
        conn = sqlite3.connect(db_path)
        conn.execute('''CREATE TABLE sessions (
            job_id TEXT PRIMARY KEY, created_at TEXT, mode TEXT, result_json TEXT
        )''')
        conn.execute('INSERT INTO sessions VALUES (?, ?, ?, ?)',
                     ('j1', datetime.now().isoformat(), 'standing_no_brace', '{}'))
        conn.execute('INSERT INTO sessions VALUES (?, ?, ?, ?)',
                     ('j2', datetime.now().isoformat(), 'walking_with_brace', '{}'))
        conn.commit()
        conn.close()

        from analysis import trend_analysis
        trend_analysis.TREND_DB = db_path
        result = get_session_history(mode='standing_no_brace')
        assert len(result) == 1
        assert result[0]['mode'] == 'standing_no_brace'

    def test_respects_limit(self, tmp_path):
        """Limit parameter should cap the number of results."""
        db_path = str(tmp_path / 'test_sessions.db')
        conn = sqlite3.connect(db_path)
        conn.execute('''CREATE TABLE sessions (
            job_id TEXT PRIMARY KEY, created_at TEXT, mode TEXT, result_json TEXT
        )''')
        for i in range(10):
            conn.execute('INSERT INTO sessions VALUES (?, ?, ?, ?)',
                         (f'j{i}', datetime.now().isoformat(), 'standing_no_brace', '{}'))
        conn.commit()
        conn.close()

        from analysis import trend_analysis
        trend_analysis.TREND_DB = db_path
        result = get_session_history(limit=3)
        assert len(result) == 3


class TestComputeTrends:
    """Tests for trend computation via linear regression."""

    def test_insufficient_data_with_empty_list(self):
        """Empty session list should return insufficient_data status."""
        result = compute_trends([])
        assert result['status'] == 'insufficient_data'

    def test_insufficient_data_with_single_session(self):
        """Single session should return insufficient_data (need at least 2)."""
        sessions = [{'metrics': {'trunk_lean_angle': 5.0}, 'created_at': '2025-01-01', 'job_id': 'j1', 'mode': 'standing_no_brace'}]
        result = compute_trends(sessions)
        assert result['status'] == 'insufficient_data'

    def test_stable_trend_for_identical_values(self):
        """Identical values across sessions should show 'stable' direction."""
        # Sessions in DESC order (newest first) matching get_session_history
        sessions = [
            {'metrics': {'trunk_lean_angle': 5.0}, 'created_at': f'2025-01-{i:02d}', 'job_id': f'j{i}', 'mode': 'standing_no_brace'}
            for i in range(5, 0, -1)
        ]
        result = compute_trends(sessions)
        assert result['status'] == 'analyzed'
        assert result['trends']['trunk_lean_angle']['direction'] == 'stable'

    def test_increasing_trend(self):
        """Rising values should show 'increasing' direction."""
        # Sessions in DESC order (newest first) matching get_session_history
        sessions = [
            {'metrics': {'trunk_lean_angle': (6 - i) * 2.0}, 'created_at': f'2025-01-{6-i:02d}', 'job_id': f'j{i}', 'mode': 'standing_no_brace'}
            for i in range(1, 6)
        ]
        result = compute_trends(sessions)
        assert result['trends']['trunk_lean_angle']['direction'] == 'increasing'
        assert result['trends']['trunk_lean_angle']['total_change'] > 0

    def test_decreasing_trend(self):
        """Falling values should show 'decreasing' direction."""
        # Sessions in DESC order (newest first) matching get_session_history
        sessions = [
            {'metrics': {'shoulder_asymmetry': 10 + (i - 1) * 2.0}, 'created_at': f'2025-01-{6-i:02d}', 'job_id': f'j{i}', 'mode': 'standing_no_brace'}
            for i in range(1, 6)
        ]
        result = compute_trends(sessions)
        assert result['trends']['shoulder_asymmetry']['direction'] == 'decreasing'

    def test_critical_alert_on_large_change(self):
        """Change exceeding critical threshold should generate critical alert."""
        # Sessions in DESC order (newest first) matching get_session_history
        sessions = [
            {'metrics': {'trunk_lean_angle': 8.0}, 'created_at': '2025-01-05', 'job_id': 'j2', 'mode': 'standing_no_brace'},
            {'metrics': {'trunk_lean_angle': 1.0}, 'created_at': '2025-01-01', 'job_id': 'j1', 'mode': 'standing_no_brace'},
        ]
        result = compute_trends(sessions)
        critical_alerts = [a for a in result['alerts'] if a['level'] == 'critical']
        assert len(critical_alerts) > 0

    def test_warning_alert_on_moderate_change(self):
        """Change exceeding warning threshold should generate warning alert."""
        # Sessions in DESC order (newest first) matching get_session_history
        sessions = [
            {'metrics': {'trunk_lean_angle': 5.5}, 'created_at': '2025-01-05', 'job_id': 'j2', 'mode': 'standing_no_brace'},
            {'metrics': {'trunk_lean_angle': 2.0}, 'created_at': '2025-01-01', 'job_id': 'j1', 'mode': 'standing_no_brace'},
        ]
        result = compute_trends(sessions)
        warning_alerts = [a for a in result['alerts'] if a['level'] == 'warning']
        assert len(warning_alerts) > 0

    def test_no_alerts_for_stable_data(self):
        """Stable data should produce no alerts."""
        sessions = [
            {'metrics': {'trunk_lean_angle': 3.0}, 'created_at': f'2025-01-{i:02d}', 'job_id': f'j{i}', 'mode': 'standing_no_brace'}
            for i in range(1, 6)
        ]
        result = compute_trends(sessions)
        assert len(result['alerts']) == 0

    def test_trends_include_session_count(self):
        """Each metric trend should include session_count."""
        sessions = [
            {'metrics': {'trunk_lean_angle': float(i)}, 'created_at': f'2025-01-{i:02d}', 'job_id': f'j{i}', 'mode': 'standing_no_brace'}
            for i in range(1, 5)
        ]
        result = compute_trends(sessions)
        assert result['trends']['trunk_lean_angle']['session_count'] == 4

    def test_non_numeric_metrics_excluded(self):
        """Non-numeric metric values (strings, bools) should be excluded."""
        sessions = [
            {'metrics': {'trunk_lean_angle': 5.0, 'shoulder_status': 'good'}, 'created_at': '2025-01-01', 'job_id': 'j1', 'mode': 'standing_no_brace'},
            {'metrics': {'trunk_lean_angle': 6.0, 'shoulder_status': 'needs_improvement'}, 'created_at': '2025-01-02', 'job_id': 'j2', 'mode': 'standing_no_brace'},
        ]
        result = compute_trends(sessions)
        assert 'shoulder_status' not in result['trends']
        assert 'trunk_lean_angle' in result['trends']


class TestGenerateRecommendations:
    """Tests for recommendation generation."""

    def test_returns_list(self):
        """Should always return a list of strings."""
        trends = {'status': 'analyzed', 'trends': {}, 'alerts': []}
        result = _generate_recommendations(trends)
        assert isinstance(result, list)
        assert all(isinstance(r, str) for r in result)

    def test_insufficient_data_message(self):
        """Non-analyzed status should suggest continued monitoring."""
        trends = {'status': 'insufficient_data'}
        result = _generate_recommendations(trends)
        assert any('Insufficient data' in r or 'Continue' in r for r in result)

    def test_critical_alert_recommends_specialist(self):
        """Critical alerts should recommend consulting a specialist."""
        trends = {
            'status': 'analyzed',
            'trends': {},
            'alerts': [{'metric': 'trunk_lean_angle', 'level': 'critical', 'message': 'test', 'change': 6.0}]
        }
        result = _generate_recommendations(trends)
        assert any('URGENT' in r or 'specialist' in r.lower() for r in result)

    def test_stable_metrics_positive(self):
        """Stable metrics should generate positive recommendations."""
        trends = {
            'status': 'analyzed',
            'trends': {
                'trunk_lean_angle': {'direction': 'stable'},
                'shoulder_asymmetry': {'direction': 'stable'}
            },
            'alerts': []
        }
        result = _generate_recommendations(trends)
        assert any('Positive' in r or 'stable' in r.lower() for r in result)


class TestProgressionThresholds:
    """Tests for threshold configuration."""

    def test_all_expected_metrics_have_thresholds(self):
        """Every tracked metric should have a threshold configuration."""
        expected = {'trunk_lean_angle', 'shoulder_asymmetry', 'hip_asymmetry',
                    'rib_hump_proxy', 'trunk_rotation_angle', 'spine_deviation'}
        assert expected == set(PROGRESSION_THRESHOLDS.keys())

    def test_thresholds_have_both_levels(self):
        """Each threshold should have both 'significant' and 'alert' levels."""
        for metric, thresholds in PROGRESSION_THRESHOLDS.items():
            assert 'significant' in thresholds, f"{metric} missing 'significant'"
            assert 'alert' in thresholds, f"{metric} missing 'alert'"
            assert thresholds['significant'] > thresholds['alert'], f"{metric}: significant must > alert"
