import cv2
import numpy as np

def detect_brace(image):
    # Convert to HSV to detect common brace colors (white, beige, dark)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Simple heuristic for white/light braces
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Check if a significant portion of the torso is covered
    h, w, _ = image.shape
    torso_region = mask[int(h*0.2):int(h*0.8), int(w*0.2):int(w*0.8)]
    
    white_pixels = cv2.countNonZero(torso_region)
    total_pixels = torso_region.size
    
    percentage = (white_pixels / total_pixels) * 100
    
    # Heuristic: if > 20% of torso is white-ish, might be a brace
    return percentage > 20
