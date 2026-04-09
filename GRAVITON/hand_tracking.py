# hand_tracking.py
# Detects and tracks hands using MediaPipe
# Returns landmarks, confidence, and hand label (Left/Right)

import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Custom cyberpunk drawing specs
LANDMARK_STYLE = mp_draw.DrawingSpec(color=(0, 255, 180), thickness=2, circle_radius=3)
CONNECTION_STYLE = mp_draw.DrawingSpec(color=(0, 180, 255), thickness=2)

class HandTracker:
    def __init__(self):
        self.hands = mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def get_hands(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        hands_data = []

        if result.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(result.multi_hand_landmarks):
                # Draw glowing skeleton
                mp_draw.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    LANDMARK_STYLE, CONNECTION_STYLE
                )

                # Get label (Left or Right)
                label = "Right"
                if result.multi_handedness:
                    label = result.multi_handedness[i].classification[0].label
                    score = result.multi_handedness[i].classification[0].score
                else:
                    score = 1.0

                # Extract landmarks
                landmarks = []
                for lm in hand_landmarks.landmark:
                    h, w, _ = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmarks.append((cx, cy))

                hands_data.append({
                    "landmarks": landmarks,
                    "label": label,
                    "confidence": round(score, 2)
                })

        return hands_data, frame