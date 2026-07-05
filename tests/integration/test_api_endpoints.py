"""
Integration tests for Flask API endpoints.

Tests all routes for correct status codes, response structures,
and database state mutations. Uses the Flask test client.
"""
import json
import io
import pytest


# ---------------------------------------------------------------------------
# Page Routes (HTML responses)
# ---------------------------------------------------------------------------

class TestPageRoutes:
    """Tests for HTML page routes."""

    def test_index_returns_200(self, client):
        """Home page should return 200."""
        resp = client.get('/')
        assert resp.status_code == 200

    def test_index_contains_upload_form(self, client):
        """Home page should contain the upload form."""
        resp = client.get('/')
        assert b'uploadForm' in resp.data
        assert b'Analyze Session' in resp.data

    def test_history_returns_200(self, client):
        """History page should return 200."""
        resp = client.get('/history')
        assert resp.status_code == 200

    def test_compare_returns_200(self, client):
        """Compare page should return 200."""
        resp = client.get('/compare')
        assert resp.status_code == 200

    def test_dashboard_returns_200(self, client):
        """Dashboard page should return 200."""
        resp = client.get('/dashboard')
        assert resp.status_code == 200

    def test_trends_returns_200(self, client):
        """Trends page should return 200."""
        resp = client.get('/trends')
        assert resp.status_code == 200

    def test_sensors_returns_200(self, client):
        """Sensors page should return 200."""
        resp = client.get('/sensors')
        assert resp.status_code == 200

    def test_about_returns_200(self, client):
        """About page should return 200."""
        resp = client.get('/about')
        assert resp.status_code == 200

    def test_results_404_for_missing_job(self, client):
        """Results for non-existent job should return 404."""
        resp = client.get('/results/nonexistent')
        assert resp.status_code == 404

    def test_results_404_for_processing_job(self, client):
        """Results for in-progress job should return 404."""
        # Simulate a processing job
        import app as app_module
        app_module.jobs['test123'] = {'status': 'processing'}
        resp = client.get('/results/test123')
        assert resp.status_code == 404

    def test_results_200_for_error_job(self, client):
        """Results for error job should return 200 with error message."""
        import app as app_module
        app_module.jobs['err123'] = {'status': 'error', 'message': 'Test error'}
        resp = client.get('/results/err123')
        assert resp.status_code == 200
        assert b'Analysis Error' in resp.data


# ---------------------------------------------------------------------------
# Upload API
# ---------------------------------------------------------------------------

class TestUploadAPI:
    """Tests for the /upload endpoint."""

    def test_upload_no_file_returns_400(self, client):
        """Upload without file should return 400."""
        resp = client.post('/upload')
        assert resp.status_code == 400
        assert 'error' in resp.get_json()

    def test_upload_unsupported_format_returns_400(self, client):
        """Upload of unsupported file type should return 400."""
        data = {'mode': 'standing_no_brace', 'age_group': 'under15'}
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 400

    def test_upload_valid_image_returns_job_id(self, client, valid_test_image):
        """Valid image upload should return a job_id."""
        with open(valid_test_image, 'rb') as f:
            data = {
                'media': (f, 'test.jpg'),
                'mode': 'standing_no_brace',
                'age_group': 'under15'
            }
            resp = client.post('/upload', data=data, content_type='multipart/form-data')

        assert resp.status_code == 200
        json_data = resp.get_json()
        assert 'job_id' in json_data
        assert len(json_data['job_id']) == 8

    def test_upload_default_mode(self, client, valid_test_image):
        """Upload without mode should default to standing_no_brace."""
        with open(valid_test_image, 'rb') as f:
            data = {'media': (f, 'test.jpg')}
            resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 200

    def test_upload_default_age_group(self, client, valid_test_image):
        """Upload without age_group should default to under15."""
        with open(valid_test_image, 'rb') as f:
            data = {'media': (f, 'test.jpg'), 'mode': 'standing_no_brace'}
            resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Status API
