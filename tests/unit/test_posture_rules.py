"""
Unit tests for analysis/posture_rules.py

Tests the standing posture analysis pipeline including:
- Symmetric (good) posture metrics
- Asymmetric (needs_improvement) posture metrics
- Edge cases: empty landmarks, single landmark, extreme values
- Age-group threshold differentiation
"""
import pytest
import numpy as np

from analysis.posture_rules import analyze_posture, AGE_THRESHOLDS


class TestAnalyzePosture:
    """Tests for the main analyze_posture function."""

    def test_returns_empty_dict_when_no_landmarks(self):
        """Empty landmarks should return an empty dict, not crash."""
        result = analyze_posture(None, (600, 400, 3))
        assert result == {}

    def test_returns_empty_dict_for_empty_list(self):
        """Empty list of landmarks should return an empty dict."""
        result = analyze_posture([], (600, 400, 3))
        assert result == {}

    def test_returns_all_expected_keys(self, mock_landmarks, image_shape):
        """Result should contain all 8 expected metric keys."""
        result = analyze_posture(mock_landmarks, image_shape)
        expected_keys = {
            'shoulder_asymmetry', 'hip_asymmetry', 'trunk_lean_angle',
            'head_tilt', 'spine_deviation', 'arm_hang_diff',
            'shoulder_status', 'trunk_status'
        }
        assert set(result.keys()) == expected_keys

    def test_symmetric_posture_all_good(self, mock_landmarks, image_shape):
        """A perfectly symmetric posture should have 'good' status for all."""
        result = analyze_posture(mock_landmarks, image_shape)
        assert result['shoulder_status'] == 'good'
        assert result['trunk_status'] == 'good'

    def test_asymmetric_posture_detected(self, asymmetric_landmarks, image_shape):
        """Asymmetric landmarks should trigger 'needs_improvement' status."""
        result = analyze_posture(asymmetric_landmarks, image_shape)
        # Left shoulder Y=0.22, Right shoulder Y=0.34 -> diff = 0.12 * 600 = 72px
        # This exceeds all age thresholds
        assert result['shoulder_status'] == 'needs_improvement'
        assert result['shoulder_asymmetry'] > 0

    def test_metrics_are_numeric(self, mock_landmarks, image_shape):
        """All numeric metrics should be float or int, not strings or None."""
        result = analyze_posture(mock_landmarks, image_shape)
        for key in ['shoulder_asymmetry', 'hip_asymmetry', 'trunk_lean_angle',
                     'head_tilt', 'spine_deviation', 'arm_hang_diff']:
            assert isinstance(result[key], (int, float)), f"{key} should be numeric"
            assert not np.isnan(result[key]), f"{key} should not be NaN"

    def test_trunk_angle_is_non_negative(self, mock_landmarks, image_shape):
        """Trunk lean angle should always be >= 0 (absolute value)."""
        result = analyze_posture(mock_landmarks, image_shape)
        assert result['trunk_lean_angle'] >= 0

    def test_asymmetry_metrics_are_non_negative(self, asymmetric_landmarks, image_shape):
        """Asymmetry values should be absolute differences, always >= 0."""
        result = analyze_posture(asymmetric_landmarks, image_shape)
        assert result['shoulder_asymmetry'] >= 0
        assert result['hip_asymmetry'] >= 0
        assert result['arm_hang_diff'] >= 0

    def test_default_age_group_is_under15(self, mock_landmarks, image_shape):
        """Without specifying age_group, should use 'under15' thresholds."""
        result_default = analyze_posture(mock_landmarks, image_shape)
        result_explicit = analyze_posture(mock_landmarks, image_shape, age_group='under15')
        assert result_default == result_explicit


