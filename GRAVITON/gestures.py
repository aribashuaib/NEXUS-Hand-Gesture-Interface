# gestures.py
# Interprets hand landmarks into named gestures
# Uses finger tip vs knuckle positions to determine state

import numpy as np

# MediaPipe landmark indexes
WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
INDEX_MCP = 5   # index knuckle
MIDDLE_MCP = 9
RING_MCP = 13
PINKY_MCP = 17

def finger_is_up(landmarks, tip, mcp):
    return landmarks[tip][1] < landmarks[mcp][1]

def get_distance(p1, p2):
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def detect_gesture(landmarks):
    if not landmarks or len(landmarks) < 21:
        return "NONE"

    thumb = landmarks[THUMB_TIP]
    index = landmarks[INDEX_TIP]
    middle = landmarks[MIDDLE_TIP]
    ring = landmarks[RING_TIP]
    pinky = landmarks[PINKY_TIP]
    wrist = landmarks[WRIST]

    # Check which fingers are up
    index_up = finger_is_up(landmarks, INDEX_TIP, INDEX_MCP)
    middle_up = finger_is_up(landmarks, MIDDLE_TIP, MIDDLE_MCP)
    ring_up = finger_is_up(landmarks, RING_TIP, RING_MCP)
    pinky_up = finger_is_up(landmarks, PINKY_TIP, PINKY_MCP)
    fingers_up = sum([index_up, middle_up, ring_up, pinky_up])

    # Pinch detection
    pinch_dist = get_distance(thumb, index)
    if pinch_dist < 40:
        return "PINCH"

    # Fist
    if fingers_up == 0:
        return "FIST"

    # Peace sign
    if index_up and middle_up and not ring_up and not pinky_up:
        return "PEACE"

    # Pointing
    if index_up and not middle_up and not ring_up and not pinky_up:
        return "POINT"

    # Open hand
    if fingers_up >= 4:
        return "OPEN"

    # Three fingers
    if fingers_up == 3:
        return "THREE"

    return "NONE"

def get_palm_center(landmarks):
    # Average of wrist and middle knuckle
    x = (landmarks[0][0] + landmarks[9][0]) // 2
    y = (landmarks[0][1] + landmarks[9][1]) // 2
    return (x, y)

def get_finger_angles(landmarks):
    # Returns angles of each finger for data visualization
    angles = {}
    fingers = {
        "Index": (5, 6, 8),
        "Middle": (9, 10, 12),
        "Ring": (13, 14, 16),
        "Pinky": (17, 18, 20)
    }
    for name, (a, b, c) in fingers.items():
        v1 = np.array(landmarks[b]) - np.array(landmarks[a])
        v2 = np.array(landmarks[c]) - np.array(landmarks[b])
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
        angles[name] = round(angle, 1)
    return angles