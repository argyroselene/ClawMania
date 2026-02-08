import pygame

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 30) # Dark blue-ish black
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

# Retro Theme
HOT_PINK = (255, 105, 180)
DEEP_PURPLE = (50, 0, 50)
NEON_GREEN = (57, 255, 20)
CYAN = (0, 255, 255)
PIXEL_YELLOW = (255, 215, 0)

# Semantic Aliases
BG_COLOR = DEEP_PURPLE
UI_BG_COLOR = (70, 20, 70)
TEXT_COLOR = HOT_PINK
HIGHLIGHT_COLOR = CYAN

# Fonts
def get_font(size):
    return pygame.font.SysFont("Arial", size)

# Game Constants
GRAVITY = 0.5
