# renderer.py
# Draws the full cyberpunk HUD interface

import pygame
import numpy as np
import math
import time

# Color palette
NEON_CYAN    = (0, 255, 220)
NEON_PINK    = (255, 0, 200)
NEON_GREEN   = (0, 255, 100)
NEON_PURPLE  = (160, 0, 255)
NEON_ORANGE  = (255, 140, 0)
DARK_BG      = (5, 5, 15)
PANEL_BG     = (8, 8, 25)
GRID_COLOR   = (15, 15, 40)
WHITE        = (255, 255, 255)
DIM_CYAN     = (0, 80, 100)

GESTURE_COLORS = {
    "PINCH":  NEON_PINK,
    "FIST":   NEON_ORANGE,
    "OPEN":   NEON_CYAN,
    "PEACE":  NEON_GREEN,
    "POINT":  (0, 180, 255),
    "THREE":  NEON_PURPLE,
    "NONE":   (60, 60, 80),
}

def draw_glow_circle(screen, color, pos, radius, width=2, layers=3):
    for i in range(layers, 0, -1):
        alpha_surf = pygame.Surface((radius*2+20, radius*2+20), pygame.SRCALPHA)
        r, g, b = color
        alpha = int(40 / i)
        pygame.draw.circle(alpha_surf, (r, g, b, alpha),
                           (radius+10, radius+10), radius + i*3, width+i)
        screen.blit(alpha_surf, (pos[0]-radius-10, pos[1]-radius-10))
    pygame.draw.circle(screen, color, pos, radius, width)

def draw_grid(screen, width, height):
    spacing = 50
    for x in range(0, width, spacing):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, height), 1)
    for y in range(0, height, spacing):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (width, y), 1)

def draw_scanlines(screen, width, height):
    for y in range(0, height, 4):
        pygame.draw.line(screen, (0, 0, 0, 30), (0, y), (width, y), 1)

def draw_corner_brackets(screen, x, y, w, h, color, size=20, thickness=2):
    # Top left
    pygame.draw.lines(screen, color, False, [(x+size, y), (x, y), (x, y+size)], thickness)
    # Top right
    pygame.draw.lines(screen, color, False, [(x+w-size, y), (x+w, y), (x+w, y+size)], thickness)
    # Bottom left
    pygame.draw.lines(screen, color, False, [(x+size, y+h), (x, y+h), (x, y+h-size)], thickness)
    # Bottom right
    pygame.draw.lines(screen, color, False, [(x+w-size, y+h), (x+w, y+h), (x+w, y+h-size)], thickness)

def draw_panel(screen, x, y, w, h, color=DIM_CYAN):
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((8, 8, 25, 200))
    screen.blit(panel, (x, y))
    draw_corner_brackets(screen, x, y, w, h, color)

