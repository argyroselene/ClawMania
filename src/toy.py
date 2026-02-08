import pygame
import random
from src.utils import WHITE, PIXEL_YELLOW, CYAN, HOT_PINK, NEON_GREEN

class Toy:
    def __init__(self, x, y, size="medium"):
        self.x = x
        self.y = y
        self.base_y = y # To return to if dropped
        self.size = size
        self.grabbed = False
        
        # Properties based on size
        if size == "small":
            self.width = 30
            self.height = 30
            self.weight_factor = 0.8
            self.difficulty_factor = 1.2 # Harder to grab small things? Or easier? Specs said "Small toys may still slip"
            self.color = HOT_PINK
            self.points = 10
        elif size == "medium":
            self.width = 40
            self.height = 40
            self.weight_factor = 1.0
            self.difficulty_factor = 1.0
            self.color = PIXEL_YELLOW
            self.points = 20
        elif size == "large":
            self.width = 50
            self.height = 50
            self.weight_factor = 1.5
            self.difficulty_factor = 0.7 # Easier to target, harder to hold? 
            # Let's stick to "Difficulty Factor" as 1.0 for now and tune later
            self.difficulty_factor = 0.8 
            self.color = CYAN
            self.points = 30

        self.rect = pygame.Rect(x, y - self.height, self.width, self.height)

    def update(self, bin_x, bin_velocity):
        if not self.grabbed:
            # Move with the bin
            self.x += bin_velocity
            self.rect.x = self.x
            self.rect.y = self.y - self.height

    def draw(self, screen):
        # Draw pixelated block
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2) # Highlight
        
        # Inner detail to look "toy-like" (eyes?)
        eye_color = (0, 0, 0)
        eye_size = 4
        pygame.draw.rect(screen, eye_color, (self.rect.x + self.width//4, self.rect.y + self.height//3, eye_size, eye_size))
        pygame.draw.rect(screen, eye_color, (self.rect.x + 3*self.width//4 - eye_size, self.rect.y + self.height//3, eye_size, eye_size))
