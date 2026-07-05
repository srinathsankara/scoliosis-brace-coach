import os
import urllib.request
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_URL = (
    'https://storage.googleapis.com/mediapipe-models/'
    'pose_landmarker/pose_landmarker_lite/float16/1/'
    'pose_landmarker_lite.task'
)
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pose_landmarker.task')


class PoseDetector:
    def __init__(self):
        self._ensure_model()
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def _ensure_model(self):
        if os.path.exists(MODEL_PATH):
            return
        print('[Scoliosis Coach] Downloading pose model...')
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print('[Scoliosis Coach] Model downloaded.')
        except Exception as exc:
            print(f'[Scoliosis Coach] ERROR downloading model: {exc}')

    def detect(self, image):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.landmarker.detect(mp_image)
        return result.pose_landmarks[0] if result.pose_landmarks else None

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return angle if angle <= 180.0 else 360.0 - angle

    def get_landmark_coords(self, landmarks, image_shape, landmark_id):
        h, w = image_shape[:2]
        lm = landmarks[landmark_id]
        return [int(lm.x * w), int(lm.y * h)]


detector = PoseDetector()
