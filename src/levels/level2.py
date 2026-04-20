import random

class Level2:
    """
    Level 2: Simple Collection (3 toys, 5 chances)
    Now uses NORMAL distribution for:
    - Grip Strength
    - Drop Offset
    """
    def __init__(self):
        self.config = {
            "name": "Level 2 (Normal)",
            "grip_strength": 0.60, 
            "slip_probability": 0.10,
            "drop_offset_range": 5.0,
            "control_time": 9.0,
            "bin_speed": 1.0, 
            "toy_type": "single",
            "toy_fixed_position": True
        }
        
        # State Tracking
        self.toys_collected = 0
        self.toys_needed = 3
        self.max_attempts = 5
        self.attempts_used = 0

        self.level_score = 0
        self.last_score_awarded = 0
        self.message = ""
        
        self.active_attempt = False
        self.slip_checked = False

    def get_config(self):
        return self.config

    def update(self, dt, claw, toys, bin_obj):
        status = {
            "game_over": False,
            "success": False,
            "message": "",
            "score_awarded": self.last_score_awarded,
            "total_score": self.level_score,
            "toys_collected": self.toys_collected,
            "toys_needed": self.toys_needed
        }
        
        # --- DETECT ATTEMPT START ---
        if claw.state == "LIFTING" and not self.active_attempt:
            self.active_attempt = True
            self.slip_checked = False

        # --- SLIP CHECK ---
        if claw.state in ["LIFTING", "RETURNING"] and claw.held_toy and not self.slip_checked:
            if self.check_slip():
                claw.held_toy.grabbed = False
                claw.held_toy.y = bin_obj.y + bin_obj.height - 10
                claw.held_toy = None
                
                self.message = "Slipped!"
            self.slip_checked = True

        # --- DETECT ATTEMPT END ---
        if self.active_attempt and claw.state == "IDLE":
            self.attempts_used += 1
            self.active_attempt = False

        # HUD Message
        if not self.message:
            status["message"] = f"Toys: {self.toys_collected}/{self.toys_needed} | Chances: {self.max_attempts - self.attempts_used}"
        else:
            status["message"] = self.message

        # Reset transient feedback
        self.message = ""
        self.last_score_awarded = 0

        # Win/Loss
        if self.toys_collected >= self.toys_needed:
            status["game_over"] = True
            status["success"] = True
            status["message"] = "Level Cleared!"
        elif self.attempts_used >= self.max_attempts and claw.state == "IDLE":
            status["game_over"] = True
            status["success"] = False
            status["message"] = "Out of Attempts!"

        return status

    
    def grip_success(self):
        mean = self.config["grip_strength"]
        std = 0.1  # Balanced variation

        grip_value = random.gauss(mean, std)

        # Clamp between 0 and 1
        grip_value = max(0.0, min(1.0, grip_value))

        return random.random() <= grip_value

    def resolve_grab(self, claw_rect, toys):
        cx, cy, cw, ch = claw_rect

        for toy in toys:
            if toy.grabbed:
                continue
            
            toy_left = toy.x
            toy_top = toy.y - toy.height
            
            if (cx < toy_left + toy.width and cx + cw > toy_left and
                cy < toy.y and cy + ch > toy_top):
                
                if self.grip_success():
                    toy.grabbed = True
                    return toy

        return None


    def check_slip(self):
        return random.random() < self.config["slip_probability"]

    def get_drop_offset(self):
        r = self.config["drop_offset_range"]

        # 99% of values within range
        offset = random.gauss(0, r / 3)

        # Clamp to range
        offset = max(-r, min(r, offset))

        return offset


    def on_toy_collected(self, toy=None):
        score = 100 
        self.toys_collected += 1
        self.level_score += score
        self.last_score_awarded = score
        self.message = f"Score! +{score}"