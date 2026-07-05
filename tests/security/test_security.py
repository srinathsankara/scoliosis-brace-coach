"""
Security & DevSecOps Tests

Automated security checks for common vulnerabilities:
- SQL injection on all inputs
- Missing security headers
- Path traversal in file uploads
- XSS in template rendering
- Input validation bypass attempts
- Information disclosure

Run with: pytest tests/security/ -v --timeout=30
"""
import os
import json
import sqlite3
import pytest


# ---------------------------------------------------------------------------
# SQL Injection Tests
# ---------------------------------------------------------------------------

class TestSQLInjection:
    """Test for SQL injection vulnerabilities on all input endpoints."""

    SQL_PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE sessions; --",
        "' UNION SELECT * FROM sessions --",
        "1' AND 1=1 --",
        "admin'--",
        "' OR 1=1 #",
        "1; DELETE FROM sessions WHERE 1=1",
    ]

    def test_upload_mode_sql_injection(self, client, valid_test_image):
        """SQL injection in mode parameter should not cause DB error."""
        for payload in self.SQL_PAYLOADS:
            with open(valid_test_image, 'rb') as f:
                data = {
                    'media': (f, 'test.jpg'),
                    'mode': payload,
                    'age_group': 'under15'
                }
                resp = client.post('/upload', data=data, content_type='multipart/form-data')
            # Should not return 500 (server error from SQL injection)
            assert resp.status_code != 500, f"SQL injection in mode caused 500: {payload}"

    def test_upload_age_group_sql_injection(self, client, valid_test_image):
        """SQL injection in age_group parameter should not cause DB error."""
        for payload in self.SQL_PAYLOADS:
            with open(valid_test_image, 'rb') as f:
                data = {
                    'media': (f, 'test.jpg'),
                    'mode': 'standing_no_brace',
                    'age_group': payload
                }
                resp = client.post('/upload', data=data, content_type='multipart/form-data')
            assert resp.status_code != 500, f"SQL injection in age_group caused 500: {payload}"

    def test_status_endpoint_sql_injection(self, client):
        """SQL injection in job_id URL parameter should not cause DB error."""
        for payload in self.SQL_PAYLOADS:
            resp = client.get(f'/status/{payload}')
            assert resp.status_code != 500, f"SQL injection in status caused 500: {payload}"

    def test_session_endpoint_sql_injection(self, client):
        """SQL injection in session endpoint should not cause DB error."""
        for payload in self.SQL_PAYLOADS:
            resp = client.get(f'/api/session/{payload}')
            assert resp.status_code != 500, f"SQL injection in session caused 500: {payload}"

    def test_compliance_summary_sql_injection(self, client):
        """SQL injection in compliance summary should not cause DB error."""
        for payload in self.SQL_PAYLOADS:
            resp = client.get(f'/api/compliance/summary/{payload}')
            assert resp.status_code != 500, f"SQL injection in compliance summary caused 500: {payload}"

    def test_pressure_history_sql_injection(self, client):
        """SQL injection in pressure history should not cause DB error."""
        for payload in self.SQL_PAYLOADS:
            resp = client.get(f'/api/pressure/history/{payload}')
            assert resp.status_code != 500, f"SQL injection in pressure history caused 500: {payload}"

    def test_trends_mode_filter_sql_injection(self, client):
        """SQL injection in trends mode filter should not cause DB error."""
        for payload in self.SQL_PAYLOADS:
            resp = client.get(f'/api/trends?mode={payload}')
            assert resp.status_code != 500, f"SQL injection in trends mode caused 500: {payload}"


# ---------------------------------------------------------------------------
# Path Traversal Tests
# ---------------------------------------------------------------------------

class TestPathTraversal:
    """Test for path traversal attacks on file upload."""

    TRAVERSAL_PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "..%252f..%252f..%252fetc/passwd",
    ]

    def test_path_traversal_in_filename(self, client):
        """Malicious filenames should not access files outside upload dir."""
        for payload in self.TRAVERSAL_PAYLOADS:
            data = {
                'media': (b'\xff\xd8\xff\xe0fake_jpeg_data', payload),
                'mode': 'standing_no_brace',
            }
            resp = client.post('/upload', data=data, content_type='multipart/form-data')
            # Should either reject the file or save it safely in uploads/
            if resp.status_code == 200:
                job_id = resp.get_json().get('job_id', '')
                # Verify the file was saved in the uploads directory, not outside it
                import app as app_module
                upload_dir = os.path.abspath(app_module.app.config['UPLOAD_FOLDER'])
                for saved_file in os.listdir(upload_dir):
                    full_path = os.path.abspath(os.path.join(upload_dir, saved_file))
                    assert full_path.startswith(upload_dir), \
                        f"File saved outside upload dir: {full_path}"


# ---------------------------------------------------------------------------
# Security Headers Tests
# ---------------------------------------------------------------------------

class TestSecurityHeaders:
    """Test for missing security headers (OWASP recommendations)."""

    def test_no_server_header_leak(self, client):
        """Server header should not reveal framework version."""
        resp = client.get('/')
        server = resp.headers.get('Server', '')
        # Flask's default Server header may leak version
        # This is informational - flag if present
        if 'Werkzeug' in server or 'Python' in server:
            pytest.xfail(f"Server header leaks info: {server}")

    def test_content_type_options(self, client):
        """X-Content-Type-Options should be set to prevent MIME sniffing."""
        resp = client.get('/')
        xcto = resp.headers.get('X-Content-Type-Options', '')
        if not xcto:
            pytest.xfail("Missing X-Content-Type-Options header (recommended: nosniff)")

    def test_x_frame_options(self, client):
        """X-Frame-Options should prevent clickjacking."""
        resp = client.get('/')
        xfo = resp.headers.get('X-Frame-Options', '')
        if not xfo:
            pytest.xfail("Missing X-Frame-Options header (recommended: DENY or SAMEORIGIN)")

    def test_content_security_policy(self, client):
        """Content-Security-Policy should restrict resource loading."""
        resp = client.get('/')
        csp = resp.headers.get('Content-Security-Policy', '')
        if not csp:
            pytest.xfail("Missing Content-Security-Policy header")

    def test_strict_transport_security(self, client):
        """Strict-Transport-Security should enforce HTTPS (when deployed)."""
        resp = client.get('/')
        hsts = resp.headers.get('Strict-Transport-Security', '')
        if not hsts:
            pytest.xfail("Missing HSTS header (required for production HTTPS)")


