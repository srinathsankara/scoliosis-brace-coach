"""
Unit tests for analysis/exercise_rules.py

Tests Schroth exercise form analysis (currently placeholder).
"""
import pytest

from analysis.exercise_rules import analyze_exercise


class TestAnalyzeExercise:
    """Tests for the analyze_exercise function (placeholder)."""

    def test_returns_empty_dict_when_no_landmarks(self):
        """Empty landmarks should return empty dict."""
        result = analyze_exercise(None, (600, 400, 3))
        assert result == {}

    def test_returns_expected_keys(self, mock_landmarks, image_shape):
        """Should return exercise_form_score and feedback."""
        result = analyze_exercise(mock_landmarks, image_shape)
        assert 'exercise_form_score' in result
        assert 'feedback' in result

    def test_placeholder_returns_perfect_score(self, mock_landmarks, image_shape):
        """Placeholder should always return score of 100."""
        result = analyze_exercise(mock_landmarks, image_shape)
        assert result['exercise_form_score'] == 100

    def test_placeholder_returns_positive_feedback(self, mock_landmarks, image_shape):
        """Placeholder should return positive feedback string."""
        result = analyze_exercise(mock_landmarks, image_shape)
        assert isinstance(result['feedback'], str)
        assert len(result['feedback']) > 0

    def test_score_is_integer(self, mock_landmarks, image_shape):
        """Score should be an integer."""
        result = analyze_exercise(mock_landmarks, image_shape)
        assert isinstance(result['exercise_form_score'], int)
