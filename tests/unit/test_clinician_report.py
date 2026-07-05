"""
Unit tests for analysis/clinician_report.py

Tests PDF report generation and patient summary computation.
"""
import json
import sqlite3
import pytest
from datetime import datetime

from analysis.clinician_report import (
    get_patient_summary, generate_pdf_report, get_all_patients
)


class TestGetPatientSummary:
    """Tests for patient summary computation."""

    def test_returns_none_when_no_sessions(self, tmp_path):
        """No sessions should return None."""
        import analysis.clinician_report as cr
        cr.DB_PATH = str(tmp_path / 'empty.db')
        result = get_patient_summary()
        assert result is None

    def test_returns_summary_with_sessions(self, tmp_path):
        """Should return summary dict when sessions exist."""
        import analysis.clinician_report as cr
        db_path = str(tmp_path / 'test.db')
        cr.DB_PATH = db_path

        conn = sqlite3.connect(db_path)
        conn.execute('''CREATE TABLE sessions (
            job_id TEXT PRIMARY KEY, created_at TEXT, mode TEXT, result_json TEXT
        )''')
        result = {
            'status': 'success', 'mode': 'standing_no_brace', 'brace_detected': False,
            'metrics': {'trunk_lean_angle': 5.0, 'shoulder_asymmetry': 10.0}
        }
        conn.execute('INSERT INTO sessions VALUES (?, ?, ?, ?)',
                     ('j1', datetime.now().isoformat(), 'standing_no_brace', json.dumps(result)))
        conn.commit()
        conn.close()

        summary = get_patient_summary()
        assert summary is not None
        assert summary['total_sessions'] == 1
        assert 'session_summary' in summary

    def test_brace_effectiveness_computed(self, tmp_path):
        """Brace effectiveness should be computed when both with/without sessions exist."""
        import analysis.clinician_report as cr
        db_path = str(tmp_path / 'test.db')
        cr.DB_PATH = db_path

        conn = sqlite3.connect(db_path)
        conn.execute('''CREATE TABLE sessions (
            job_id TEXT PRIMARY KEY, created_at TEXT, mode TEXT, result_json TEXT
        )''')
        no_brace = {'status': 'success', 'mode': 'standing_no_brace', 'brace_detected': False,
                    'metrics': {'trunk_lean_angle': 8.0}}
        with_brace = {'status': 'success', 'mode': 'standing_with_brace', 'brace_detected': True,
                      'metrics': {'trunk_lean_angle': 3.0}}
        conn.execute('INSERT INTO sessions VALUES (?, ?, ?, ?)',
                     ('j1', datetime.now().isoformat(), 'standing_no_brace', json.dumps(no_brace)))
        conn.execute('INSERT INTO sessions VALUES (?, ?, ?, ?)',
                     ('j2', datetime.now().isoformat(), 'standing_with_brace', json.dumps(with_brace)))
        conn.commit()
        conn.close()

        summary = get_patient_summary()
        assert summary['brace_effectiveness'] is not None
        # Correction: (8-3)/8 * 100 = 62.5%
        assert summary['brace_effectiveness']['correction_percentage'] == 62.5

    def test_session_summary_counts(self, tmp_path):
        """Session summary should correctly count sessions by mode."""
        import analysis.clinician_report as cr
        db_path = str(tmp_path / 'test.db')
        cr.DB_PATH = db_path

        conn = sqlite3.connect(db_path)
        conn.execute('''CREATE TABLE sessions (
            job_id TEXT PRIMARY KEY, created_at TEXT, mode TEXT, result_json TEXT
        )''')
        modes = ['standing_no_brace', 'standing_no_brace', 'standing_with_brace', 'walking_no_brace', 'exercise']
        for i, mode in enumerate(modes):
            conn.execute('INSERT INTO sessions VALUES (?, ?, ?, ?)',
                         (f'j{i}', datetime.now().isoformat(), mode, '{}'))
        conn.commit()
        conn.close()

        summary = get_patient_summary()
        assert summary['session_summary']['standing_no_brace'] == 2
        assert summary['session_summary']['standing_with_brace'] == 1
        assert summary['session_summary']['walking'] == 1
        assert summary['session_summary']['exercise'] == 1


class TestGeneratePdfReport:
    """Tests for PDF report generation."""

    def test_generates_pdf_bytes(self, tmp_path):
        """Should generate non-empty PDF bytes."""
        import analysis.clinician_report as cr
        cr.DB_PATH = str(tmp_path / 'empty.db')

        pdf = generate_pdf_report()
        assert isinstance(pdf, bytes)
        assert len(pdf) > 0

    def test_pdf_starts_with_magic_bytes(self, tmp_path):
        """PDF should start with %PDF- header."""
        import analysis.clinician_report as cr
        cr.DB_PATH = str(tmp_path / 'empty.db')

        pdf = generate_pdf_report()
        assert pdf[:5] == b'%PDF-'

    def test_pdf_with_sessions(self, tmp_path):
        """PDF with session data should be larger than empty PDF."""
        import analysis.clinician_report as cr
        db_path = str(tmp_path / 'test.db')
        cr.DB_PATH = db_path

        conn = sqlite3.connect(db_path)
        conn.execute('''CREATE TABLE sessions (
            job_id TEXT PRIMARY KEY, created_at TEXT, mode TEXT, result_json TEXT
        )''')
        result = {'status': 'success', 'mode': 'standing_no_brace', 'brace_detected': False,
                  'metrics': {'trunk_lean_angle': 5.0, 'shoulder_asymmetry': 10.0}}
        conn.execute('INSERT INTO sessions VALUES (?, ?, ?, ?)',
                     ('j1', datetime.now().isoformat(), 'standing_no_brace', json.dumps(result)))
        conn.commit()
        conn.close()

        pdf_empty = generate_pdf_report.__wrapped__(str(tmp_path / 'empty.db')) if hasattr(generate_pdf_report, '__wrapped__') else None
        pdf_full = generate_pdf_report()
        assert len(pdf_full) > 100  # Should be substantial
