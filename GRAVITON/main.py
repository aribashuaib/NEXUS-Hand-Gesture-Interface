# main.py
# NEXUS — Real-Time Hand Gesture Interface
# Final Year Project | Computer Vision System
# Built with Python, OpenCV, MediaPipe, Pygame

import cv2
import pygame
import sys
import time
from hand_tracking import HandTracker
from gestures import detect_gesture, get_palm_center, get_finger_angles
from renderer import (
    draw_grid, draw_scanlines, draw_gesture_display,
    draw_finger_bars, draw_hand_info, draw_stats,
    draw_title, draw_radar, DARK_BG, NEON_CYAN, DIM_CYAN
)
from particles import ParticleSystem

# --- Config ---
WIDTH, HEIGHT = 1400, 800
CAM_W, CAM_H  = 640, 480
FPS           = 60
CAM_PANEL_W   = 680
CAM_PANEL_H   = 510
RIGHT_W       = WIDTH - CAM_PANEL_W - 20

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("NEXUS — Real-Time Hand Gesture Interface")
    clock = pygame.time.Clock()

    # Fonts
    font_title  = pygame.font.SysFont("consolas", 42, bold=True)
    font_big    = pygame.font.SysFont("consolas", 36, bold=True)
    font_med    = pygame.font.SysFont("consolas", 22, bold=True)
    font_small  = pygame.font.SysFont("consolas", 15)
    font_tiny   = pygame.font.SysFont("consolas", 12)

    # Systems
    tracker  = HandTracker()
    particles = ParticleSystem(WIDTH, HEIGHT)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)

    fps_display = 60.0
    gesture_history = []

    while True:
        dt = clock.tick(FPS)
        fps_display = 0.9 * fps_display + 0.1 * clock.get_fps()

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                cap.release()
                pygame.quit()
                sys.exit()

        # --- Webcam ---
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)  # mirror

        hands_data, frame = tracker.get_hands(frame)

        # --- Gesture Detection ---
        gestures = []
        angles_data = {}
        for hand in hands_data:
            lms = hand["landmarks"]
            g = detect_gesture(lms)
            gestures.append(g)
            angles_data = get_finger_angles(lms)

            palm = get_palm_center(lms)
            # Map to screen
            sx = int(palm[0] / CAM_W * CAM_PANEL_W)
            sy = int(palm[1] / CAM_H * CAM_PANEL_H) + 90
            particles.emit(sx, sy, g)

        current_gesture = gestures[0] if gestures else "NONE"

        # --- Update ---
        particles.update()

        # --- Draw Background ---
        screen.fill(DARK_BG)
        draw_grid(screen, WIDTH, HEIGHT)

        # --- Particles (data streams behind everything) ---
        particles.draw(screen, font_tiny)

        # --- Title ---
        draw_title(screen, font_title, font_small)

        # --- Webcam Panel (left side) ---
        cam_x, cam_y = 10, 90
        frame_resized = cv2.resize(frame, (CAM_PANEL_W, CAM_PANEL_H))
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        frame_surf = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))

        # Dim the webcam slightly for cyberpunk look
        dim = pygame.Surface((CAM_PANEL_W, CAM_PANEL_H))
        dim.set_alpha(30)
        dim.fill((0, 0, 20))

        screen.blit(frame_surf, (cam_x, cam_y))
        screen.blit(dim, (cam_x, cam_y))

        # Border around webcam
        from renderer import draw_corner_brackets
        draw_corner_brackets(screen, cam_x, cam_y, CAM_PANEL_W, CAM_PANEL_H, NEON_CYAN, size=30, thickness=2)

        # Webcam label
        lbl = font_small.render("[ LIVE FEED — HAND TRACKING ACTIVE ]", True, NEON_CYAN)
        screen.blit(lbl, (cam_x + 10, cam_y + CAM_PANEL_H + 8))

        # --- Right Panel ---
        rx = CAM_PANEL_W + 20
        pad = 10

        # Gesture display (top right)
        draw_gesture_display(screen, font_big, font_med, font_small,
                             current_gesture,
                             rx, 90, RIGHT_W - pad, 160)

        # Hand info
        draw_hand_info(screen, font_med, font_small, hands_data, gestures,
                       rx, 265, RIGHT_W - pad, 170)

        # Finger angle bars
        if angles_data:
            draw_finger_bars(screen, font_small, angles_data,
                             rx, 450, RIGHT_W - pad, 160)
        else:
            draw_finger_bars(screen, font_small,
                             {"Index": 0, "Middle": 0, "Ring": 0, "Pinky": 0},
                             rx, 450, RIGHT_W - pad, 160)

        # Stats
        draw_stats(screen, font_med, font_small,
                   fps_display, len(hands_data),
                   rx, 625, RIGHT_W - pad, 135)

        # Radar (bottom left corner)
        draw_radar(screen, font_small, hands_data,
                   cam_x + 80, cam_y + CAM_PANEL_H - 80, 60)

        # Scanlines overlay for cyberpunk feel
        draw_scanlines(screen, WIDTH, HEIGHT)

        pygame.display.flip()

    cap.release()
    pygame.quit()

if __name__ == "__main__":
    main()