# ---------------------------------------------------------------------------

class TestStatusAPI:
    """Tests for the /status/<job_id> endpoint."""

    def test_status_not_found(self, client):
        """Unknown job_id should return error."""
        resp = client.get('/status/nonexistent')
        assert resp.status_code == 200  # Flask returns 200 for this
        assert 'error' in resp.get_json()

    def test_status_processing(self, client):
        """Processing job should return processing status."""
        import app as app_module
        app_module.jobs['proc1'] = {'status': 'processing', 'progress': 0}
        resp = client.get('/status/proc1')
        assert resp.get_json()['status'] == 'processing'

    def test_status_done(self, client):
        """Done job should return done status with result."""
        import app as app_module
        app_module.jobs['done1'] = {'status': 'done', 'result': {'test': True}}
        resp = client.get('/status/done1')
        data = resp.get_json()
        assert data['status'] == 'done'
        assert data['result']['test'] is True


# ---------------------------------------------------------------------------
# Session API
# ---------------------------------------------------------------------------

class TestSessionAPI:
    """Tests for the /api/session/<job_id> endpoint."""

    def test_session_not_found(self, client):
        """Unknown session should return 404."""
        resp = client.get('/api/session/nonexistent')
        assert resp.status_code == 404

    def test_session_returns_json(self, client, sample_standing_result):
        """Existing session should return valid JSON."""
        import app as app_module
        with open(app_module.DB_PATH, 'a') as f:
            pass  # Ensure DB exists
        app_module.init_db()

        import sqlite3
        conn = sqlite3.connect(app_module.DB_PATH)
        conn.execute(
            'INSERT INTO sessions (job_id, created_at, mode, result_json) VALUES (?, ?, ?, ?)',
            ('test_s1', '2025-01-15T10:00:00', 'standing_no_brace',
             json.dumps(sample_standing_result))
        )
        conn.commit()
        conn.close()

        resp = client.get('/api/session/test_s1')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'success'
        assert 'metrics' in data


# ---------------------------------------------------------------------------
# Trends API
# ---------------------------------------------------------------------------

class TestTrendsAPI:
    """Tests for the /api/trends endpoint."""

    def test_trends_returns_json(self, client):
        """Trends endpoint should return valid JSON."""
        resp = client.get('/api/trends')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'status' in data

    def test_trends_insufficient_data(self, client):
        """With no sessions, should return insufficient_data."""
        resp = client.get('/api/trends')
        data = resp.get_json()
        assert data['status'] == 'insufficient_data'

    def test_trends_with_mode_filter(self, client):
        """Mode filter should be accepted."""
        resp = client.get('/api/trends?mode=standing_no_brace')
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Progression Report API
# ---------------------------------------------------------------------------

class TestProgressionReportAPI:
    """Tests for the /api/progression-report endpoint."""

    def test_returns_json(self, client):
        """Should return valid JSON."""
        resp = client.get('/api/progression-report')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'total_sessions' in data or 'status' in data


# ---------------------------------------------------------------------------
# PDF Report API
# ---------------------------------------------------------------------------

class TestPdfReportAPI:
    """Tests for the /api/pdf-report endpoint."""

    def test_returns_pdf(self, client):
        """Should return PDF binary data."""
        resp = client.get('/api/pdf-report')
        assert resp.status_code == 200
        assert resp.content_type == 'application/pdf'

    def test_pdf_starts_with_magic_bytes(self, client):
        """PDF should start with %PDF- header."""
        resp = client.get('/api/pdf-report')
        assert resp.data[:5] == b'%PDF-'

    def test_pdf_has_content_disposition(self, client):
        """Should have attachment disposition for download."""
        resp = client.get('/api/pdf-report')
        assert 'attachment' in resp.headers.get('Content-Disposition', '')


# ---------------------------------------------------------------------------
# Pressure Evaluation API
# ---------------------------------------------------------------------------

