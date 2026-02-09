import pygame
from src.utils import SCREEN_WIDTH, SCREEN_HEIGHT, GRAY, DEEP_PURPLE, NEON_GREEN

class Bin:
    def __init__(self, x, y, width, height, speed=0.0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = 1 # 1 for right, -1 for left
        self.color = DEEP_PURPLE
        self.border_color = NEON_GREEN
        
        # Bounds for movement
        self.min_x = 50
        self.max_x = SCREEN_WIDTH - 50 - width

    def update(self):
        if self.speed > 0:
            self.x += self.speed * self.direction
            
            # Bounce logic
            if self.x >= self.max_x:
                self.x = self.max_x
                self.direction = -1
            elif self.x <= self.min_x:
                self.x = self.min_x
                self.direction = 1

    def draw(self, screen):
        # Draw Bin Container (U-shape)
        thickness = 10
        
        # Bottom
        pygame.draw.rect(screen, self.color, (self.x, self.y + self.height - thickness, self.width, thickness))
        pygame.draw.rect(screen, self.border_color, (self.x, self.y + self.height - thickness, self.width, thickness), 2)
        
        # Left Wall
        pygame.draw.rect(screen, self.color, (self.x, self.y, thickness, self.height))
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, thickness, self.height), 2)
        
        # Right Wall
        pygame.draw.rect(screen, self.color, (self.x + self.width - thickness, self.y, thickness, self.height))
        pygame.draw.rect(screen, self.border_color, (self.x + self.width - thickness, self.y, thickness, self.height), 2)
