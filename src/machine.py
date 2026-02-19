import pygame
import random
from src.claw import Claw
from src.bin import Bin
from src.toy import Toy
from src.utils import SCREEN_WIDTH, SCREEN_HEIGHT, load_image, get_font, WHITE, BLACK

class Machine:
    def __init__(self, config, level_logic=None):
        self.config = config
        self.level_logic = level_logic
        
        # Load Background
        self.background = load_image("background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        
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
        self.game_over = False
        self.won = False
        
        # Popup Feedback
        self.popup_message = None
        self.popup_end_time = 0

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
        dt = 1/60.0 # Approx
        
        # 1. Update Bin
        self.bin.update()
        
        # 2. Update Toys (move with bin if not grabbed)
        bin_velocity = 0
        if self.bin.speed > 0:
            bin_velocity = self.bin.speed * self.bin.direction
            
        for toy in self.toys:
            toy.update(self.bin.x, bin_velocity)
            
            # Check for basket collection here
            if not toy.grabbed and not toy.in_basket:
                # Basket Rect (Visual)
                basket_rect = pygame.Rect(10, SCREEN_HEIGHT - 120, 130, 120)
                # Actual catch zone
                if basket_rect.colliderect(toy.rect):
                    # Check if deep enough
                     # Check if deep enough
                    if toy.y > SCREEN_HEIGHT - 120 and toy.on_ground:
                         # print(f"Collected: {toy.size}")
                         toy.in_basket = True
                         self.score += toy.points
                         self.last_result = f"Score! +{toy.points}"
                         self.show_popup("COLLECTED!")
                         # Update stats
                         if self.level_logic and hasattr(self.level_logic, "on_toy_collected"):
                             self.level_logic.on_toy_collected()
            
        # 3. Update Claw
        prev_state = self.claw.state
        self.claw.update()
        
        # 4. Check Interactions
        
        # STATE CHANGE: GRABBING -> LIFTING (The moment of grab attempt)
        if prev_state == "GRABBING" and self.claw.state == "LIFTING":
            self.attempt_grab()
            
        # STATE: LIFTING/RETURNING (Check for slip)
        # If level logic exists, it might handle slip internally in its update method
        # But we also have a dedicated check_slip here for legacy/practice.
        # Let's delegate if level_logic exists, otherwise use default.
        if self.level_logic:
             pass # Logic handled in level_logic.update() usually, or we call it explicitly?
             # Actually, Level1.update handles slip. So we skip default check_slip.
        elif self.claw.state in ["LIFTING", "RETURNING"] and self.claw.held_toy:
            self.check_slip()
            
        # STATE CHANGE: RELEASING -> IDLE (Drop toy)
        if self.claw.state == "RELEASING" and prev_state != "RELEASING":
            self.drop_toy()

        # Update held toy position
        if self.claw.held_toy:
            self.claw.held_toy.x = self.claw.x - self.claw.held_toy.width // 2
            # Positioning it "inside" the claw (claw is ~120px tall, so +60 puts it mid-bottom)
            # Positioning it "inside" the claw (claw is ~120px tall, so +60 puts it mid-bottom)
            # Add Sway based on claw movement
            sway = 0
            if self.claw.state == "RETURNING":
                sway = 10 # Drag behind slightly
            elif self.claw.state == "MOVING": # If we had moving state for manual control
                 pass
            
            self.claw.held_toy.x = self.claw.x - self.claw.held_toy.width // 2 + sway
            self.claw.held_toy.y = self.claw.y + 50 # Moved up slightly to be more "in" the palm

        # 5. Level Logic Update (Win/Loss/Slip)
        if self.level_logic:
            status = self.level_logic.update(dt, self.claw, self.toys, self.bin)
            if status["game_over"]:
                self.game_over = True
                self.won = status["success"]
                self.last_result = status["message"]
            elif status["message"]:
                 self.last_result = status["message"]

    def draw(self, screen):
        # Draw Background
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((50, 0, 50)) # Fallback color

        # Draw Bin
        # Draw Basket Back (Interior)
        basket_rect = pygame.Rect(10, SCREEN_HEIGHT - 120, 130, 120)
        pygame.draw.rect(screen, (100, 50, 10), basket_rect) # Darker interior
        
        self.bin.draw(screen)
        
        # Draw Toys (Unheld first, then held)
        for toy in self.toys:
           if not toy.grabbed:
               toy.draw(screen)

        # Draw Held Toy (Behind Claw for "Inside" look)
        if self.claw.held_toy:
             self.claw.held_toy.draw(screen)

        # Draw Claw
        self.claw.draw(screen)
             
        # Draw Basket Front (Rim)
        pygame.draw.rect(screen, (160, 82, 45), basket_rect, 5) # Lighter border
        # Label
        b_font = get_font(20)
        b_text = b_font.render("PRIZES", True, (255, 220, 180))
        screen.blit(b_text, (basket_rect.centerx - b_text.get_width()//2, basket_rect.y + 10))
        
        # Draw HUD (Score)
        # from src.utils import get_font, WHITE, BLACK # Removed local import
        font = get_font(24)
        score_surf = font.render(f"Score: {self.score}", False, WHITE)
        screen.blit(score_surf, (SCREEN_WIDTH - 150, 10))
        
        # Level Stats HUD (Top Left)
        if self.level_logic and hasattr(self.level_logic, 'toys_collected'):
             # Toys Collected
             toys_remaining = max(0, self.level_logic.toys_needed - self.level_logic.toys_collected)
             toys_str = f"Toys Left: {toys_remaining}"
             toys_surf = font.render(toys_str, False, (0, 255, 255))
             screen.blit(toys_surf, (20, 10))
             
             # Chances
             rem_chances = self.level_logic.max_attempts - self.level_logic.attempts_used
             chances_str = f"Chances: {max(0, rem_chances)}" 
             c_color = (255, 50, 50) if rem_chances <= 1 else (0, 255, 0)
             chances_surf = font.render(chances_str, False, c_color)
             screen.blit(chances_surf, (20, 40))
             
             # Feedback Message (Below stats)
             if self.last_result:
                 msg_surf = font.render(self.last_result, True, (255, 255, 0))
                 screen.blit(msg_surf, (20, 70))

        # Popup Message (Center)
        if self.popup_message and pygame.time.get_ticks() < self.popup_end_time:
            # Draw Box
            padding = 20
            pop_font = get_font(36)
            text_surf = pop_font.render(self.popup_message, True, WHITE)
            
            bg_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            bg_rect.inflate_ip(padding*2, padding)
            
            pygame.draw.rect(screen, (0, 0, 0, 200), bg_rect)
            pygame.draw.rect(screen, WHITE, bg_rect, 2)
            screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))
        else:
            self.popup_message = None # Reset

        if self.game_over:
             msg = "LEVEL COMPLETE!" if self.won else "GAME OVER"
             color = (0, 255, 0) if self.won else (255, 0, 0)
             go_surf = get_font(48).render(msg, False, color)
             screen.blit(go_surf, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50))

    def show_popup(self, message, duration=1.0):
        self.popup_message = message
        self.popup_end_time = pygame.time.get_ticks() + int(duration * 1000)

    def drop_toy(self):
        if self.claw.held_toy:
            # Drop it
            # Apply release offset
            
            offset = 0.0
            if self.level_logic:
                if hasattr(self.level_logic, "get_drop_offset"):
                     offset = self.level_logic.get_drop_offset()
            else:
                offset_magn = self.config.get("release_offset", 0.0)
                offset = random.uniform(-offset_magn, offset_magn)
            
            self.claw.held_toy.x += offset
            self.claw.held_toy.grabbed = False
            # Ensure gravity takes over
            self.claw.held_toy = None

    def attempt_grab(self):
        if self.level_logic:
            result_toy = self.level_logic.resolve_grab((self.claw.x - self.claw.width//2, self.claw.y, self.claw.width, self.claw.height), self.toys)
            if result_toy:
                self.claw.held_toy = result_toy
                result_toy.grabbed = True
                self.show_popup("GRABBED!")
            else:
                self.show_popup("MISSED!")
            return

        # Default Practice Mode Logic
        # ... (Legacy logic simplification for brevity or update?)
        # Let's keep legacy but update feedback
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
        
        if closest_toy and min_dist < 40:
             # ... Logic ...
            max_dist = 40.0
            alignment = max(0.0, 1.0 - (min_dist / max_dist))
            G = self.config.get("grip_strength", 0.8)
            T = closest_toy.difficulty_factor
            D = 1.0 
            P_grab = G * alignment * T * D
            
            if random.random() <= P_grab:
                self.claw.held_toy = closest_toy
                closest_toy.grabbed = True
                self.show_popup("GRABBED!")
            else:
                self.show_popup("MISSED!")
        else:
             self.show_popup("MISSED!")

    def check_slip(self):
        # Called every frame during LIFTING/RETURNING
        # Small chance to slip per frame
        if random.random() < 0.01: # 1% chance per frame to slip
             # Can calculate based on grip strength
             G = self.config.get("grip_strength", 0.8)
             # Higher grip = lower slip chance
             chance = 0.02 * (1.0 - G)
             
             if random.random() < chance:
                print(f"Slipped!")
                self.claw.held_toy.grabbed = False
                # Add some horizontal velocity on slip
                self.claw.held_toy.vx = random.uniform(-2, 2)
                # Gravity will take it down
                self.claw.held_toy = None
                self.show_popup("SLIPPED!")
