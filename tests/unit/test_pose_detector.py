"""
Unit tests for analysis/pose_detector.py

Tests the MediaPipe PoseLandmarker wrapper.
Note: These tests verify the interface and utility functions.
Full MediaPipe integration tests require the model file.
"""
import pytest
import numpy as np

from analysis.pose_detector import PoseDetector


class TestCalculateAngle:
    """Tests for the static angle calculation utility."""

    def test_right_angle(self):
        """90-degree angle should be detected."""
        a = [0, 0]
        b = [0, 0]
        c = [1, 0]
        # When a=b, the angle is undefined, but let's test with distinct points
        a = [0, 1]
        b = [0, 0]
        c = [1, 0]
        angle = PoseDetector.calculate_angle(a, b, c)
        assert abs(angle - 90.0) < 0.01

    def test_straight_line(self):
        """180-degree straight line."""
        a = [0, 0]
        b = [1, 0]
        c = [2, 0]
        angle = PoseDetector.calculate_angle(a, b, c)
        assert abs(angle - 180.0) < 0.01

    def test_zero_angle(self):
        """Overlapping points should give 0 or 360."""
        a = [1, 0]
        b = [0, 0]
        c = [1, 0]
        angle = PoseDetector.calculate_angle(a, b, c)
        assert angle == 0.0 or angle == 360.0

    def test_symmetric_angles(self):
        """Mirror configurations should give same absolute angle."""
        a1, b1, c1 = [0, 1], [0, 0], [1, 0]
        a2, b2, c2 = [0, 1], [0, 0], [-1, 0]
        angle1 = PoseDetector.calculate_angle(a1, b1, c1)
        angle2 = PoseDetector.calculate_angle(a2, b2, c2)
        assert abs(angle1 - angle2) < 0.01

    def test_angle_is_always_positive(self):
        """Angle should always be non-negative."""
        # Test multiple configurations
        points = [
            ([1, 0], [0, 0], [0, 1]),
            ([-1, 0], [0, 0], [0, -1]),
            ([3, 4], [0, 0], [-3, 4]),
        ]
        for a, b, c in points:
            angle = PoseDetector.calculate_angle(a, b, c)
            assert angle >= 0

    def test_angle_bounded_0_to_360(self):
        """Angle should always be in [0, 360]."""
        angle = PoseDetector.calculate_angle([1, 1], [0, 0], [-1, -1])
        assert 0 <= angle <= 360


class TestGetLandmarkCoords:
    """Tests for landmark coordinate conversion."""

    def test_normalizes_to_pixel_coords(self):
        """Normalized coords should be scaled to image dimensions."""
        class LM:
            def __init__(self): self.x = 0.5; self.y = 0.5; self.z = 0.0

        landmarks = [LM() for _ in range(33)]
        image_shape = (600, 400, 3)
        coords = PoseDetector.get_landmark_coords(landmarks, image_shape, 0)
        assert coords == [200, 300]  # 0.5 * 400, 0.5 * 600

    def test_top_left_origin(self):
        """(0,0) normalized should map to (0,0) pixels."""
        class LM:
            def __init__(self): self.x = 0.0; self.y = 0.0; self.z = 0.0

        landmarks = [LM() for _ in range(33)]
        coords = PoseDetector.get_landmark_coords(landmarks, (600, 400, 3), 0)
        assert coords == [0, 0]

    def test_bottom_right(self):
        """(1,1) normalized should map to (width, height) pixels."""
        class LM:
            def __init__(self): self.x = 1.0; self.y = 1.0; self.z = 0.0

        landmarks = [LM() for _ in range(33)]
        coords = PoseDetector.get_landmark_coords(landmarks, (600, 400, 3), 0)
        assert coords == [400, 600]

    def test_returns_integers(self):
        """Coordinates should be integers (pixel positions)."""
        class LM:
            def __init__(self): self.x = 0.333; self.y = 0.667; self.z = 0.0

        landmarks = [LM() for _ in range(33)]
        coords = PoseDetector.get_landmark_coords(landmarks, (600, 400, 3), 0)
        assert isinstance(coords[0], int)
        assert isinstance(coords[1], int)

    def test_landmark_index_selection(self):
        """Different landmark indices should select different landmarks."""
        class LM:
            def __init__(self, x, y): self.x = x; self.y = y; self.z = 0.0

        landmarks = [LM(0.1 * i, 0.1 * i) for i in range(33)]
        coords_0 = PoseDetector.get_landmark_coords(landmarks, (100, 100, 3), 0)
        coords_5 = PoseDetector.get_landmark_coords(landmarks, (100, 100, 3), 5)
        assert coords_0 != coords_5
