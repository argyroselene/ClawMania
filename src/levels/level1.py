import random

class Level1:
    """
    Level 1: Fair Start (Beginner-Friendly)

    Easier baseline:
    - Grip Strength: 0.95
    - Slip Probability: 0.02 (single check)
    - Drop Offset: ±2px
    """

    def __init__(self):
        self.config = {
            "name": "Fair Start",
            "grip_strength": 0.95,        # Increased
            "slip_probability": 0.02,     # Reduced
            "drop_offset_range": 2.0,     # Slightly smaller
            "control_time": 12.0,
            "bin_speed": 0
        }

        self.slip_checked = False
        self.active_attempt = False  # Track grab attempt lifecycle
        
        # New Win Condition State
        self.max_attempts = 5
        self.attempts_used = 0
        self.toys_collected = 0
        self.toys_needed = 3

    def get_config(self):
        return self.config

    def update(self, dt, claw, toys, bin_obj):
        status = {"game_over": False, "success": False, "message": ""}

        # --- DETECT ATTEMPT START ---
        if claw.state == "LIFTING" and not self.active_attempt:
            self.active_attempt = True
            self.slip_checked = False

        if claw.state == "LIFTING" and claw.held_toy and not self.slip_checked:
            if random.random() <= self.config["slip_probability"]:
                self.apply_slip(claw, bin_obj)
                status["message"] = "Slipped!"
            self.slip_checked = True

       
        if self.active_attempt and claw.state == "IDLE":
             self.attempts_used += 1
             self.active_attempt = False
             
             
             pass

        
        if self.toys_collected >= self.toys_needed:
            status["game_over"] = True
            status["success"] = True
            status["message"] = "Level Cleared!"
        elif self.attempts_used >= self.max_attempts:
            status["game_over"] = True
            status["success"] = False
            status["message"] = "Out of Chances!"
        else:
            toys_rem = self.toys_needed - self.toys_collected
            status["message"] = f"Toys Left: {toys_rem} | Chances: {self.max_attempts - self.attempts_used}"

        return status

    def on_toy_collected(self):
        self.toys_collected += 1

    def resolve_grab(self, claw_rect, toys):
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

    def check_win(self, toys, bin_obj):
        #tracking via on_toy_collected
        return False

