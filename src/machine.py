import pygame
import random
from src.claw import Claw
from src.bin import Bin
from src.toy import Toy
from src.utils import SCREEN_WIDTH, SCREEN_HEIGHT, load_image, get_font, WHITE, BLACK, load_sound, DEEP_PURPLE

class Machine:
    def __init__(self, config, level_logic=None, persistence=None):
        self.config = config
        self.level_logic = level_logic
        self.persistence = persistence
        
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
        self.is_tie = False
        
        # Timer System
        self.attempt_active = False # True when "START" pressed, False when IDLE/Frozen
        self.attempt_timer = 0.0
        self.time_limit = 10.0 # Default fallback
        if self.level_logic:
             # Level specific timer values
             level_name = self.level_logic.config.get("name", "")
             
             if hasattr(self.level_logic, "config") and "control_time" in self.level_logic.config:
                 self.time_limit = self.level_logic.config["control_time"]
             else:
                 # Fallback logic based on name?
                 if "Level 1" in level_name: self.time_limit = 12.0
                 elif "Level 2" in level_name: self.time_limit = 9.0
                 elif "Level 3" in level_name: self.time_limit = 7.0
                 # etc.
        
       
        
        # Popup Feedback
        self.popup_message = None
        self.popup_end_time = 0

        # Load Sprites
        self.heart_img = load_image("heart.png", 40, 40)
        self.win_img = load_image("win.png", 500, 350)
        self.defeat_img = load_image("lose.png", 500, 350)
        self.tie_img = load_image("tie.png", 500, 350)

        # Load Sounds
        self.drop_snd = load_sound("drop.mp3")
        self.win_snd = load_sound("win.mp3")
        self.lose_snd = load_sound("lose.mp3")
        self.result_sound_played = False

    def populate_toys(self):
        # Create a few rows of toys inside the bin
        start_x = self.bin.x + 20
        start_y = self.bin.y + self.bin.height - 10
        
        num_toys = 5
        if hasattr(self, "level_logic") and self.level_logic:
             if hasattr(self.level_logic, "config") and "num_toys" in self.level_logic.config:
                 num_toys = self.level_logic.config["num_toys"]

        for i in range(num_toys):
             # varying sizes
            size = random.choice(["small", "medium", "large"])
            # Randomly distribute across the bin width
            spawn_x = random.randint(int(self.bin.x + 20), int(self.bin.x + self.bin.width - 60))
            
            # Random toy image ID (1, 2, or 3)
            toy_id = random.randint(1, 3)
            
            toy = Toy(spawn_x, start_y, size, toy_id=toy_id)
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
                         
                         # Coin Reward
                         if self.persistence:
                             self.persistence.add_xp(toy.points) # XP = Score
                             self.show_popup(f"COLLECTED! +{toy.points} XP")
                             
                         # Update stats
                         if self.level_logic and hasattr(self.level_logic, "on_toy_collected"):
                             self.level_logic.on_toy_collected(toy)
            
        # 3. Update Claw
        # 3. Update Claw
        prev_state = self.claw.state
        
        # Timer Logic
        if self.attempt_active and self.claw.state == "IDLE":
             self.attempt_timer -= dt
             if self.attempt_timer <= 0:
                 self.fail_attempt()
        
        
        
        # Check if user tries to move without Start
        if not self.attempt_active and self.claw.state == "IDLE":
             
             pass 
             
             
        self.claw.update(allow_input=self.attempt_active) # I'll add allow_input to Claw.update
        
        
        if prev_state != "IDLE" and self.claw.state == "IDLE":
            if self.attempt_active:
                self.attempt_active = False # Reset for next turn
        
        # 4. Check Interactions
        
        # STATE CHANGE: GRABBING -> LIFTING (The moment of grab attempt)
        if prev_state == "GRABBING" and self.claw.state == "LIFTING":
            self.attempt_grab()
        
        if self.level_logic:
             pass # Logic handled in level_logic.update() usually
             
        elif self.claw.state in ["LIFTING", "RETURNING"] and self.claw.held_toy:
            self.check_slip()
            
        # STATE CHANGE: RELEASING -> IDLE (Drop toy)
        if self.claw.state == "RELEASING" and prev_state != "RELEASING":
            self.drop_toy()

        # Update held toy position
        if self.claw.held_toy:
            self.claw.held_toy.x = self.claw.x - self.claw.held_toy.width // 2
            
            sway = 0
            if self.claw.state == "RETURNING":
                sway = 10 # Drag behind slightly
            elif self.claw.state == "MOVING": # If we had moving state for manual control
                 pass
            
            self.claw.held_toy.x = self.claw.x - self.claw.held_toy.width // 2 + sway
            self.claw.held_toy.y = self.claw.y + 50 # Moved up slightly to be more "in" the palm

        # 5. Level Logic Update (Win/Loss/Slip)
        if self.level_logic and not self.game_over:
            status = self.level_logic.update(dt, self.claw, self.toys, self.bin)
            if status["game_over"]:
                self.game_over = True
                self.won = status["success"]
                self.is_tie = status.get("is_tie", False)
                if self.won and self.persistence:
                    self.persistence.add_xp(50) # Level bonus
                    status["message"] += " +50 XP!"
                self.last_result = status["message"]
                
                # Play Result Sound once
                if not self.result_sound_played:
                    if self.won:
                        if self.win_snd: self.win_snd.play()
                    else:
                        if self.lose_snd: self.lose_snd.play()
                    self.result_sound_played = True
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
        
        # HUD
        font = get_font(24)
        
        # Draw AI Mode HUD if applicable
        is_ai = hasattr(self.level_logic, "draw_hud")
        if is_ai:
            self.level_logic.draw_hud(screen)
        
        # Hide global score in AI Mode
        if not is_ai:
            score_surf = font.render(f"Score: {self.score}", False, DEEP_PURPLE)
            screen.blit(score_surf, (SCREEN_WIDTH - 150, 10))
            
        # Draw Win Probability if available
        if hasattr(self, 'win_probability') and self.win_probability is not None:
             prob_text = font.render(f"Win Prob: {self.win_probability:.1f}%", True, DEEP_PURPLE)
             
             bar_w = 150
             bar_h = 20
             bar_x = SCREEN_WIDTH - bar_w - 20
             bar_y = 70
             
             pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
             fill_w = int((self.win_probability / 100.0) * bar_w)
             if fill_w > 0:
                 r = min(255, max(0, int(255 * (100 - self.win_probability) / 50)))
                 g = min(255, max(0, int(255 * self.win_probability / 50)))
                 pygame.draw.rect(screen, (r, g, 0), (bar_x, bar_y, fill_w, bar_h))
             pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
             
             screen.blit(prob_text, (bar_x, bar_y - 25))
        
        # Level Stats HUD (Top Left)
        if self.level_logic and hasattr(self.level_logic, 'toys_collected'):
             # Toys Collected
             toys_remaining = max(0, self.level_logic.toys_needed - self.level_logic.toys_collected)
             toys_str = f"Toys Left: {toys_remaining}"
             toys_surf = font.render(toys_str, False, (0, 255, 255))
             screen.blit(toys_surf, (20, 10))
             
             # Timer Display
             if self.attempt_active:
                 t_color = (0, 255, 0) if self.attempt_timer > 3 else (255, 0, 0)
                 timer_surf = font.render(f"Time: {self.attempt_timer:.1f}", True, t_color)
                 screen.blit(timer_surf, (SCREEN_WIDTH//2 - 50, 60))
             
             # Chances
             rem_chances = self.level_logic.max_attempts - self.level_logic.attempts_used
             
             if self.heart_img:
                 for i in range(max(0, rem_chances)):
                     screen.blit(self.heart_img, (20 + i * 45, 40))
             else:
                 chances_str = f"Chances: {max(0, rem_chances)}" 
                 c_color = (255, 50, 50) if rem_chances <= 1 else (0, 255, 0)
                 chances_surf = font.render(chances_str, False, c_color)
                 screen.blit(chances_surf, (20, 40))
             
             # Feedback Message (Below stats)
             if self.last_result:
                 msg_surf = font.render(self.last_result, True, (255, 255, 0))
                 screen.blit(msg_surf, (20, 70))

        # Popup Message (Center) - White Style
        if self.popup_message and pygame.time.get_ticks() < self.popup_end_time:
            # Draw Box
            padding = 15
            pop_font = get_font(28)
            text_surf = pop_font.render(self.popup_message, True, BLACK)
            
            bg_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            bg_rect.inflate_ip(padding*2, padding)
            
            # Draw White Box with Shadow-like border
            pygame.draw.rect(screen, WHITE, bg_rect, border_radius=5)
            pygame.draw.rect(screen, (180, 180, 180), bg_rect, 2, border_radius=5)
            screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))
        else:
            self.popup_message = None # Reset

        if self.game_over:
             # 1. Dim the background scene
             overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
             overlay.fill((0, 0, 0, 160)) # Semi-transparent black
             screen.blit(overlay, (0, 0))

             # 2. Draw Result Image (Bright)
             result_img = None
             if self.is_tie:
                 result_img = self.tie_img
             else:
                 result_img = self.win_img if self.won else self.defeat_img
                 
             if result_img:
                 img_rect = result_img.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                 screen.blit(result_img, img_rect)
             else:
                 # Fallback to text
                 msg = self.last_result if self.last_result else ("LEVEL COMPLETE!" if self.won else "GAME OVER")
                 color = (255, 255, 0) if self.is_tie else ((0, 255, 0) if self.won else (255, 0, 0))
                 go_font = get_font(48)
                 go_surf = go_font.render(msg, False, color)
                 screen.blit(go_surf, (SCREEN_WIDTH//2 - go_surf.get_width()//2, SCREEN_HEIGHT//2))
        
        # Draw Start Button if needed
        if not self.attempt_active and not self.game_over and self.claw.state == "IDLE":
             # Reset Logic check: if chances > 0
             can_play = True
             if self.level_logic and hasattr(self.level_logic, "max_attempts"):
                 if self.level_logic.attempts_used >= self.level_logic.max_attempts:
                     can_play = False
             
             if self.level_logic and hasattr(self.level_logic, "is_ai_turn"):
                 if self.level_logic.is_ai_turn():
                     can_play = False
             
             if can_play:
                 # Draw "PRESS START" button or text
                 # Using a simple rect for now
                 btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 60, 150, 120, 50)
                 pygame.draw.rect(screen, (0, 200, 0), btn_rect)
                 pygame.draw.rect(screen, WHITE, btn_rect, 3)
                 
                 s_font = get_font(24)
                 lbl = s_font.render("START", True, WHITE)
                 screen.blit(lbl, (btn_rect.centerx - lbl.get_width()//2, btn_rect.centery - lbl.get_height()//2))
                 
                 
                 if pygame.mouse.get_pressed()[0]:
                     mx, my = pygame.mouse.get_pos()
                     if btn_rect.collidepoint(mx, my):
                         self.start_attempt()

    def show_popup(self, message, duration=1.0):
        self.popup_message = message
        self.popup_end_time = pygame.time.get_ticks() + int(duration * 1000)

    def drop_toy(self):
        if self.claw.held_toy:
            
            
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
            
            # Play drop sound
            if self.drop_snd:
                self.drop_snd.play()

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
        
        if random.random() < 0.01: 
             # Can calculate based on grip strength
             G = self.config.get("grip_strength", 0.8)
             # Higher grip = lower slip chance
             chance = self.config.get("slip_chance", 0.02 * (1.0 - G))
             
             if random.random() < chance:
                print(f"Slipped!")
                self.claw.held_toy.grabbed = False
                # Add some horizontal velocity on slip
                self.claw.held_toy.vx = random.uniform(-2, 2)
                # Gravity will take it down
                self.claw.held_toy = None
             
    def start_attempt(self):
        self.attempt_active = True
        self.attempt_timer = self.time_limit
        self.show_popup("GO!", 0.5)

    def fail_attempt(self):
        self.attempt_active = False
        self.show_popup("TIME UP!")
        # Consume chance logic
        if self.level_logic:
             self.level_logic.attempts_used += 1
