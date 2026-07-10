from .pose_detector import get_detector
import numpy as np

AGE_THRESHOLDS = {
    'under12': {'shoulder_diff': 12, 'trunk_angle': 2.5},
    'under15': {'shoulder_diff': 15, 'trunk_angle': 3.0},
    'under18': {'shoulder_diff': 18, 'trunk_angle': 3.5},
    'adult': {'shoulder_diff': 20, 'trunk_angle': 4.0}
}

def analyze_posture(landmarks, image_shape, age_group='under15'):
    if not landmarks:
        return {}
    
    # Key landmarks
    l_sh = get_detector().get_landmark_coords(landmarks, image_shape, 11)
    r_sh = get_detector().get_landmark_coords(landmarks, image_shape, 12)
    l_hip = get_detector().get_landmark_coords(landmarks, image_shape, 23)
    r_hip = get_detector().get_landmark_coords(landmarks, image_shape, 24)
    nose = get_detector().get_landmark_coords(landmarks, image_shape, 0)
    l_ankle = get_detector().get_landmark_coords(landmarks, image_shape, 27)
    r_ankle = get_detector().get_landmark_coords(landmarks, image_shape, 28)
    
    # Midpoints
    mid_sh = [(l_sh[0] + r_sh[0])/2, (l_sh[1] + r_sh[1])/2]
    mid_hip = [(l_hip[0] + r_hip[0])/2, (l_hip[1] + r_hip[1])/2]
    
    # Metrics
    shoulder_diff = abs(l_sh[1] - r_sh[1])
    hip_diff = abs(l_hip[1] - r_hip[1])
    
    # Trunk lean angle (coronal plane)
    trunk_angle = abs(np.arctan2(mid_sh[0] - mid_hip[0], mid_hip[1] - mid_sh[1]) * 180 / np.pi)
    
    # Head tilt
    head_tilt = abs(nose[0] - mid_sh[0])
    
    # Spine deviation
    spine_deviation = abs(mid_sh[0] - mid_hip[0])
    
    # Arm hang asymmetry
    l_wrist = get_detector().get_landmark_coords(landmarks, image_shape, 15)
    r_wrist = get_detector().get_landmark_coords(landmarks, image_shape, 16)
    arm_diff = abs((l_sh[1] - l_wrist[1]) - (r_sh[1] - r_wrist[1]))
    
    thresholds = AGE_THRESHOLDS.get(age_group, AGE_THRESHOLDS['under15'])
    
    # Status determination
    shoulder_status = "good" if shoulder_diff < thresholds['shoulder_diff'] else "needs_improvement"
    trunk_status = "good" if trunk_angle < thresholds['trunk_angle'] else "needs_improvement"
    
    return {
        'shoulder_asymmetry': round(shoulder_diff, 2),
        'hip_asymmetry': round(hip_diff, 2),
        'trunk_lean_angle': round(trunk_angle, 2),
        'head_tilt': round(head_tilt, 2),
        'spine_deviation': round(spine_deviation, 2),
        'arm_hang_diff': round(arm_diff, 2),
        'shoulder_status': shoulder_status,
        'trunk_status': trunk_status
    }
