"""
Back asymmetry analysis for scoliosis detection.

Uses image-level analysis to detect spinal curvature by measuring:
1. Left-right brightness asymmetry (rib hump causes one side to appear more prominent)
2. Contour analysis for spinal deviation
3. Pixel-level asymmetry in the back region

This supplements pose landmark analysis which only measures gross body asymmetry.
"""
import cv2
import numpy as np


def analyze_back_asymmetry(image, landmarks):
    """
    Analyze back image for scoliosis-related asymmetry using pixel-level analysis.
    
    Args:
        image: BGR image
        landmarks: MediaPipe pose landmarks (33 points)
    
    Returns:
        dict with asymmetry metrics
    """
    if landmarks is None or len(landmarks) < 33:
        return {}
    
    h, w = image.shape[:2]
    
    # Get key landmarks
    l_sh = (int(landmarks[11].x * w), int(landmarks[11].y * h))
    r_sh = (int(landmarks[12].x * w), int(landmarks[12].y * h))
    l_hip = (int(landmarks[23].x * w), int(landmarks[23].y * h))
    r_hip = (int(landmarks[24].x * w), int(landmarks[24].y * h))
    nose = (int(landmarks[0].x * w), int(landmarks[0].y * h))
    
    # Define the back region (torso area between shoulders and hips)
    mid_sh_x = (l_sh[0] + r_sh[0]) // 2
    mid_sh_y = (l_sh[1] + r_sh[1]) // 2
    mid_hip_x = (l_hip[0] + r_hip[0]) // 2
    mid_hip_y = (l_hip[1] + r_hip[1]) // 2
    
    # Bounding box for back region
    x_min = max(0, min(l_sh[0], l_hip[0]) - 10)
    x_max = min(w, max(r_sh[0], r_hip[0]) + 10)
    y_min = max(0, mid_sh_y - 20)
    y_max = min(h, mid_hip_y + 20)
    
    # Extract back region
    back_region = image[y_min:y_max, x_min:x_max]
    if back_region.size == 0:
        return {}
    
    gray = cv2.cvtColor(back_region, cv2.COLOR_BGR2GRAY)
    
    # --- Metric 1: Left-Right Brightness Asymmetry ---
    # Scoliosis causes one side of the back to be more prominent (rib hump)
    # which appears brighter in the image
    mid_x_in_region = mid_sh_x - x_min
    left_half = gray[:, :mid_x_in_region]
    right_half = gray[:, mid_x_in_region:]
    
    if left_half.size > 0 and right_half.size > 0:
        left_mean = np.mean(left_half)
        right_mean = np.mean(right_half)
        brightness_asymmetry = abs(left_mean - right_mean)
    else:
        brightness_asymmetry = 0
    
    # --- Metric 2: Contour-Based Spine Deviation ---
    # Find the midline of the back by analyzing vertical brightness profile
    # and measuring deviation from vertical
    midline_deviation = _measure_midline_deviation(gray, mid_x_in_region)
    
    # --- Metric 3: Texture Asymmetry ---
    # Scoliosis creates different textures on left vs right due to muscle imbalance
    texture_asymmetry = _measure_texture_asymmetry(gray, mid_x_in_region)
    
    # --- Metric 4: Edge Density Asymmetry ---
    # More prominent side may show different edge patterns
    edges = cv2.Canny(gray, 50, 150)
    edge_asymmetry = _measure_edge_asymmetry(edges, mid_x_in_region)
    
    # --- Metric 5: Vertical Profile Analysis ---
    # Analyze brightness along vertical midline to detect spinal curve
    spine_curve_score = _measure_spine_curve(gray, mid_x_in_region)
    
    # Combine into risk score (0-100, higher = more concerning)
    risk_score = 0
    if brightness_asymmetry > 5:
        risk_score += min(25, brightness_asymmetry * 1.5)
    if midline_deviation > 1:
        risk_score += min(25, midline_deviation * 5)
    if texture_asymmetry > 5:
        risk_score += min(20, texture_asymmetry * 0.8)
    if edge_asymmetry > 5:
        risk_score += min(15, edge_asymmetry * 0.6)
    if spine_curve_score > 1:
        risk_score += min(15, spine_curve_score * 3)
    
    return {
        'brightness_asymmetry': round(brightness_asymmetry, 2),
        'midline_deviation': round(midline_deviation, 2),
        'texture_asymmetry': round(texture_asymmetry, 2),
        'edge_asymmetry': round(edge_asymmetry, 2),
        'spine_curve_score': round(spine_curve_score, 2),
        'back_asymmetry_risk': round(min(100, risk_score), 1),
        'back_asymmetry_status': 'needs_improvement' if risk_score > 20 else 'good',
    }


