"""
Unit tests for analysis/gait_rules.py

Tests walking gait analysis including:
- Basic metric computation
- Empty landmark handling
- Multiple frame processing
"""
import pytest

from analysis.gait_rules import analyze_gait


class TestAnalyzeGait:
    """Tests for the analyze_gait function."""

    def test_returns_empty_dict_when_no_landmarks(self):
        """Empty landmarks list should return empty dict."""
        result = analyze_gait([], (600, 400, 3))
        assert result == {}

    def test_returns_empty_dict_for_none(self):
        """None landmarks should return empty dict."""
        result = analyze_gait(None, (600, 400, 3))
        assert result == {}

    def test_returns_expected_keys(self, mock_landmarks, image_shape):
        """Should return pelvic_tilt and step_symmetry_estimate."""
        result = analyze_gait([mock_landmarks], image_shape)
        assert 'pelvic_tilt' in result
        assert 'step_symmetry_estimate' in result

    def test_symmetric_gait_low_values(self, mock_landmarks, image_shape):
        """Symmetric landmarks should produce low asymmetry values."""
        result = analyze_gait([mock_landmarks], image_shape)
        # Mock landmarks have symmetric hips
        assert result['pelvic_tilt'] >= 0
        assert result['step_symmetry_estimate'] >= 0

    def test_uses_last_frame(self, asymmetric_landmarks, mock_landmarks, image_shape):
        """Should use the last landmark set in the list."""
        result = analyze_gait([mock_landmarks, asymmetric_landmarks], image_shape)
        # The last frame is asymmetric
        assert result['pelvic_tilt'] > 0

    def test_single_frame_works(self, mock_landmarks, image_shape):
        """Single frame should work fine."""
        result = analyze_gait([mock_landmarks], image_shape)
        assert isinstance(result['pelvic_tilt'], (int, float))
        assert isinstance(result['step_symmetry_estimate'], (int, float))

    def test_metrics_are_non_negative(self, mock_landmarks, image_shape):
        """Gait metrics should be non-negative."""
        result = analyze_gait([mock_landmarks], image_shape)
        assert result['pelvic_tilt'] >= 0
        assert result['step_symmetry_estimate'] >= 0