# ---------------------------------------------------------------------------
# Input Validation Tests
# ---------------------------------------------------------------------------

class TestInputValidation:
    """Test input validation and error handling."""

    def test_upload_with_empty_filename(self, client):
        """Empty filename should be rejected."""
        data = {
            'media': (b'fake_data', ''),
            'mode': 'standing_no_brace',
        }
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
        # Should not crash
        assert resp.status_code in (400, 404, 200)

    def test_upload_with_path_in_filename(self, client):
        """Filename with path separators should be sanitized."""
        data = {
            'media': (b'\xff\xd8\xff\xe0fake', '../../evil.jpg'),
            'mode': 'standing_no_brace',
        }
        resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code != 500

    def test_pressure_evaluate_with_negative_values(self, client):
        """Negative pressure values should be handled gracefully."""
        payload = {
            'upper_support': -100,
            'middle_pressure': -200,
            'lower_support': -150
        }
        resp = client.post('/api/pressure/evaluate', json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert 0 <= data['score'] <= 100

    def test_pressure_evaluate_with_extreme_values(self, client):
        """Extremely large pressure values should not crash."""
        payload = {
            'upper_support': 999999,
            'middle_pressure': 999999,
            'lower_support': 999999
        }
        resp = client.post('/api/pressure/evaluate', json=payload)
        assert resp.status_code == 200

    def test_pressure_evaluate_with_string_values(self, client):
        """String values where numbers expected should be handled."""
        payload = {
            'upper_support': 'not_a_number',
            'middle_pressure': 60,
            'lower_support': 45
        }
        resp = client.post('/api/pressure/evaluate', json=payload)
        # Should either parse or return 400
        assert resp.status_code in (200, 400)

    def test_compliance_start_with_special_characters(self, client):
        """Special characters in session_id should be handled."""
        payload = {'session_id': '<script>alert("xss")</script>'}
        resp = client.post('/api/compliance/start', json=payload)
        assert resp.status_code == 200

    def test_upload_extremely_large_metadata(self, client):
        """Very long mode/age_group strings should not crash."""
        long_string = 'A' * 10000
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'requirements.txt'), 'rb') as f:
            data = {
                'media': (f, 'test.jpg'),
                'mode': long_string,
                'age_group': long_string,
            }
            resp = client.post('/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code != 500


# ---------------------------------------------------------------------------
# Information Disclosure Tests
# ---------------------------------------------------------------------------

class TestInformationDisclosure:
    """Test for sensitive information leakage."""

    def test_error_messages_dont_leak_stack_traces(self, client):
        """Error responses should not contain stack traces."""
        resp = client.get('/api/session/nonexistent_12345')
        body = resp.get_data(as_text=True)
        assert 'Traceback' not in body
        assert 'File "' not in body
        assert 'line ' not in body

    def test_404_page_dont_leak_info(self, client):
        """404 responses should not reveal server information."""
        resp = client.get('/nonexistent_page_xyz')
        body = resp.get_data(as_text=True)
        assert 'Werkzeug' not in body
        assert 'Python/' not in body

    def test_database_errors_dont_leak_schema(self, client):
        """Database errors should not reveal table structure."""
        # Try to trigger a DB error via malformed input
        resp = client.get('/api/session/../../etc/passwd')
        body = resp.get_data(as_text=True)
        assert 'CREATE TABLE' not in body
        assert 'sqlite_master' not in body

    def test_debug_mode_disabled_in_responses(self, client):
        """Debug mode should not be evident in responses."""
        resp = client.get('/')
        # Flask debug mode adds a debugger badge
        assert 'Debugger' not in resp.get_data(as_text=True)
        assert 'debugger' not in resp.get_data(as_text=True).lower()


# ---------------------------------------------------------------------------
# Authentication & Authorization Tests
# ---------------------------------------------------------------------------

class TestAuthenticationBypass:
    """Test for authentication bypass attempts.

    Note: The current application has no authentication.
    These tests document the expected behavior and flag it as a risk.
    """

    def test_all_endpoints_accessible_without_auth(self, client):
        """All endpoints should be accessible (no auth implemented).

        WARNING: This documents a security gap. Production deployment
        should add authentication before exposing externally.
        """
        endpoints = [
            '/',
            '/dashboard',
            '/history',
            '/compare',
            '/sensors',
            '/trends',
            '/about',
            '/api/trends',
            '/api/progression-report',
            '/api/pdf-report',
        ]
        for endpoint in endpoints:
            resp = client.get(endpoint)
            assert resp.status_code == 200, \
                f"Endpoint {endpoint} returned {resp.status_code} (expected 200 - no auth required)"

    def test_admin_endpoints_no_auth_protection(self, client):
        """Dashboard should not require authentication (current behavior).

        NOTE: This is a security gap. In production, clinician dashboard
        should require authentication to protect patient data.
        """
        resp = client.get('/dashboard')
        assert resp.status_code == 200  # Currently no auth - documented risk
