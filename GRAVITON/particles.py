
import pygame
import random
import numpy as np

class Particle:
    def __init__(self, x, y, color, speed=2):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * np.pi)
        spd = random.uniform(0.5, speed)
        self.vx = np.cos(angle) * spd
        self.vy = np.sin(angle) * spd
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.size = random.uniform(2, 5)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size *= 0.97

    def draw(self, screen):
        if self.life > 0 and self.size > 0.5:
            alpha = int(self.life * 255)
            r, g, b = self.color
            color = (min(255,r), min(255,g), min(255,b))
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))

    def is_dead(self):
        return self.life <= 0 or self.size < 0.5


class DataStream:
    # Falling data characters like Matrix effect
    def __init__(self, x, height):
        self.x = x
        self.y = random.randint(-height, 0)
        self.speed = random.uniform(2, 6)
        self.height = height
        self.char = random.choice("01NEXUS<>{}[]|\\/*&^%$#@!")
        self.brightness = random.randint(80, 255)

    def update(self):
        self.y += self.speed
        if self.y > self.height:
            self.y = random.randint(-200, 0)
            self.char = random.choice("01NEXUS<>{}[]|\\/*&^%$#@!")

    def draw(self, screen, font):
        color = (0, self.brightness, int(self.brightness * 0.5))
        text = font.render(self.char, True, color)
        screen.blit(text, (self.x, int(self.y)))


class ParticleSystem:
    def __init__(self, width, height):
        self.particles = []
        self.streams = [DataStream(x, height) for x in range(0, width, 25)]
        self.width = width
        self.height = height

    def emit(self, x, y, gesture):
        colors = {
            "PINCH":  (255, 50, 200),   # pink
            "FIST":   (255, 80, 0),     # orange
            "OPEN":   (0, 255, 180),    # cyan
            "PEACE":  (100, 255, 0),    # green
            "POINT":  (0, 180, 255),    # blue
            "THREE":  (180, 0, 255),    # purple
            "NONE":   (100, 100, 100),  # grey
        }
        color = colors.get(gesture, (255, 255, 255))
        count = 8 if gesture != "NONE" else 2
        for _ in range(count):
            self.particles.append(Particle(x, y, color, speed=3))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.is_dead()]
        for s in self.streams:
            s.update()

    def draw(self, screen, small_font):
        for s in self.streams:
            s.draw(screen, small_font)
        for p in self.particles:
            p.draw(screen)