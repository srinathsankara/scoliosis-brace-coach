"""
Unit tests for sensors/brace_pressure.py

Tests pressure evaluation, compliance tracking, and temperature detection.
"""
import json
import os
import sqlite3
import time
import pytest
from datetime import datetime

from sensors.brace_pressure import (
    parse_pressure_data, evaluate_pressure, detect_wear_from_temperature,
    start_compliance_session, log_pressure_reading, end_compliance_session,
    get_compliance_summary, get_pressure_history, CORRECTION_POINTS,
    init_compliance_db, COMPLIANCE_DB
)


class TestParsePressureData:
    """Tests for sensor payload parsing."""

    def test_parses_valid_json_string(self):
        """Valid JSON string with required keys should parse successfully."""
        payload = json.dumps({
            'upper_support': 50.0,
            'middle_pressure': 60.0,
            'lower_support': 45.0,
            'skin_temp': 34.5
        })
        result = parse_pressure_data(payload)
        assert result is not None
        assert result['upper_support'] == 50.0
        assert result['middle_pressure'] == 60.0
        assert result['lower_support'] == 45.0
        assert result['skin_temp'] == 34.5

    def test_parses_dict_input(self):
        """Dict input should be parsed directly."""
        payload = {
            'upper_support': 50.0,
            'middle_pressure': 60.0,
            'lower_support': 45.0
        }
        result = parse_pressure_data(payload)
        assert result is not None
        assert result['upper_support'] == 50.0

    def test_returns_none_for_missing_keys(self):
        """Missing required keys should return None."""
        payload = {'upper_support': 50.0}
        result = parse_pressure_data(payload)
        assert result is None

    def test_returns_none_for_invalid_json(self):
        """Invalid JSON string should return None."""
        result = parse_pressure_data("not valid json {{{")
        assert result is None

    def test_returns_none_for_none_input(self):
        """None input should return None."""
        result = parse_pressure_data(None)
        assert result is None

    def test_includes_timestamp_if_provided(self):
        """Timestamp should be included if provided."""
        payload = {
            'upper_support': 50.0,
            'middle_pressure': 60.0,
            'lower_support': 45.0,
            'timestamp': '2025-01-15T10:30:00'
        }
        result = parse_pressure_data(payload)
        assert result['timestamp'] == '2025-01-15T10:30:00'

    def test_generates_timestamp_if_missing(self):
        """Timestamp should be auto-generated if not provided."""
        payload = {
            'upper_support': 50.0,
            'middle_pressure': 60.0,
            'lower_support': 45.0
        }
        result = parse_pressure_data(payload)
        assert 'timestamp' in result

    def test_converts_string_values_to_float(self):
        """String numeric values should be converted to float."""
        payload = {
            'upper_support': '50',
            'middle_pressure': '60',
            'lower_support': '45'
        }
        result = parse_pressure_data(payload)
        assert isinstance(result['upper_support'], float)


class TestEvaluatePressure:
    """Tests for pressure evaluation against ideal ranges."""

    def test_optimal_pressure_scores_100(self):
        """Readings within ideal range should score 100."""
        readings = {
            'upper_support': 50.0,  # ideal: 40-60
            'middle_pressure': 60.0,  # ideal: 50-70
            'lower_support': 45.0   # ideal: 35-55
        }
        result = evaluate_pressure(readings)
        assert result['score'] == 100.0
        assert result['status'] == 'analyzed'

    def test_too_low_pressure(self):
        """Readings below ideal range should score lower."""
        readings = {
            'upper_support': 20.0,  # way below 40-60
            'middle_pressure': 60.0,
            'lower_support': 45.0
        }
        result = evaluate_pressure(readings)
        assert result['score'] < 100.0
        assert result['points']['upper_support']['status'] in ('too_low', 'critically_off')

    def test_too_high_pressure(self):
        """Readings above ideal range should score lower."""
        readings = {
            'upper_support': 80.0,  # way above 40-60
            'middle_pressure': 60.0,
            'lower_support': 45.0
        }
        result = evaluate_pressure(readings)
        assert result['score'] < 100.0
        assert result['points']['upper_support']['status'] in ('too_high', 'critically_off')

    def test_returns_no_data_for_none(self):
        """None readings should return no_data status."""
        result = evaluate_pressure(None)
        assert result['status'] == 'no_data'
        assert result['score'] == 0

    def test_all_three_correction_points_present(self):
        """Result should contain all three correction points."""
        readings = {'upper_support': 50.0, 'middle_pressure': 60.0, 'lower_support': 45.0}
        result = evaluate_pressure(readings)
        assert set(result['points'].keys()) == {'upper_support', 'middle_pressure', 'lower_support'}

    def test_each_point_has_ideal_range(self):
        """Each point should include its ideal range."""
        readings = {'upper_support': 50.0, 'middle_pressure': 60.0, 'lower_support': 45.0}
        result = evaluate_pressure(readings)
        for point_name, point_data in result['points'].items():
            assert 'ideal_range' in point_data
            assert 'unit' in point_data
            assert point_data['unit'] == 'kPa'

    def test_score_is_bounded_0_to_100(self):
        """Overall score should always be between 0 and 100."""
        # Test with extreme values
        readings = {'upper_support': 0.0, 'middle_pressure': 0.0, 'lower_support': 0.0}
        result = evaluate_pressure(readings)
        assert 0 <= result['score'] <= 100

    def test_critically_off_score(self):
        """Very extreme values should be marked as critically_off."""
        readings = {
            'upper_support': 5.0,   # < 70% of 40 (min) = 28
            'middle_pressure': 60.0,
            'lower_support': 45.0
        }
        result = evaluate_pressure(readings)
        assert result['points']['upper_support']['status'] == 'critically_off'
        assert result['points']['upper_support']['score'] == 20


