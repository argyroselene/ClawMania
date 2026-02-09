import pygame
import random
from src.claw import Claw
from src.bin import Bin
from src.toy import Toy
from src.utils import SCREEN_WIDTH, SCREEN_HEIGHT

class Machine:
    def __init__(self, config):
        self.config = config
        
        # Initialize Bin
        bin_width = 400
        bin_height = 100
        bin_x = (SCREEN_WIDTH - bin_width) // 2
        bin_y = SCREEN_HEIGHT - 100
        
        # Bin speed comes from config
        bin_speed = config.get("bin_speed", 0.0)
        self.bin = Bin(bin_x, bin_y, bin_width, bin_height, speed=bin_speed)
        
        # Initialize Claw
        claw_x = SCREEN_WIDTH // 2
        claw_y = 100
        self.claw = Claw(claw_x, claw_y, config)
        
        # Initialize Toys
        self.toys = []
        self.populate_toys()
        
        # UI/Feedback state
        self.last_result = "" 
        self.score = 0

    def populate_toys(self):
        # Create a few rows of toys inside the bin
        start_x = self.bin.x + 20
        start_y = self.bin.y + self.bin.height - 10
        
        # Simple grid for now
        for i in range(5):
             # varying sizes
            size = random.choice(["small", "medium", "large"])
            # Distribute them relative to bin position
            toy_x = start_x + i * 60
            toy = Toy(toy_x, start_y, size)
            self.toys.append(toy)

    def update(self):
        # 1. Update Bin
        self.bin.update()
        
        # 2. Update Toys (move with bin if not grabbed)
        bin_velocity = 0
        if self.bin.speed > 0:
            bin_velocity = self.bin.speed * self.bin.direction
            
        for toy in self.toys:
            toy.update(self.bin.x, bin_velocity)
            
        # 3. Update Claw
        prev_state = self.claw.state
        self.claw.update()
        
        # 4. Check Interactions
        
        # STATE CHANGE: GRABBING -> LIFTING (The moment of grab attempt)
        if prev_state == "GRABBING" and self.claw.state == "LIFTING":
            self.attempt_grab()
            
        # STATE: LIFTING/RETURNING (Check for slip)
        if self.claw.state in ["LIFTING", "RETURNING"] and self.claw.held_toy:
            self.check_slip()
            
        # STATE CHANGE: RELEASING -> IDLE (Drop toy)
        if self.claw.state == "RELEASING" and prev_state != "RELEASING":
            self.drop_toy()

        # Update held toy position
        if self.claw.held_toy:
            self.claw.held_toy.x = self.claw.x - self.claw.held_toy.width // 2
            self.claw.held_toy.y = self.claw.y + 60 # Hanging below claw

    def attempt_grab(self):
        # Find closest toy
        closest_toy = None
        min_dist = 999
        
        claw_center_x = self.claw.x
        
        for toy in self.toys:
            if toy.grabbed: continue
            
            toy_center_x = toy.x + toy.width // 2
            dist = abs(claw_center_x - toy_center_x)
            
            if dist < min_dist:
                min_dist = dist
                closest_toy = toy
        
        # Threshold for even attempting (e.g., must be within 40px)
        if closest_toy and min_dist < 40:
            # 1. Alignment Accuracy A
            # A = 1 - (distance / max_allowed_distance)
            max_dist = 40.0
            alignment = max(0.0, 1.0 - (min_dist / max_dist))
            
            # 2. Grab Probability
            # P_grab = G * A * T * D
            # G = grip strength (0-1)
            # T = toy difficulty (around 1)
            # D = level difficulty (1 for practice)
            G = self.config.get("grip_strength", 0.8)
            T = closest_toy.difficulty_factor
            D = 1.0 
            
            P_grab = G * alignment * T * D
            
            # Roll dice
            roll = random.random()
            print(f"Grab Check: Dist={min_dist:.2f}, Align={alignment:.2f}, P={P_grab:.2f}, Roll={roll:.2f}")
            
            if roll <= P_grab:
                # SUCCESS
                self.claw.held_toy = closest_toy
                closest_toy.grabbed = True
                self.last_result = "Grabbed!"
            else:
                self.last_result = "Missed (Bad Roll)"
        else:
             self.last_result = "Missed (Too Far)"

    def check_slip(self):
        # P_slip = (1 - G) * T * L
        # Checked every frame? That's too aggressive.
        # Let's check randomly or every X frames.
        if random.random() < 0.05: # 5% chance per frame to RUN the check
            G = self.config.get("grip_strength", 0.8)
            T = self.claw.held_toy.difficulty_factor
            L = 1.0 # Level slip modifier (config "slip_chance" can be this)
            L = self.config.get("slip_chance", 0.1) * 5 # Scale it up to be noticeable
            
            P_slip = (1.0 - G) * T * L
            
            if random.random() < P_slip:
                # SLIP!
                print(f"Slipped! P_slip={P_slip:.2f}")
                self.claw.held_toy.grabbed = False
                self.claw.held_toy.y = self.bin.y + self.bin.height - 10 # Fall back to bin (simple)
                self.claw.held_toy = None
                self.last_result = "Slipped!"

    def drop_toy(self):
        if self.claw.held_toy:
            # Drop it
            # Apply release offset
            offset_magn = self.config.get("release_offset", 0.0)
            offset = random.uniform(-offset_magn, offset_magn)
            
            self.claw.held_toy.x += offset
            self.claw.held_toy.grabbed = False
            
            # Check if it landed in the chute (e.g., left side < 100)
            if self.claw.held_toy.x < 100:
                self.score += self.claw.held_toy.points
                self.last_result = f"Score! +{self.claw.held_toy.points}"
                # Remove toy or respawn?
                self.toys.remove(self.claw.held_toy)
            else:
                self.last_result = "Dropped Outside"
                # Return to bin Y
                self.claw.held_toy.y = self.bin.y + self.bin.height - 10
            
            self.claw.held_toy = None

    def draw(self, screen):
        # Draw Bin
        self.bin.draw(screen)
        
        # Draw Toys
        for toy in self.toys:
            toy.draw(screen)
            
        # Draw Claw (last so it's on top)
        self.claw.draw(screen)
        
        # Draw HUD (Score / Result)
        from src.utils import get_font, WHITE
        font = get_font(24)
        score_surf = font.render(f"Score: {self.score}", False, WHITE)
        screen.blit(score_surf, (SCREEN_WIDTH - 150, 10))
        
        if self.last_result:
            res_surf = font.render(self.last_result, False, WHITE)
            screen.blit(res_surf, (SCREEN_WIDTH // 2 - 50, 100))
