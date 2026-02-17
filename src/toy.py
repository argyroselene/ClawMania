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
        # Construct the absolute path to the image
        # In a real app we'd have a resource manager, but for now let's load it here or in __init__
        # Ideally, we load it once. 
        # But to keep it simple for this step:
        
        # We need to make sure the image is loaded. 
        # For performance, we should load it in __init__ or have a shared loader.
        # Let's add a static cache or just load in __init__ for now since there are few toys.
        
        if not hasattr(self, 'image'):
            try:
                # Assuming assets are in d:\Simulation project\ClawMania\assets\images\toy.png
                # We need to get the base path.
                import os
                # __file__ is .../src/toy.py
                # dirname -> .../src
                # dirname -> .../ClawMania (Root)
                base_path = os.path.dirname(os.path.dirname(__file__)) 
                image_path = os.path.join(base_path, "assets", "images", "toy.png")
                self.image = pygame.image.load(image_path).convert_alpha()

                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except Exception as e:
                print(f"Error loading toy.png: {e}")
                self.image = None

        if self.image:
            screen.blit(self.image, self.rect)
        else:
            # Fallback to rect
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)

