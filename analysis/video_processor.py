from .pose_detector import detector
from .brace_detector import detect_brace
from .posture_rules import analyze_posture
from .rotation_rules import analyze_rotation
from .back_asymmetry import analyze_back_asymmetry
from .gait_rules import analyze_gait
from .exercise_rules import analyze_exercise
import cv2
import os

def process_media(path, mode, age_group='under15'):
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.jpg', '.jpeg', '.png', '.bmp'):
        image = cv2.imread(path)
        if image is None:
            return {'status': 'error', 'message': 'Could not read image'}
        frames = [image]
    else:
        cap = cv2.VideoCapture(path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames = []
        if frame_count > 1:
            for i in range(0, min(frame_count, 10)):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i * (frame_count // 10))
                ret, frame = cap.read()
                if ret: frames.append(frame)
        else:
            ret, frame = cap.read()
            if ret: frames.append(frame)
        cap.release()

    if not frames:
        return {'status': 'error', 'message': 'Could not read media'}

    image = frames[len(frames)//2]
    has_brace = detect_brace(image)
    landmarks = detector.detect(image)

    if not landmarks:
        return {'status': 'error', 'message': 'No person detected'}

    analysis = {
        'status': 'success',
        'mode': mode,
        'brace_detected': has_brace,
        'metrics': {}
    }

    if 'standing' in mode:
        metrics = analyze_posture(landmarks, image.shape, age_group)
        rotation = analyze_rotation(landmarks, image.shape, age_group)
        metrics.update(rotation)
        back_asym = analyze_back_asymmetry(image, landmarks)
        metrics.update(back_asym)
        analysis['metrics'] = metrics
    elif 'walking' in mode:
        all_landmarks = [detector.detect(f) for f in frames if detector.detect(f)]
        gait_metrics = analyze_gait(all_landmarks, image.shape)
        if landmarks:
            rotation = analyze_rotation(landmarks, image.shape, age_group)
            gait_metrics.update(rotation)
        analysis['metrics'] = gait_metrics
    elif 'exercise' in mode:
        analysis['metrics'] = analyze_exercise(landmarks, image.shape)

    return analysis
