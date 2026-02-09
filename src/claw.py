import pygame
from src.utils import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, HOT_PINK, CYAN, NEON_GREEN

class Claw:
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.config = config
        
        # Physics / Config properties
        self.move_speed = 5
        self.drop_speed = 4
        self.lift_speed = config.get("lift_speed", 3.0)
        self.drop_delay = config.get("drop_delay", 0.5)
        self.grip_strength = config.get("grip_strength", 0.8)
        self.release_offset = config.get("release_offset", 0.0)
        
        # State Machine
        self.state = "IDLE" # IDLE, MOVING, DROPPING, GRABBING, LIFTING, RETURNING, RELEASING
        self.target_y = y
        self.max_drop_depth = 450
        self.grab_timer = 0
        self.held_toy = None

    def update(self):
        dt = 1/60 # approximation
        
        if self.state == "IDLE":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.x -= self.move_speed
            if keys[pygame.K_RIGHT]:
                self.x += self.move_speed
                
            self.x = max(50, min(self.x, SCREEN_WIDTH - 50))
            
            if keys[pygame.K_SPACE]:
                self.state = "DROPPING"
                
        elif self.state == "DROPPING":
            self.y += self.drop_speed
            if self.y >= self.max_drop_depth:
                self.state = "GRABBING"
                self.grab_timer = pygame.time.get_ticks()
                
        elif self.state == "GRABBING":
            # Wait for drop delay
            elapsed = (pygame.time.get_ticks() - self.grab_timer) / 1000.0
            if elapsed >= self.drop_delay:
                self.state = "LIFTING"
                # TODO: Check collision with toys here
                
        elif self.state == "LIFTING":
            self.y -= self.lift_speed
            if self.y <= 100: # Return height
                self.state = "RETURNING"
                
        elif self.state == "RETURNING":
            # Move back to start (left side usually)
            if self.x > 100:
                self.x -= self.move_speed
            else:
                self.state = "RELEASING"
                
        elif self.state == "RELEASING":
            # Open claw, drop toy
            # Apply release offset
            if self.held_toy:
                self.held_toy = None
            
            self.state = "IDLE" # Reset

    def draw(self, screen):
        # Draw Rope
        pygame.draw.line(screen, GRAY, (self.x, 0), (self.x, self.y), 2)
        
        # Draw Claw Body
        rect = pygame.Rect(self.x - self.width//2, self.y, self.width, self.height)
        pygame.draw.rect(screen, HOT_PINK, rect)
        pygame.draw.rect(screen, CYAN, rect, 2) # Border
        
        # Draw "fingers"
        finger_color = NEON_GREEN
        if self.state in ["GRABBING", "LIFTING", "RETURNING"]:
            # Closed
            pygame.draw.line(screen, finger_color, (self.x - 15, self.y + 60), (self.x, self.y + 80), 3)
            pygame.draw.line(screen, finger_color, (self.x + 15, self.y + 60), (self.x, self.y + 80), 3)
        else:
            # Open
            pygame.draw.line(screen, finger_color, (self.x - 15, self.y + 60), (self.x - 25, self.y + 90), 3)
            pygame.draw.line(screen, finger_color, (self.x + 15, self.y + 60), (self.x + 25, self.y + 90), 3)
