import random
import pygame

class AIMode:
    def __init__(self):
        self.config = {
            "name": "AI Mode",
            "grip_strength": 0.90,        
            "slip_probability": 0.02,     
            "drop_offset_range": .5,     
            "control_time": 12.0,
            "bin_speed": 0,
            "num_toys": 7
        }

        self.slip_checked = False
        self.active_attempt = False
        
        # Turn state
        self.total_turns_allowed = 6
        self.turns_played = 0
        self.player_turns_left = 3
        self.ai_turns_left = 3
        
        # Random first turn: "PLAYER" or "AI"
        self.current_turn = random.choice(["PLAYER", "AI"])
        self.turn_state = "WAITING" # WAITING, PLAYING, FINISHED_TURN
        
        self.scores = {"PLAYER": 0, "AI": 0}
        
        # For AI auto movement
        self.ai_target_x = None
        self.turn_end_timer = 0
        
        # Load heart sprite
        from src.utils import load_image
        self.heart_img = load_image("heart.png", 30, 30) # Slightly smaller for HUD

    def get_config(self):
        return self.config

    def is_ai_turn(self):
        return self.current_turn == "AI"

    def update(self, dt, claw, toys, bin_obj):
        status = {"game_over": False, "success": False, "message": "", "is_tie": False}
        
        if self.turns_played >= self.total_turns_allowed:
            status["game_over"] = True
            p_score = self.scores["PLAYER"]
            a_score = self.scores["AI"]
            
            if p_score > a_score:
                status["success"] = True
                status["message"] = "YOU WIN!"
            elif p_score < a_score:
                status["success"] = False
                status["message"] = "AI WINS!"
            else:
                status["success"] = False # Not a win
                status["is_tie"] = True
                status["message"] = "IT'S A TIE!"
            return status

        # --- DETECT ATTEMPT START ---
        if claw.state == "LIFTING" and not self.active_attempt:
            self.active_attempt = True
            self.slip_checked = False

        if claw.state == "LIFTING" and claw.held_toy and not self.slip_checked:
            if random.random() <= self.config["slip_probability"]:
                self.apply_slip(claw, bin_obj)
                status["message"] = "Slipped!"
            self.slip_checked = True
            
        if self.turn_state == "PLAYING" and claw.state == "IDLE" and self.active_attempt:
            # Turn ended! Wait for toys to drop and settle
            self.active_attempt = False
            self.turn_state = "FINISHED_TURN"
            self.turn_end_timer = pygame.time.get_ticks()

        if self.turn_state == "FINISHED_TURN":
            if pygame.time.get_ticks() - getattr(self, 'turn_end_timer', 0) > 2500: # 2.5 seconds delay
                if self.current_turn == "PLAYER":
                    self.player_turns_left -= 1
                else:
                    self.ai_turns_left -= 1
                    
                self.turns_played += 1
                self.turn_state = "WAITING"
                if self.turns_played < self.total_turns_allowed:
                    self.current_turn = "AI" if self.current_turn == "PLAYER" else "PLAYER"
            
        # Manage AI Turn
        if self.current_turn == "AI" and self.turn_state == "WAITING":
            # Just start the attempt automatically
            self.turn_state = "PLAYING"
            self.ai_target_x = self.pick_ai_target(toys, bin_obj)

        elif self.current_turn == "PLAYER" and self.turn_state == "WAITING":
            if claw.state == "DROPPING" or self.active_attempt:
                 self.turn_state = "PLAYING"
            
        # Move AI Claw automatically
        if self.current_turn == "AI" and self.turn_state == "PLAYING" and claw.state == "IDLE":
            if self.ai_target_x is not None:
                # Move towards target
                diff = self.ai_target_x - claw.x
                if abs(diff) > claw.move_speed:
                    claw.x += claw.move_speed if diff > 0 else -claw.move_speed
                else:
                    claw.x = self.ai_target_x
                    claw.state = "DROPPING"
                    self.active_attempt = True # Trigger attempt visually
                    self.ai_target_x = None

        # UI message
        turns_left = self.total_turns_allowed - self.turns_played
        turn_owner = "PLAYER" if self.current_turn == "PLAYER" else "AI"
        turn_text = f"{turn_owner}'s Turn! ({turns_left} turns left)"
        if self.turn_state == "FINISHED_TURN":
            turn_text = "Switching turns..."
            
        status["message"] = turn_text
        return status

    def draw_hud(self, screen):
        from src.utils import get_font, WHITE, SCREEN_WIDTH, DEEP_PURPLE
        font = get_font(28)
        
        # Player Score Box
        p_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, 10, 200, 45)
        pygame.draw.rect(screen, (0, 0, 100, 180), p_rect)
        pygame.draw.rect(screen, (0, 200, 255), p_rect, 2)
        p_surf = font.render(f"PLAYER: {self.scores['PLAYER']}", True, WHITE)
        screen.blit(p_surf, (p_rect.centerx - p_surf.get_width()//2, p_rect.centery - p_surf.get_height()//2))

        # AI Score Box
        a_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, 10, 200, 45)
        pygame.draw.rect(screen, (100, 0, 0, 180), a_rect)
        pygame.draw.rect(screen, (255, 100, 0), a_rect, 2)
        a_surf = font.render(f"AI: {self.scores['AI']}", True, WHITE)
        screen.blit(a_surf, (a_rect.centerx - a_surf.get_width()//2, a_rect.centery - a_surf.get_height()//2))
        
        # Turn Indicator
        turn_owner = "PLAYER" if self.current_turn == "PLAYER" else "AI"
        color = (0, 255, 255) if turn_owner == "PLAYER" else (255, 100, 100)
        indicator_text = f"{turn_owner}'S TURN"
        if self.turn_state == "FINISHED_TURN":
            indicator_text = "PREPARING..."
            color = WHITE
            
        ind_surf = get_font(20).render(indicator_text, True, color)
        screen.blit(ind_surf, (SCREEN_WIDTH // 2 - ind_surf.get_width()//2, 65))

        # Hearts for turns left
        if self.heart_img:
            # Player Hearts (Top Left)
            for i in range(max(0, self.player_turns_left)):
                screen.blit(self.heart_img, (10 + i * 35, 15))
            
            # AI Hearts (Top Right)
            for i in range(max(0, self.ai_turns_left)):
                # Draw from right to left
                screen.blit(self.heart_img, (SCREEN_WIDTH - 40 - i * 35, 15))

    def pick_ai_target(self, toys, bin_obj):
        # Pick a regular ungrabbed toy
        available_toys = [t for t in toys if not t.grabbed and not t.in_basket]
        if not available_toys:
            # Drop randomly in the bin if no toys
            return random.uniform(bin_obj.x + 40, bin_obj.x + bin_obj.width - 40)
            
        target_toy = random.choice(available_toys)
        # Target center of toy with a gaussian error
        toy_center_x = target_toy.x + target_toy.width // 2
        # std_dev of 15 means it'll often be close, but sometimes miss completely
        target_x = random.gauss(toy_center_x, 15) 
        
        # clamp to bin bounds
        min_x, max_x = bin_obj.x + 20, bin_obj.x + bin_obj.width - 20
        return max(min_x, min(target_x, max_x))

    def on_toy_collected(self, toy=None):
        # Ensure we can handle toy object or None
        points = 10 if toy is None else toy.points
        self.scores[self.current_turn] += points

    def resolve_grab(self, claw_rect, toys):
        # Reuse logic from Level 1
        cx, cy, cw, ch = claw_rect
        claw_center_x = cx + cw // 2

        best_toy = None
        min_dist = float('inf')

        for toy in toys:
            if toy.grabbed:
                continue

            # AABB
            toy_left = toy.x
            toy_top = toy.y - toy.height
            
            if (cx < toy_left + toy.width and cx + cw > toy_left and
                cy < toy.y and cy + ch > toy_top):
                
                # Calculate distance to center
                toy_center_x = toy.x + toy.width // 2
                dist = abs(claw_center_x - toy_center_x)
                
                if dist < min_dist:
                    min_dist = dist
                    best_toy = toy

        if best_toy:
             # Easier probabilistic grip
            if random.random() <= self.config["grip_strength"]:
                best_toy.grabbed = True
                return best_toy
                
        return None

    def apply_slip(self, claw, bin_obj=None):
        if claw.held_toy:
            toy = claw.held_toy
            toy.grabbed = False
            # If bin_obj is provided, reset to its floor
            if bin_obj:
                toy.y = bin_obj.y + bin_obj.height - 10
            claw.held_toy = None

    def get_drop_offset(self):
        r = self.config["drop_offset_range"]
        return random.uniform(-r, r)
