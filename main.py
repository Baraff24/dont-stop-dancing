import pygame
import sys
import random
import math
import numpy as np
from moviepy.editor import VideoFileClip
import mediapipe as mp
import os

# Set ffmpeg path
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BG_COLOR = (0, 0, 0)
CIRCLE_COLOR = (255, 105, 180)
INNER_CIRCLE_COLOR = (169, 169, 169)  # Grey color for the inner circle
BALL_COLOR = (255, 0, 255)
FPS = 60
BALL_INITIAL_SIZE = 20
BALL_GROWTH_RATE = 2.5
BALL_SPEED = 5
CIRCLE_RADIUS = 250  # Radius of the outer circle
CIRCLE_CENTER = (WIDTH // 2, HEIGHT // 2)
MAX_BALL_SIZE = CIRCLE_RADIUS - 5  # Maximum size of the ball

# Initialize MediaPipe Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)


def remove_greenscreen(im):
    im_rgb = im[:, :, :3]
    im_rgb = (im_rgb * 255).astype(np.uint8)
    results = mp_selfie_segmentation.process(im_rgb)
    mask = results.segmentation_mask
    mask = mask > 0.8
    mask = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
    im = im_rgb * mask
    return im


# Load video and apply greenscreen removal
toothless_video = VideoFileClip("toothless-dancing-driftveil-city-greenscreen.mp4").resize(height=200).fl_image(
    remove_greenscreen)

# Set up the window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Ball grows with every bounce until Toothless stops dancing')


# Ball class
class Ball:
    def __init__(self):
        self.size = BALL_INITIAL_SIZE
        self.x = CIRCLE_CENTER[0]
        self.y = CIRCLE_CENTER[1]
        self.dx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.dy = random.choice([-BALL_SPEED, BALL_SPEED])

    def move(self):
        self.x += self.dx
        self.y += self.dy

        # Calculate distance from the center of the circle
        distance_from_center = math.sqrt((self.x - CIRCLE_CENTER[0]) ** 2 + (self.y - CIRCLE_CENTER[1]) ** 2)

        # Check for bounces and increase ball size
        if distance_from_center + self.size >= CIRCLE_RADIUS:
            # Calculate angle of incidence and reflect the ball
            angle = math.atan2(self.y - CIRCLE_CENTER[1], self.x - CIRCLE_CENTER[0])
            self.dx = -BALL_SPEED * math.cos(angle + random.uniform(-0.1, 0.1))
            self.dy = -BALL_SPEED * math.sin(angle + random.uniform(-0.1, 0.1))
            if self.size < MAX_BALL_SIZE:
                self.size += BALL_GROWTH_RATE
            # Start Toothless video
            toothless.dance()
        else:
            toothless.stop_dance()

    def draw(self, window):
        # Draw the inner ball
        pygame.draw.circle(window, BALL_COLOR, (self.x, self.y), self.size)


# Toothless class
class Toothless:
    def __init__(self):
        self.video = toothless_video
        self.dance_start_time = None
        self.dancing = False

    def dance(self):
        if not self.dancing:
            self.dancing = True
            self.dance_start_time = pygame.time.get_ticks() / 1000.0

    def stop_dance(self):
        self.dancing = False
        self.dance_start_time = None

    def draw(self, window):
        if self.dancing:
            current_time = pygame.time.get_ticks() / 1000.0
            video_time = current_time - self.dance_start_time
            if video_time >= self.video.duration:
                self.stop_dance()
            else:
                frame = self.video.get_frame(video_time)
                frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                window.blit(frame_surface, (CIRCLE_CENTER[0] - 100, CIRCLE_CENTER[1] - 100))


# Initialize objects
ball = Ball()
toothless = Toothless()

# Main loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the ball
    ball.move()

    # Draw everything
    window.fill(BG_COLOR)
    pygame.draw.circle(window, INNER_CIRCLE_COLOR, CIRCLE_CENTER, CIRCLE_RADIUS)  # Draw the inner circle
    pygame.draw.circle(window, CIRCLE_COLOR, CIRCLE_CENTER, CIRCLE_RADIUS, 5)  # Draw the outer circle border
    ball.draw(window)
    toothless.draw(window)
    pygame.display.flip()

    # Control the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()
