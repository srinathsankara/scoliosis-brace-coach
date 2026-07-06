"""
Shared test fixtures for the Scoliosis Brace Coach test suite.

Provides:
- Flask test client
- Temporary database isolation
- Mock pose landmarks
- Test image generation
- Database cleanup between tests
"""
import os
import sys
import sqlite3
import tempfile
import shutil
import numpy as np
import cv2
import pytest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Temporary directory isolation
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolate_workdir(tmp_path, monkeypatch):
    """
    Run every test in an isolated temp directory so databases, uploads,
    and model files never leak between tests or into the real project root.
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# Flask test client
# ---------------------------------------------------------------------------

@pytest.fixture
def app(tmp_path):
    """
    Create a fresh Flask application instance for each test.
    The app is configured for testing (no debug, temp DB paths).
    """
    from app import app as flask_app, init_db

    flask_app.config['TESTING'] = True
    flask_app.config['UPLOAD_FOLDER'] = str(tempfile.mkdtemp(prefix='uploads_'))
    flask_app.config['RESULTS_FOLDER'] = str(tempfile.mkdtemp(prefix='results_'))
    flask_app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB for tests

    os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(flask_app.config['RESULTS_FOLDER'], exist_ok=True)

    # Override DB paths to temp locations
    import app as app_module
    app_module.DB_PATH = str(tmp_path / 'sessions.db')
    app_module.jobs = {}

    init_db()

    yield flask_app

    # Cleanup
    shutil.rmtree(flask_app.config['UPLOAD_FOLDER'], ignore_errors=True)
    shutil.rmtree(flask_app.config['RESULTS_FOLDER'], ignore_errors=True)


@pytest.fixture
def client(app):
    """Flask test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI runner for testing commands."""
    return app.test_cli_runner()


# ---------------------------------------------------------------------------
# Test images
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_test_image(tmp_path):
    """
    Generate a realistic-ish test image with a human-like silhouette.
    MediaPipe needs actual body-like shapes to detect landmarks.
    This creates a gradient figure on a plain background.
    """
    img = np.ones((600, 400, 3), dtype=np.uint8) * 220

    # Skin-tone fill for body regions
    skin = (140, 160, 190)

    # Head
    cv2.ellipse(img, (200, 70), (25, 30), 0, 0, 360, skin, -1)
    # Neck
    cv2.rectangle(img, (192, 100), (208, 130), skin, -1)
    # Torso
    cv2.rectangle(img, (140, 130), (260, 340), skin, -1)
    # Left arm
    pts_l = np.array([[140, 140], [100, 200], [80, 300], [110, 310], [130, 210], [140, 170]], np.int32)
    cv2.fillPoly(img, [pts_l], skin)
    # Right arm
    pts_r = np.array([[260, 140], [300, 200], [320, 300], [290, 310], [270, 210], [260, 170]], np.int32)
    cv2.fillPoly(img, [pts_r], skin)
    # Left leg
    cv2.rectangle(img, (150, 340), (185, 560), skin, -1)
    # Right leg
    cv2.rectangle(img, (215, 340), (250, 560), skin, -1)

    path = tmp_path / 'test_person.jpg'
    cv2.imwrite(str(path), img)
    return str(path)


@pytest.fixture
def plain_image(tmp_path):
    """A plain white image with no body (should trigger 'No person detected')."""
    img = np.ones((400, 400, 3), dtype=np.uint8) * 255
    path = tmp_path / 'plain.jpg'
    cv2.imwrite(str(path), img)
    return str(path)


@pytest.fixture
def brace_test_image(tmp_path):
    """Image with white region in torso area to trigger brace detection."""
    img = np.ones((600, 400, 3), dtype=np.uint8) * 200

    skin = (140, 160, 190)
    brace_white = (250, 250, 250)

    # Head
    cv2.ellipse(img, (200, 70), (25, 30), 0, 0, 360, skin, -1)
    cv2.rectangle(img, (192, 100), (208, 130), skin, -1)
    # Torso with brace overlay (white)
    cv2.rectangle(img, (140, 130), (260, 340), brace_white, -1)
    # Arms and legs
    pts_l = np.array([[140, 140], [100, 200], [80, 300], [110, 310], [130, 210]], np.int32)
    cv2.fillPoly(img, [pts_l], skin)
    pts_r = np.array([[260, 140], [300, 200], [320, 300], [290, 310], [270, 210]], np.int32)
    cv2.fillPoly(img, [pts_r], skin)
    cv2.rectangle(img, (150, 340), (185, 560), skin, -1)
    cv2.rectangle(img, (215, 340), (250, 560), skin, -1)

    path = tmp_path / 'brace_person.jpg'
    cv2.imwrite(str(path), img)
    return str(path)


# ---------------------------------------------------------------------------
# Mock pose landmarks
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_landmarks():
    """
    Generate synthetic MediaPipe-style pose landmarks for a centered,
    upright person (no asymmetry). 33 landmarks with x, y, z in [0, 1].
    """
    class MockLandmark:
        def __init__(self, x, y, z=0.0):
            self.x = x
            self.y = y
            self.z = z

    landmarks = [MockLandmark(0.5, 0.5) for _ in range(33)]

    # Left shoulder (11)
    landmarks[11] = MockLandmark(0.42, 0.28)
    # Right shoulder (12)
    landmarks[12] = MockLandmark(0.58, 0.28)
    # Left elbow (13)
    landmarks[13] = MockLandmark(0.35, 0.40)
    # Right elbow (14)
    landmarks[14] = MockLandmark(0.65, 0.40)
    # Left wrist (15)
    landmarks[15] = MockLandmark(0.30, 0.52)
    # Right wrist (16)
    landmarks[16] = MockLandmark(0.70, 0.52)
    # Nose (0)
    landmarks[0] = MockLandmark(0.50, 0.12)
    # Left hip (23)
    landmarks[23] = MockLandmark(0.44, 0.55)
    # Right hip (24)
    landmarks[24] = MockLandmark(0.56, 0.55)
    # Left knee (25)
    landmarks[25] = MockLandmark(0.44, 0.72)
    # Right knee (26)
    landmarks[26] = MockLandmark(0.56, 0.72)
    # Left ankle (27)
    landmarks[27] = MockLandmark(0.44, 0.90)
    # Right ankle (28)
    landmarks[28] = MockLandmark(0.56, 0.90)

    return landmarks


@pytest.fixture
def asymmetric_landmarks():
    """
    Landmarks with deliberate asymmetry to trigger 'needs_improvement' status.
    Left shoulder higher than right, trunk lean to the left.
    """
    class MockLandmark:
        def __init__(self, x, y, z=0.0):
            self.x = x
            self.y = y
            self.z = z

    landmarks = [MockLandmark(0.5, 0.5) for _ in range(33)]

    # Shoulders: left closer to midline than right (asymmetric rib hump)
    landmarks[11] = MockLandmark(0.38, 0.22)
    landmarks[12] = MockLandmark(0.64, 0.34)
    landmarks[13] = MockLandmark(0.33, 0.38)
    landmarks[14] = MockLandmark(0.67, 0.44)
    landmarks[15] = MockLandmark(0.28, 0.52)
    landmarks[16] = MockLandmark(0.72, 0.54)
    landmarks[0] = MockLandmark(0.48, 0.12)
    # Hips: left higher than right
    landmarks[23] = MockLandmark(0.42, 0.50)
    landmarks[24] = MockLandmark(0.58, 0.58)
    landmarks[25] = MockLandmark(0.42, 0.72)
    landmarks[26] = MockLandmark(0.58, 0.72)
    landmarks[27] = MockLandmark(0.42, 0.90)
    landmarks[28] = MockLandmark(0.58, 0.90)

    return landmarks


@pytest.fixture
def image_shape():
    """Standard image dimensions for tests: 600 height x 400 width x 3 channels."""
    return (600, 400, 3)


# ---------------------------------------------------------------------------
# Sample analysis result (for DB population)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_standing_result():
    """A realistic standing analysis result dict."""
    return {
        'status': 'success',
        'mode': 'standing_no_brace',
        'brace_detected': False,
        'metrics': {
            'shoulder_asymmetry': 3.5,
            'hip_asymmetry': 2.1,
            'trunk_lean_angle': 1.8,
            'head_tilt': 2.0,
            'spine_deviation': 1.5,
            'arm_hang_diff': 1.2,
            'shoulder_status': 'good',
            'trunk_status': 'good',
            'rib_hump_proxy': 2.0,
            'rib_hump_status': 'good',
            'axillary_fold_diff': 1.5,
            'axillary_status': 'good',
            'trunk_rotation_angle': 1.2,
            'rotation_status': 'good',
            'trunk_offset': 0.8,
            'scapular_winging_diff': 1.0,
            'pelvic_obliquity': 1.5,
            'rotation_risk_score': 8.5
        }
    }


@pytest.fixture
def sample_braced_result():
    """A realistic braced standing analysis result (improved metrics)."""
    return {
        'status': 'success',
        'mode': 'standing_with_brace',
        'brace_detected': True,
        'metrics': {
            'shoulder_asymmetry': 1.2,
            'hip_asymmetry': 1.0,
            'trunk_lean_angle': 0.5,
            'head_tilt': 0.8,
            'spine_deviation': 0.3,
            'arm_hang_diff': 0.5,
            'shoulder_status': 'good',
            'trunk_status': 'good',
            'rib_hump_proxy': 0.8,
            'rib_hump_status': 'good',
            'axillary_fold_diff': 0.6,
            'axillary_status': 'good',
            'trunk_rotation_angle': 0.4,
            'rotation_status': 'good',
            'trunk_offset': 0.2,
            'scapular_winging_diff': 0.5,
            'pelvic_obliquity': 0.7,
            'rotation_risk_score': 2.1
        }
    }


def insert_test_session(db_path, job_id, result, mode='standing_no_brace'):
    """Helper to insert a session directly into the test database."""
    from datetime import datetime
    import json
    conn = sqlite3.connect(db_path)
    conn.execute(
        'INSERT INTO sessions (job_id, created_at, mode, result_json) VALUES (?, ?, ?, ?)',
        (job_id, datetime.now().isoformat(), mode, json.dumps(result))
    )
    conn.commit()
    conn.close()