class TestPressureEvaluateAPI:
    """Tests for the /api/pressure/evaluate endpoint."""

    def test_optimal_pressure(self, client):
        """Optimal pressure readings should score 100."""
        payload = {
            'upper_support': 50.0,
            'middle_pressure': 60.0,
            'lower_support': 45.0,
            'skin_temp': 34.5
        }
        resp = client.post('/api/pressure/evaluate', json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['score'] == 100.0
        assert data['status'] == 'analyzed'

    def test_suboptimal_pressure(self, client):
        """Sub-optimal pressure should score < 100."""
        payload = {
            'upper_support': 20.0,
            'middle_pressure': 60.0,
            'lower_support': 45.0
        }
        resp = client.post('/api/pressure/evaluate', json=payload)
        data = resp.get_json()
        assert data['score'] < 100.0

    def test_invalid_payload_returns_400(self, client):
        """Missing required fields should return 400."""
        resp = client.post('/api/pressure/evaluate', json={'invalid': True})
        assert resp.status_code == 400

    def test_empty_body_returns_400(self, client):
        """Empty request body should return 400."""
        resp = client.post('/api/pressure/evaluate', json={})
        assert resp.status_code == 400

    def test_response_has_all_points(self, client):
        """Response should contain all 3 correction points."""
        payload = {
            'upper_support': 50.0,
            'middle_pressure': 60.0,
            'lower_support': 45.0
        }
        resp = client.post('/api/pressure/evaluate', json=payload)
        data = resp.get_json()
        assert set(data['points'].keys()) == {'upper_support', 'middle_pressure', 'lower_support'}


# ---------------------------------------------------------------------------
# Compliance API
# ---------------------------------------------------------------------------

class TestComplianceAPI:
    """Tests for compliance tracking endpoints."""

    def test_start_session(self, client):
        """Should create a new compliance session."""
        resp = client.post('/api/compliance/start', json={'session_id': 'integ_test_1'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['session_id'] == 'integ_test_1'
        assert data['status'] == 'started'

    def test_start_generates_session_id(self, client):
        """Should auto-generate session_id if not provided."""
        resp = client.post('/api/compliance/start', json={})
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'session_id' in data

    def test_log_reading(self, client):
        """Should log a pressure reading."""
        client.post('/api/compliance/start', json={'session_id': 'integ_test_2'})
        resp = client.post('/api/compliance/log', json={
            'session_id': 'integ_test_2',
            'upper_support': 50.0,
            'middle_pressure': 60.0,
            'lower_support': 45.0,
            'skin_temp': 34.5,
            'brace_detected': True
        })
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'logged'

    def test_log_without_session_id_returns_400(self, client):
        """Log without session_id should return 400."""
        resp = client.post('/api/compliance/log', json={'upper_support': 50})
        assert resp.status_code == 400

    def test_end_session(self, client):
        """Should end session and return summary."""
        client.post('/api/compliance/start', json={'session_id': 'integ_test_3'})
        resp = client.post('/api/compliance/end', json={'session_id': 'integ_test_3'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'total_wear_minutes' in data
        assert 'compliance_percentage' in data

    def test_end_without_session_id_returns_400(self, client):
        """End without session_id should return 400."""
        resp = client.post('/api/compliance/end', json={})
        assert resp.status_code == 400

    def test_compliance_summary(self, client):
        """Should return compliance summary for existing session."""
        client.post('/api/compliance/start', json={'session_id': 'integ_test_4'})
        resp = client.get('/api/compliance/summary/integ_test_4')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'compliance_percentage' in data

    def test_pressure_history(self, client):
        """Should return pressure reading history."""
        client.post('/api/compliance/start', json={'session_id': 'integ_test_5'})
        client.post('/api/compliance/log', json={
            'session_id': 'integ_test_5',
            'upper_support': 50.0, 'middle_pressure': 60.0, 'lower_support': 45.0,
            'skin_temp': 34.5, 'brace_detected': True
        })
        resp = client.get('/api/pressure/history/integ_test_5')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
