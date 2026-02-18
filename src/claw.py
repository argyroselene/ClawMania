import pygame
from src.utils import SCREEN_WIDTH, SCREEN_HEIGHT, load_image

class Claw:
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 120
        self.config = config
        
        # Load Assets
        self.img_open = load_image("claw_open.png", self.width, self.height)
        self.img_closed = load_image("claw_closed.png", self.width, self.height)
        # For arm, we might want to keep original width but stretch height dynamically, 
        # or tile it. For simplicity, let's load it raw and crop/tile in draw.
        self.img_arm = load_image("claw_arm.png") 
        if self.img_arm:
             # Scale arm width to something reasonable if needed, e.g., 20px
             self.img_arm = pygame.transform.scale(self.img_arm, (20, self.img_arm.get_height()))
        
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
        self.max_drop_depth = 470 # Adjusted for larger claw height (590 floor - 120 height)
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
            # held_toy is cleared by Machine.drop_toy()
            self.state = "IDLE" # Reset

    def draw(self, screen):
        # Draw Rope (Arm)
        if self.img_arm:
            # Stretch or tile? Let's just draw a line for now if image is missing, 
            # or stretch the image to the current length.
            # Arm goes from (self.x, 0) to (self.x, self.y)
            # Center the arm image on self.x
            arm_height = max(1, self.y)
            # Scale simply for now
            scaled_arm = pygame.transform.scale(self.img_arm, (self.img_arm.get_width(), int(arm_height)))
            screen.blit(scaled_arm, (self.x - self.img_arm.get_width()//2, 0))
        else:
             # Fallback
             pygame.draw.line(screen, (100, 100, 100), (self.x, 0), (self.x, self.y), 2)
        
        # Draw Claw Body
        image_to_draw = self.img_open
        if self.state in ["GRABBING", "LIFTING", "RETURNING"]:
            if self.img_closed:
                image_to_draw = self.img_closed
        
        if image_to_draw:
            # Image is already scaled to width/height
            # Draw centered on x, and top at y
            # self.x is center X.
            screen.blit(image_to_draw, (self.x - self.width//2, self.y))
        else:
            # Fallback Geometric Drawing
            rect = pygame.Rect(self.x - self.width//2, self.y, self.width, self.height)
            pygame.draw.rect(screen, (255, 105, 180), rect)
            pygame.draw.rect(screen, (0, 255, 255), rect, 2)

