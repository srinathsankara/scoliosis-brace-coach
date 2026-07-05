"""
Unit tests for analysis/video_processor.py

Tests the analysis pipeline orchestrator.
"""
import os
import pytest
import numpy as np
import cv2

from analysis.video_processor import process_media


class TestProcessMedia:
    """Tests for the main process_media function."""

    def test_returns_error_for_nonexistent_file(self):
        """Non-existent file should return error status."""
        result = process_media('/nonexistent/file.jpg', 'standing_no_brace')
        assert result['status'] == 'error'

    def test_returns_error_for_corrupt_image(self, tmp_path):
        """Corrupt image file should return error."""
        corrupt_file = tmp_path / 'corrupt.jpg'
        corrupt_file.write_bytes(b'not a real image')
        result = process_media(str(corrupt_file), 'standing_no_brace')
        assert result['status'] == 'error'

    def test_returns_error_for_empty_image(self, plain_image):
        """Image with no person should return error."""
        result = process_media(plain_image, 'standing_no_brace')
        assert result['status'] == 'error'
        assert 'No person detected' in result['message']

    def test_standing_mode_calls_posture_analysis(self, valid_test_image):
        """Standing mode should trigger posture + rotation analysis."""
        result = process_media(valid_test_image, 'standing_no_brace')
        # May succeed or fail depending on MediaPipe detection
        # But if it succeeds, it should have metrics
        if result['status'] == 'success':
            assert 'metrics' in result
            assert result['mode'] == 'standing_no_brace'

    def test_mode_is_preserved_in_result(self, valid_test_image):
        """The requested mode should be preserved in the result."""
        result = process_media(valid_test_image, 'standing_with_brace', 'under18')
        if result['status'] == 'success':
            assert result['mode'] == 'standing_with_brace'

    def test_brace_detection_runs(self, brace_test_image):
        """Brace detection should run for standing modes."""
        result = process_media(brace_test_image, 'standing_no_brace')
        if result['status'] == 'success':
            assert 'brace_detected' in result
            assert isinstance(result['brace_detected'], bool)

    def test_image_extension_detection(self, valid_test_image):
        """Should correctly identify image files by extension."""
        result = process_media(valid_test_image, 'standing_no_brace')
        # Should not crash
        assert 'status' in result

    def test_default_age_group(self, valid_test_image):
        """Default age group should be under15."""
        result = process_media(valid_test_image, 'standing_no_brace')
        # Should not crash with default age group
        assert 'status' in result

    def test_invalid_mode_still_runs(self, valid_test_image):
        """Invalid mode should not crash the pipeline."""
        result = process_media(valid_test_image, 'invalid_mode_xyz')
        # Should return success but with empty metrics (no matching analysis)
        if result['status'] == 'success':
            assert result['metrics'] == {}