def draw_gesture_display(screen, font_big, font_med, font_small, gesture, x, y, w, h):
    draw_panel(screen, x, y, w, h, GESTURE_COLORS.get(gesture, DIM_CYAN))

    # Label
    label = font_small.render("GESTURE DETECTED", True, DIM_CYAN)
    screen.blit(label, (x + 15, y + 15))

    # Big gesture name
    color = GESTURE_COLORS.get(gesture, (60, 60, 80))
    text = font_big.render(gesture, True, color)
    tx = x + w//2 - text.get_width()//2
    ty = y + h//2 - text.get_height()//2
    screen.blit(text, (tx, ty))

    # Pulsing ring
    t = time.time()
    pulse = int(20 + 10 * math.sin(t * 4))
    draw_glow_circle(screen, color, (x + w//2, y + h//2 + 10), pulse + 30, width=1, layers=2)

def draw_finger_bars(screen, font_small, angles, x, y, w, h):
    draw_panel(screen, x, y, w, h)
    title = font_small.render("FINGER JOINT ANGLES", True, DIM_CYAN)
    screen.blit(title, (x+15, y+12))

    bar_colors = [NEON_CYAN, NEON_PINK, NEON_GREEN, NEON_PURPLE]
    fingers = list(angles.items())
    bar_h = 18
    gap = 28

    for i, (name, angle) in enumerate(fingers):
        by = y + 40 + i * gap
        bar_w = int((angle / 180) * (w - 80))
        color = bar_colors[i % len(bar_colors)]

        # Background bar
        pygame.draw.rect(screen, (20, 20, 40), (x+70, by, w-80, bar_h), border_radius=4)
        # Filled bar
        if bar_w > 0:
            pygame.draw.rect(screen, color, (x+70, by, bar_w, bar_h), border_radius=4)
        # Label
        lbl = font_small.render(f"{name[:3]}: {angle}°", True, color)
        screen.blit(lbl, (x+5, by+2))

def draw_hand_info(screen, font_med, font_small, hands_data, gestures, x, y, w, h):
    draw_panel(screen, x, y, w, h)
    title = font_small.render("HAND TRACKING DATA", True, DIM_CYAN)
    screen.blit(title, (x+15, y+12))

    if not hands_data:
        msg = font_med.render("NO HANDS DETECTED", True, (80, 80, 100))
        screen.blit(msg, (x + w//2 - msg.get_width()//2, y + h//2 - 10))
        return

    for i, hand in enumerate(hands_data[:2]):
        col = NEON_CYAN if hand["label"] == "Right" else NEON_PINK
        oy = y + 40 + i * 80

        label_text = font_med.render(f"{hand['label'].upper()} HAND", True, col)
        screen.blit(label_text, (x+15, oy))

        conf_text = font_small.render(f"Confidence: {int(hand['confidence']*100)}%", True, WHITE)
        screen.blit(conf_text, (x+15, oy+28))

        if i < len(gestures):
            g_color = GESTURE_COLORS.get(gestures[i], WHITE)
            g_text = font_small.render(f"Gesture: {gestures[i]}", True, g_color)
            screen.blit(g_text, (x+15, oy+50))

def draw_stats(screen, font_med, font_small, fps, hand_count, x, y, w, h):
    draw_panel(screen, x, y, w, h)
    title = font_small.render("SYSTEM STATS", True, DIM_CYAN)
    screen.blit(title, (x+15, y+12))

    fps_color = NEON_GREEN if fps >= 50 else NEON_ORANGE if fps >= 30 else (255, 50, 50)
    fps_text = font_med.render(f"FPS: {int(fps)}", True, fps_color)
    screen.blit(fps_text, (x+15, y+40))

    hands_text = font_med.render(f"HANDS: {hand_count}/2", True, NEON_CYAN)
    screen.blit(hands_text, (x+15, y+70))

    t = time.strftime("%H:%M:%S")
    time_text = font_small.render(f"TIME: {t}", True, WHITE)
    screen.blit(time_text, (x+15, y+100))

def draw_title(screen, font_title, font_small):
    t = time.time()
    # Animate color
    r = int(127 + 127 * math.sin(t * 2))
    g = int(127 + 127 * math.sin(t * 2 + 2))
    b = 255
    title = font_title.render("N E X U S", True, (r, g, b))
    screen.blit(title, (20, 15))
    sub = font_small.render("REAL-TIME HAND GESTURE INTERFACE  //  COMPUTER VISION SYSTEM", True, DIM_CYAN)
    screen.blit(sub, (22, 65))

def draw_radar(screen, font_small, landmarks_list, cx, cy, radius):
    # Mini radar showing hand position
    draw_glow_circle(screen, DIM_CYAN, (cx, cy), radius, width=1)
    draw_glow_circle(screen, GRID_COLOR, (cx, cy), radius//2, width=1)
    pygame.draw.line(screen, GRID_COLOR, (cx-radius, cy), (cx+radius, cy), 1)
    pygame.draw.line(screen, GRID_COLOR, (cx, cy-radius), (cx, cy+radius), 1)

    label = font_small.render("RADAR", True, DIM_CYAN)
    screen.blit(label, (cx - label.get_width()//2, cy - radius - 20))

    colors = [NEON_CYAN, NEON_PINK]
    for i, hand in enumerate(landmarks_list[:2]):
        lms = hand["landmarks"]
        palm = lms[9]
        # Normalize to radar
        nx = cx + int((palm[0] - 320) / 320 * radius)
        ny = cy + int((palm[1] - 240) / 240 * radius)
        nx = max(cx-radius, min(cx+radius, nx))
        ny = max(cy-radius, min(cy+radius, ny))
        draw_glow_circle(screen, colors[i], (nx, ny), 8, width=0, layers=2)