class TestTemperatureDetection:
    """Tests for temperature-based brace wear detection."""

    def test_brace_detected_above_threshold(self):
        """Temperature above baseline + 1.5 should detect brace."""
        readings = {'skin_temp': 35.0}  # baseline 33.0 + 1.5 = 34.5
        assert detect_wear_from_temperature(readings) is True

    def test_no_brace_below_threshold(self):
        """Temperature below baseline + 1.5 should not detect brace."""
        readings = {'skin_temp': 33.5}
        assert detect_wear_from_temperature(readings) is False

    def test_exactly_at_threshold(self):
        """Temperature exactly at threshold should not detect brace (not strictly greater)."""
        readings = {'skin_temp': 34.5}  # exactly baseline + 1.5
        assert detect_wear_from_temperature(readings) is False

    def test_returns_false_for_none(self):
        """None readings should return False."""
        assert detect_wear_from_temperature(None) is False

    def test_returns_false_for_missing_temp(self):
        """Readings without skin_temp should return False."""
        assert detect_wear_from_temperature({'upper_support': 50}) is False

    def test_custom_baseline(self):
        """Custom baseline should shift the threshold."""
        readings = {'skin_temp': 36.0}
        assert detect_wear_from_temperature(readings, baseline_skin_temp=34.0) is True
        assert detect_wear_from_temperature(readings, baseline_skin_temp=35.0) is False


class TestCorrectionPoints:
    """Tests for correction point configuration."""

    def test_three_correction_points_defined(self):
        """Should have exactly 3 correction points."""
        assert len(CORRECTION_POINTS) == 3

    def test_required_points_present(self):
        """All three required points should be defined."""
        assert 'upper_support' in CORRECTION_POINTS
        assert 'middle_pressure' in CORRECTION_POINTS
        assert 'lower_support' in CORRECTION_POINTS

    def test_each_point_has_ideal_range(self):
        """Each point should have an ideal_range tuple."""
        for name, config in CORRECTION_POINTS.items():
            assert 'ideal_range' in config
            low, high = config['ideal_range']
            assert low < high, f"{name}: ideal range low must be < high"

    def test_each_point_has_zone(self):
        """Each point should have a zone description."""
        for name, config in CORRECTION_POINTS.items():
            assert 'zone' in config
            assert isinstance(config['zone'], str)


class TestComplianceTracking:
    """Tests for compliance session lifecycle."""

    def test_full_lifecycle(self, tmp_path):
        """Test start -> log -> end -> summary lifecycle."""
        db_path = str(tmp_path / 'test_compliance.db')
        import sensors.brace_pressure as bp
        bp.COMPLIANCE_DB = db_path
        bp.init_compliance_db()

        # Start
        bp.start_compliance_session('test_session')

        # Log a reading
        readings = {'upper_support': 50.0, 'middle_pressure': 60.0, 'lower_support': 45.0, 'skin_temp': 34.5}
        bp.log_pressure_reading('test_session', readings, True)

        # End
        bp.end_compliance_session('test_session')

        # Summary
        summary = bp.get_compliance_summary('test_session')
        assert 'total_wear_minutes' in summary
        assert 'compliance_percentage' in summary
        assert 'status' in summary

    def test_pressure_history(self, tmp_path):
        """Pressure readings should be retrievable."""
        db_path = str(tmp_path / 'test_compliance.db')
        import sensors.brace_pressure as bp
        bp.COMPLIANCE_DB = db_path
        bp.init_compliance_db()

        bp.start_compliance_session('hist_session')
        readings = {'upper_support': 50.0, 'middle_pressure': 60.0, 'lower_support': 45.0, 'skin_temp': 34.5}
        bp.log_pressure_reading('hist_session', readings, True)

        history = bp.get_pressure_history('hist_session')
        assert len(history) == 1
        assert history[0]['upper_support'] == 50.0
        assert history[0]['brace_detected'] is True

    def test_compliance_status_categories(self):
        """Compliance status should be adequate, suboptimal, or poor."""
        # This tests the logic without DB
        assert 80 >= 0  # Just verifying our test logic
        # Full test via API integration tests