def _measure_midline_deviation(gray, mid_x):
    """Measure how much the brightness midline deviates from vertical."""
    h, w = gray.shape
    
    # Sample horizontal brightness profiles at different heights
    deviations = []
    for y in range(h // 4, 3 * h // 4, max(1, h // 10)):
        row = gray[y, :]
        # Find the center of brightness in this row
        if np.sum(row) > 0:
            center_of_mass = np.average(np.arange(len(row)), weights=row.astype(float))
            deviation = abs(center_of_mass - mid_x)
            deviations.append(deviation)
    
    # Also measure standard deviation of deviations (consistency of curve)
    if len(deviations) > 2:
        mean_dev = np.mean(deviations)
        # A curved spine shows consistent offset in one direction
        directional_deviations = [d - mean_dev for d in deviations]
        curve_consistency = abs(np.mean(directional_deviations))
        return mean_dev + curve_consistency * 0.5
    
    return np.mean(deviations) if deviations else 0


def _measure_texture_asymmetry(gray, mid_x):
    """Measure texture differences between left and right halves."""
    h, w = gray.shape
    
    left = gray[:, :mid_x] if mid_x > 0 else gray[:, :1]
    right = gray[:, mid_x:] if mid_x < w else gray[:, w-1:]
    
    if left.size == 0 or right.size == 0:
        return 0
    
    # Use Laplacian variance as texture measure
    left_texture = cv2.Laplacian(left, cv2.CV_64F).var()
    right_texture = cv2.Laplacian(right, cv2.CV_64F).var()
    
    return abs(left_texture - right_texture)


def _measure_edge_asymmetry(edges, mid_x):
    """Measure edge density asymmetry between left and right halves."""
    h, w = edges.shape
    
    left = edges[:, :mid_x] if mid_x > 0 else edges[:, :1]
    right = edges[:, mid_x:] if mid_x < w else edges[:, w-1:]
    
    if left.size == 0 or right.size == 0:
        return 0
    
    left_density = np.mean(left)
    right_density = np.mean(right)
    
    return abs(left_density - right_density)


def _measure_spine_curve(gray, mid_x):
    """Analyze the vertical brightness profile to detect spinal curve."""
    h, w = gray.shape
    
    # Sample brightness along vertical strips near the midline
    strip_width = max(5, w // 10)
    left_strip = gray[:, max(0, mid_x - strip_width):mid_x]
    right_strip = gray[:, mid_x:min(w, mid_x + strip_width)]
    
    if left_strip.size == 0 or right_strip.size == 0:
        return 0
    
    # Compare vertical profiles
    left_profile = np.mean(left_strip, axis=1)
    right_profile = np.mean(right_strip, axis=1)
    
    # A curved spine creates a systematic difference in the profiles
    diff_profile = left_profile - right_profile
    
    # Look for consistent offset (not random noise)
    mean_diff = np.mean(diff_profile)
    std_diff = np.std(diff_profile)
    
    # Score based on consistent asymmetry
    if std_diff > 0:
        consistency = abs(mean_diff) / (std_diff + 1e-6)
    else:
        consistency = 0
    
    # Also look for systematic change along the vertical axis
    # A curved spine shows a gradient in the difference profile
    if len(diff_profile) > 10:
        # Fit a line to the difference profile
        x = np.arange(len(diff_profile))
        if np.std(x) > 0:
            slope = np.polyfit(x, diff_profile, 1)[0]
            curve_gradient = abs(slope) * len(diff_profile)
        else:
            curve_gradient = 0
    else:
        curve_gradient = 0
    
    return consistency * abs(mean_diff) + curve_gradient * 0.3
