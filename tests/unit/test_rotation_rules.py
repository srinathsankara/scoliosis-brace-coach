"""
Unit tests for analysis/rotation_rules.py

Tests trunk rotation and rib hump estimation including:
- Symmetric rotation metrics
- Asymmetric rotation metrics
- Risk score computation
- Age-group threshold differentiation
- Edge cases
"""
import pytest
import numpy as np

from analysis.rotation_rules import analyze_rotation, ROTATION_THRESHOLDS


class TestAnalyzeRotation:
    """Tests for the main analyze_rotation function."""

    def test_returns_empty_dict_when_no_landmarks(self):
        """Empty landmarks should return an empty dict."""
        result = analyze_rotation(None, (600, 400, 3))
        assert result == {}

    def test_returns_all_expected_keys(self, mock_landmarks, image_shape):
        """Result should contain all 10 expected metric keys."""
        result = analyze_rotation(mock_landmarks, image_shape)
        expected_keys = {
            'rib_hump_proxy', 'rib_hump_status',
            'axillary_fold_diff', 'axillary_status',
            'trunk_rotation_angle', 'rotation_status',
            'trunk_offset', 'scapular_winging_diff',
            'pelvic_obliquity', 'rotation_risk_score'
        }
        assert set(result.keys()) == expected_keys

    def test_symmetric_rotation_all_good(self, mock_landmarks, image_shape):
        """Symmetric landmarks should produce 'good' rotation status."""
        result = analyze_rotation(mock_landmarks, image_shape)
        assert result['rib_hump_status'] == 'good'
        assert result['axillary_status'] == 'good'
        assert result['rotation_status'] == 'good'

    def test_asymmetric_rotation_detected(self, asymmetric_landmarks, image_shape):
        """Asymmetric landmarks should trigger rotation issues."""
        result = analyze_rotation(asymmetric_landmarks, image_shape)
        # The asymmetric fixture has left shoulder higher than right
        assert result['rib_hump_proxy'] > 0
        assert result['axillary_fold_diff'] > 0

    def test_risk_score_is_bounded(self, mock_landmarks, image_shape):
        """Risk score should always be between 0 and 100."""
        result = analyze_rotation(mock_landmarks, image_shape)
        assert 0 <= result['rotation_risk_score'] <= 100

    def test_risk_score_increases_with_asymmetry(self, mock_landmarks, asymmetric_landmarks, image_shape):
        """More asymmetric landmarks should produce a higher risk score."""
        result_symmetric = analyze_rotation(mock_landmarks, image_shape)
        result_asymmetric = analyze_rotation(asymmetric_landmarks, image_shape)
        assert result_asymmetric['rotation_risk_score'] > result_symmetric['rotation_risk_score']

    def test_metrics_are_non_negative(self, mock_landmarks, image_shape):
        """All rotation metrics should be non-negative."""
        result = analyze_rotation(mock_landmarks, image_shape)
        assert result['rib_hump_proxy'] >= 0
        assert result['axillary_fold_diff'] >= 0
        assert result['trunk_rotation_angle'] >= 0
        assert result['scapular_winging_diff'] >= 0
        assert result['pelvic_obliquity'] >= 0

    def test_trunk_rotation_angle_is_degrees(self, mock_landmarks, image_shape):
        """Rotation angle should be in degrees (0-180 range)."""
        result = analyze_rotation(mock_landmarks, image_shape)
        assert 0 <= result['trunk_rotation_angle'] <= 180


class TestRotationThresholds:
    """Tests for age-group-specific rotation thresholds."""

    @pytest.mark.parametrize("age_group", ['under12', 'under15', 'under18', 'adult'])
    def test_all_age_groups_accepted(self, asymmetric_landmarks, image_shape, age_group):
        """All valid age groups should be processed without error."""
        result = analyze_rotation(asymmetric_landmarks, image_shape, age_group=age_group)
        assert 'rotation_risk_score' in result

    def test_threshold_values_are_sane(self):
        """Verify rotation threshold values are within reasonable bounds."""
        for group, thresholds in ROTATION_THRESHOLDS.items():
            assert 2 <= thresholds['rib_hump'] <= 15
            assert 2 <= thresholds['axillary_diff'] <= 12
            assert 1 <= thresholds['rotation_angle'] <= 10

    def test_younger_thresholds_are_stricter(self):
        """Under-12 rotation thresholds should be stricter than adult."""
        assert ROTATION_THRESHOLDS['under12']['rib_hump'] < ROTATION_THRESHOLDS['adult']['rib_hump']
        assert ROTATION_THRESHOLDS['under12']['rotation_angle'] <= ROTATION_THRESHOLDS['adult']['rotation_angle']


class TestRotationEdgeCases:
    """Edge case tests for rotation computation."""

    def test_identical_shoulder_and_hip_lines(self):
        """When shoulder and hip lines are parallel, rotation angle should be 0."""
        class LM:
            def __init__(self, x, y): self.x = x; self.y = y; self.z = 0.0
        landmarks = [LM(0.5, 0.5) for _ in range(33)]
        # Perfectly symmetric
        landmarks[11] = LM(0.42, 0.28)
        landmarks[12] = LM(0.58, 0.28)
        landmarks[23] = LM(0.44, 0.55)
        landmarks[24] = LM(0.56, 0.55)
        landmarks[13] = LM(0.35, 0.40)
        landmarks[14] = LM(0.65, 0.40)
        landmarks[25] = LM(0.44, 0.72)
        landmarks[26] = LM(0.56, 0.72)

        result = analyze_rotation(landmarks, (600, 400, 3))
        assert result['trunk_rotation_angle'] == 0.0

    def test_max_rotation_risk_score(self):
        """Extremely asymmetric landmarks should approach risk score of 100."""
        class LM:
            def __init__(self, x, y): self.x = x; self.y = y; self.z = 0.0
        landmarks = [LM(0.5, 0.5) for _ in range(33)]
        # Extreme asymmetry: shoulders visibly rotated from hip midline
        landmarks[11] = LM(0.10, 0.0)   # Left shoulder very far left
        landmarks[12] = LM(0.85, 1.0)   # Right shoulder less far right
        landmarks[13] = LM(0.05, 0.1)
        landmarks[14] = LM(0.95, 0.9)
        landmarks[23] = LM(0.45, 0.55)
        landmarks[24] = LM(0.55, 0.55)
        landmarks[25] = LM(0.44, 0.72)
        landmarks[26] = LM(0.56, 0.72)

        result = analyze_rotation(landmarks, (600, 400, 3))
        assert result['rotation_risk_score'] > 50