class TestAgeGroupThresholds:
    """Tests for age-group-specific threshold application."""

    @pytest.mark.parametrize("age_group", ['under12', 'under15', 'under18', 'adult'])
    def test_valid_age_groups_accepted(self, asymmetric_landmarks, image_shape, age_group):
        """All four valid age groups should be accepted without error."""
        result = analyze_posture(asymmetric_landmarks, image_shape, age_group=age_group)
        assert 'shoulder_status' in result
        assert 'trunk_status' in result

    def test_stricter_thresholds_for_younger_patients(self, asymmetric_landmarks, image_shape):
        """Under-12 should have stricter thresholds, so more likely to flag issues."""
        result_young = analyze_posture(asymmetric_landmarks, image_shape, age_group='under12')
        result_adult = analyze_posture(asymmetric_landmarks, image_shape, age_group='adult')
        # Both use same landmarks, but under12 has lower threshold
        # The asymmetric landmarks have large enough asymmetry that both should flag
        assert result_young['shoulder_asymmetry'] == result_adult['shoulder_asymmetry']
        # But thresholds differ - under12 should be stricter
        assert AGE_THRESHOLDS['under12']['shoulder_diff'] < AGE_THRESHOLDS['adult']['shoulder_diff']

    def test_unknown_age_group_falls_back_to_under15(self, mock_landmarks, image_shape):
        """Unknown age group should fall back to under15 thresholds."""
        result_unknown = analyze_posture(mock_landmarks, image_shape, age_group='nonexistent')
        result_known = analyze_posture(mock_landmarks, image_shape, age_group='under15')
        assert result_unknown == result_known

    def test_threshold_values_are_sane(self):
        """Verify threshold configuration values are within reasonable bounds."""
        for group, thresholds in AGE_THRESHOLDS.items():
            assert 5 <= thresholds['shoulder_diff'] <= 30, f"{group} shoulder_diff out of range"
            assert 1.0 <= thresholds['trunk_angle'] <= 8.0, f"{group} trunk_angle out of range"

    def test_younger_thresholds_are_stricter(self):
        """Under-12 thresholds should be stricter (lower) than adult thresholds."""
        assert AGE_THRESHOLDS['under12']['shoulder_diff'] < AGE_THRESHOLDS['adult']['shoulder_diff']
        assert AGE_THRESHOLDS['under12']['trunk_angle'] < AGE_THRESHOLDS['adult']['trunk_angle']


class TestPostureEdgeCases:
    """Edge case tests for unusual landmark configurations."""

    def test_all_landmarks_at_origin(self):
        """Landmarks all at (0,0) should not crash, just produce extreme values."""
        class LM:
            def __init__(self): self.x = 0.0; self.y = 0.0; self.z = 0.0
        landmarks = [LM() for _ in range(33)]
        result = analyze_posture(landmarks, (600, 400, 3))
        assert isinstance(result, dict)
        # All at origin means no asymmetry (all zero)
        assert result['shoulder_asymmetry'] == 0
        assert result['hip_asymmetry'] == 0

    def test_extreme_asymmetry(self):
        """One shoulder at top, one at bottom - should produce max asymmetry."""
        class LM:
            def __init__(self, x, y): self.x = x; self.y = y; self.z = 0.0
        landmarks = [LM(0.5, 0.5) for _ in range(33)]
        landmarks[11] = LM(0.4, 0.0)   # Left shoulder at very top
        landmarks[12] = LM(0.6, 1.0)   # Right shoulder at very bottom
        landmarks[23] = LM(0.44, 0.55)
        landmarks[24] = LM(0.56, 0.55)
        landmarks[0] = LM(0.5, 0.12)
        landmarks[27] = LM(0.44, 0.90)
        landmarks[28] = LM(0.56, 0.90)
        landmarks[15] = LM(0.3, 0.52)
        landmarks[16] = LM(0.7, 0.52)

        result = analyze_posture(landmarks, (600, 400, 3))
        assert result['shoulder_asymmetry'] > 100  # Very large pixel difference
        assert result['shoulder_status'] == 'needs_improvement'
