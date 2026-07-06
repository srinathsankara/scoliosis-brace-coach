import cv2
import numpy as np

def detect_brace(image):
    """Detect if a brace is present in the image using color and contour analysis."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    h, w, _ = image.shape
    
    # White/light brace colors
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Define full torso region
    torso_top = int(h * 0.25)
    torso_bot = int(h * 0.75)
    torso_left = int(w * 0.15)
    torso_right = int(w * 0.85)
    
    # Brace should appear across the CENTER of the torso, not at the edges
    # Split torso into left edge, center, and right edge
    center_left = int(w * 0.35)
    center_right = int(w * 0.65)
    
    torso_center = white_mask[torso_top:torso_bot, center_left:center_right]
    torso_center_total = torso_center.size
    
    if torso_center_total == 0:
        return False
    
    # Edge detection to verify there's an actual person
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    full_edge_density = np.mean(edges) / 255.0
    
    # No body contours detected - likely a blank/background image
    if full_edge_density < 0.01:
        return False
    
    # Check if the center of the torso has a contiguous white band
    kernel = np.ones((5, 5), np.uint8)
    cleaned = cv2.morphologyEx(torso_center, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return False
    
    # Find the largest contiguous white region in the center of the torso
    largest = max(contours, key=cv2.contourArea)
    largest_area = cv2.contourArea(largest)
    largest_ratio = largest_area / torso_center_total
    
    # A brace should occupy a significant contiguous area in the center of the torso
    return largest_ratio > 0.08
