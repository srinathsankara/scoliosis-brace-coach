"""
Unit tests for analysis/brace_detector.py

Tests HSV-based brace presence detection including:
- White brace detection
- No-brace detection
- Edge cases: dark image, uniform color, noisy image
"""
import pytest
import numpy as np
import cv2

from analysis.brace_detector import detect_brace


class TestDetectBrace:
    """Tests for the detect_brace function."""

    def test_returns_bool(self, valid_test_image):
        """Should always return a boolean."""
        image = cv2.imread(valid_test_image)
        result = detect_brace(image)
        assert isinstance(result, bool)

    def test_detects_white_brace(self, brace_test_image):
        """Image with large white torso region should detect brace."""
        image = cv2.imread(brace_test_image)
        result = detect_brace(image)
        assert result is True

    def test_no_brace_on_plain_clothing(self, valid_test_image):
        """Image without white torso region should not detect brace."""
        image = cv2.imread(valid_test_image)
        result = detect_brace(image)
        # The test image has skin-tone torso, not white
        assert result is False

    def test_all_white_image(self):
        """Completely white image has no edges, so brace detection returns False."""
        img = np.ones((600, 400, 3), dtype=np.uint8) * 255
        result = detect_brace(img)
        assert result is False

    def test_all_black_image(self):
        """Completely black image should not detect brace."""
        img = np.zeros((600, 400, 3), dtype=np.uint8)
        result = detect_brace(img)
        assert result is False

    def test_all_blue_image(self):
        """Image with no white should not detect brace."""
        img = np.full((600, 400, 3), (255, 0, 0), dtype=np.uint8)
        result = detect_brace(img)
        assert result is False

    def test_small_white_region_no_brace(self):
        """Small white patch (< 20% of torso) should not detect brace."""
        img = np.ones((600, 400, 3), dtype=np.uint8) * 100
        # Add small white square in torso area
        img[250:280, 180:220] = 255
        result = detect_brace(img)
        assert result is False

    def test_input_does_not_modify_image(self, valid_test_image):
        """The function should not modify the input image."""
        image = cv2.imread(valid_test_image)
        original = image.copy()
        detect_brace(image)
        np.testing.assert_array_equal(image, original)

    def test_grayscale_image_handled(self):
        """A grayscale image (single channel) should not crash."""
        img = np.ones((600, 400), dtype=np.uint8) * 200
        # The function expects BGR, but if passed grayscale it may error
        # This tests that we handle it gracefully or it raises a clear error
        try:
            result = detect_brace(img)
            assert isinstance(result, bool)
        except cv2.error:
            # Expected if function requires 3-channel input
            pass
