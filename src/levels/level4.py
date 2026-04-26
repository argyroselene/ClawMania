import random

class Level4:
    """
    Level 4: Pressure
    - Timer: 5 seconds
    - High Difficulty
    """
    def __init__(self):
        self.config = {
            "name": "Level 4 (High Pressure)",
            "grip_strength": 0.40, 
            "slip_probability": 0.05,
            "drop_offset_range": 15.0,
            "control_time": 5.0,
            "bin_speed": 2.0,
            "toy_type": "single",
            "toy_fixed_position": False
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
        
        # Attempt tracking done in Machine? 
        # Machine calls check_slip or we handle it here
        # Similar logic to Level 2/3
        
        # For brevity, reusing basic logic
        if claw.state == "LIFTING" and not self.active_attempt:
            self.active_attempt = True
            self.slip_checked = False
            
        if claw.state in ["LIFTING", "RETURNING"] and claw.held_toy and not self.slip_checked:
             if random.random() < self.config["slip_probability"]:
                 self.apply_slip(claw, bin_obj)
                 self.message = "Slipped!"
             self.slip_checked = True

        if self.active_attempt and claw.state == "IDLE":
             self.attempts_used += 1
             self.active_attempt = False

        if not self.message:
            status["message"] = f"Toys: {self.toys_collected}/{self.toys_needed}"
        else:
            status["message"] = self.message

        self.message = ""
        self.last_score_awarded = 0

        if self.toys_collected >= self.toys_needed:
            status["game_over"] = True
            status["success"] = True
            status["message"] = "Level Cleared!"
        elif self.attempts_used >= self.max_attempts and claw.state == "IDLE":
             status["game_over"] = True
             status["success"] = False
             status["message"] = "Out of Attempts!"

        return status

    def on_toy_collected(self, toy=None):
        self.toys_collected += 1
        self.message = "COLLECTED!"

    def resolve_grab(self, claw_rect, toys):
        # Similar logic
        cx, cy, cw, ch = claw_rect
        for toy in toys:
            if toy.grabbed: continue
            if (cx < toy.x + toy.width and cx + cw > toy.x and cy < toy.y and cy + ch > toy.y - toy.height):
                if random.random() <= self.config["grip_strength"]:
                    toy.grabbed = True
                    return toy
        return None

    def apply_slip(self, claw, bin_obj):
        if claw.held_toy:
            claw.held_toy.grabbed = False
            if bin_obj: claw.held_toy.y = bin_obj.y + bin_obj.height - 10
            claw.held_toy = None

    def get_drop_offset(self):
        return random.uniform(-15.0, 15.0)
