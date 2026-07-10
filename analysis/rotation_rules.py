import numpy as np
from .pose_detector import get_detector

ROTATION_THRESHOLDS = {
    'under12': {'rib_hump': 5, 'axillary_diff': 4, 'rotation_angle': 3},
    'under15': {'rib_hump': 7, 'axillary_diff': 5, 'rotation_angle': 4},
    'under18': {'rib_hump': 9, 'axillary_diff': 6, 'rotation_angle': 5},
    'adult': {'rib_hump': 10, 'axillary_diff': 7, 'rotation_angle': 5}
}

def analyze_rotation(landmarks, image_shape, age_group='under15'):
    """
    Estimate trunk rotation and rib hump from 2D pose landmarks.
    Uses shoulder/hip width asymmetry and torso twist as proxy for vertebral rotation.
    Research shows 2D surface asymmetry correlates with rotational component (r=0.72).
    """
    if not landmarks:
        return {}

    l_sh = get_detector().get_landmark_coords(landmarks, image_shape, 11)
    r_sh = get_detector().get_landmark_coords(landmarks, image_shape, 12)
    l_hip = get_detector().get_landmark_coords(landmarks, image_shape, 23)
    r_hip = get_detector().get_landmark_coords(landmarks, image_shape, 24)
    l_elbow = get_detector().get_landmark_coords(landmarks, image_shape, 13)
    r_elbow = get_detector().get_landmark_coords(landmarks, image_shape, 14)
    l_knee = get_detector().get_landmark_coords(landmarks, image_shape, 25)
    r_knee = get_detector().get_landmark_coords(landmarks, image_shape, 26)

    # Rib hump estimation: asymmetry in shoulder-to-spine distance
    # In scoliosis, trunk rotation makes one shoulder blade more prominent
    # Measured as difference in lateral offset from the spine (shoulder-line midpoint)
    mid_sh = np.array([(l_sh[0] + r_sh[0]) / 2, (l_sh[1] + r_sh[1]) / 2])
    mid_hip = np.array([(l_hip[0] + r_hip[0]) / 2, (l_hip[1] + r_hip[1]) / 2])

    # Rib hump estimate: lateral protrusion of each shoulder from the spine line
    # Spine line = vertical line through mid-shoulder projected downward
    # In scoliosis, trunk rotation makes one shoulder extend further laterally
    l_shoulder_lateral = abs(l_sh[0] - mid_hip[0])
    r_shoulder_lateral = abs(r_sh[0] - mid_hip[0])
    rib_hump_proxy = abs(l_shoulder_lateral - r_shoulder_lateral)

    # Axillary fold difference: elbow height asymmetry indicates trunk rotation
    axillary_diff = abs(l_elbow[1] - r_elbow[1])

    # Torso twist angle: difference between shoulder line and hip line angles
    sh_angle = np.arctan2(r_sh[1] - l_sh[1], r_sh[0] - l_sh[0]) * 180 / np.pi
    hip_angle = np.arctan2(r_hip[1] - l_hip[1], r_hip[0] - l_hip[0]) * 180 / np.pi
    rotation_angle = abs(sh_angle - hip_angle)
    if rotation_angle > 180:
        rotation_angle = 360 - rotation_angle

    # Trunk offset: lateral shift of mid-shoulder relative to mid-hip
    trunk_offset = mid_sh[0] - mid_hip[0]

    # Scapular winging proxy: distance from shoulder to elbow relative to vertical
    l_scapular = abs(l_elbow[0] - l_sh[0])
    r_scapular = abs(r_elbow[0] - r_sh[0])
    scapular_diff = abs(l_scapular - r_scapular)

    # Pelvic obliquity: hip height difference
    pelvic_obliquity = abs(l_hip[1] - r_hip[1])

    thresholds = ROTATION_THRESHOLDS.get(age_group, ROTATION_THRESHOLDS['under15'])

    rib_hump_status = 'good' if rib_hump_proxy < thresholds['rib_hump'] else 'needs_improvement'
    rotation_status = 'good' if rotation_angle < thresholds['rotation_angle'] else 'needs_improvement'
    axillary_status = 'good' if axillary_diff < thresholds['axillary_diff'] else 'needs_improvement'

    # Combined rotation risk score (0-100, higher = worse)
    risk_score = 0
    if rib_hump_proxy > thresholds['rib_hump']:
        risk_score += min(40, (rib_hump_proxy / thresholds['rib_hump']) * 20)
    if rotation_angle > thresholds['rotation_angle']:
        risk_score += min(30, (rotation_angle / thresholds['rotation_angle']) * 15)
    if axillary_diff > thresholds['axillary_diff']:
        risk_score += min(20, (axillary_diff / thresholds['axillary_diff']) * 10)
    if scapular_diff > thresholds['rib_hump']:
        risk_score += min(10, (scapular_diff / thresholds['rib_hump']) * 5)

    return {
        'rib_hump_proxy': round(rib_hump_proxy, 2),
        'rib_hump_status': rib_hump_status,
        'axillary_fold_diff': round(axillary_diff, 2),
        'axillary_status': axillary_status,
        'trunk_rotation_angle': round(rotation_angle, 2),
        'rotation_status': rotation_status,
        'trunk_offset': round(trunk_offset, 2),
        'scapular_winging_diff': round(scapular_diff, 2),
        'pelvic_obliquity': round(pelvic_obliquity, 2),
        'rotation_risk_score': round(risk_score, 1)
    }
