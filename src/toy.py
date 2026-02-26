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
        self.vy = 0 # Vertical velocity
        self.vx = 0
        self.in_basket = False
        self.on_ground = False
        
        # Properties based on size
        if size == "small":
            self.width = 60
            self.height = 60
            self.weight_factor = 0.8
            self.difficulty_factor = 1.2 # Harder to grab small things? Or easier? Specs said "Small toys may still slip"
            self.color = HOT_PINK
            self.points = 10
        elif size == "medium":
            self.width = 80
            self.height = 80
            self.weight_factor = 1.0
            self.difficulty_factor = 1.0
            self.color = PIXEL_YELLOW
            self.points = 20
        elif size == "large":
            self.width = 100
            self.height = 100
            self.weight_factor = 1.5
            self.difficulty_factor = 0.7 # Easier to target, harder to hold? 
           
            self.difficulty_factor = 0.8 
            self.color = CYAN
            self.points = 30

        self.rect = pygame.Rect(x, y - self.height, self.width, self.height)

    def update(self, bin_x, bin_velocity):
        if self.grabbed:
            self.vy = 0
            self.vx = 0
            self.on_ground = False
        elif self.in_basket:
            # Settle in basket
            self.vy = 0
            self.vx = 0
            self.on_ground = True
        else:
            
            self.vy += 0.5 # Gravity
            self.y += self.vy
            self.x += self.vx
            
            
            
            ground_y = 600 - 10 
            floor_y = 590 
            
            if self.y + self.height >= floor_y:
                self.y = floor_y - self.height
                self.vy = 0
                self.on_ground = True
                
                
                self.x += bin_velocity # Friction?
            else:
                 self.on_ground = False

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen):
        
        
        if not hasattr(self, 'image'):
            try:
                
                import os
                
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

