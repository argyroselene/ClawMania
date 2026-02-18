import random
import pygame

class Level3:
    """
    Level 3: Unstable Platform
    - Moving bin (bin_speed > 0)
    - Grip strength decays over time while holding
    - Continuous slip check while lifting/returning
    - Larger drop offset
    """
    def __init__(self):
        self.config = {
            "name": "Level 3 (Unstable)",
            "grip_strength": 0.50, # Initial grip
            "slip_probability": 0.005, # Per-frame baseline slip probability
            "drop_offset_range": 10.0,
            "control_time": 7.0,
            "bin_speed": 1.5, 
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
        self.slip_checked = False # Not strictly used for single check here, but for state consistency
        self.grab_duration = 0.0
        self.decay_rate = 0.02 # Per second reduction in grip

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
            self.grab_duration = 0.0

        # --- CONTINUOUS SLIP CHECK & DECAY ---
        if claw.state in ["LIFTING", "RETURNING"] and claw.held_toy:
            self.grab_duration += dt
            
            # effective_grip = initial_grip - (decay_rate * duration)
            effective_grip = max(0.1, float(self.config["grip_strength"]) - (self.decay_rate * self.grab_duration))
            
            # Dynamic slip probability: baseline + penalty for weak grip
            # Increase base probability as grip decays
            dynamic_slip = float(self.config["slip_probability"]) + (1.0 - effective_grip) * 0.01
            
            if random.random() < dynamic_slip:
                # Apply slip
                claw.held_toy.grabbed = False
                # Reset position to bin
                claw.held_toy.y = bin_obj.y + bin_obj.height - 10
                claw.held_toy = None
                self.message = "Lost Grip!"

        # --- DETECT ATTEMPT END (Cycle Complete) ---
        if self.active_attempt and claw.state == "IDLE":
             self.attempts_used += 1
             self.active_attempt = False

        # Status HUD Message
        if not self.message:
            status["message"] = f"Toys: {self.toys_collected}/{self.toys_needed} | Chances: {self.max_attempts - self.attempts_used}"
        else:
            status["message"] = self.message

        # Reset transient feedback
        self.message = ""
        self.last_score_awarded = 0

        # Win/Loss Conditions
        if self.toys_collected >= self.toys_needed:
            status["game_over"] = True
            status["success"] = True
            status["message"] = "Level Cleared!"
        elif self.attempts_used >= self.max_attempts and claw.state == "IDLE":
             status["game_over"] = True
             status["success"] = False
             status["message"] = "Out of Attempts!"

        return status

    def on_toy_collected(self):
        self.toys_collected += 1
        self.message = "COLLECTED!"

    def resolve_grab(self, claw_rect, toys):
        cx, cy, cw, ch = claw_rect
        for toy in toys:
            if toy.grabbed:
                continue
            
            # AABB collision check
            toy_left = toy.x
            toy_top = toy.y - toy.height
            
            if (cx < toy_left + toy.width and cx + cw > toy_left and
                cy < toy.y and cy + ch > toy_top):
                
                # Initial grab probability
                if random.random() <= float(self.config["grip_strength"]):
                    toy.grabbed = True
                    return toy
        return None

    def check_slip(self):
        # Continuous check handled in update() for Level 3
        return False

    def get_drop_offset(self):
        r = self.config["drop_offset_range"]
        return random.uniform(-r, r)
