import random
import pygame

class Level3:
    """
    Level 3: Unstable Platform (Normal-based randomness)
    - Moving bin
    - Grip strength decays over time
    - Continuous slip check
    - Normal distribution for grab & drop
    """
    def __init__(self):
        self.config = {
            "name": "Level 3 (Unstable - Normal)",
            "grip_strength": 0.50,   # Mean initial grip
            "slip_probability": 0.005,
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
        self.grab_duration = 0.0
        self.decay_rate = 0.02  # grip loss per second

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
        
        # --- ATTEMPT START ---
        if claw.state == "LIFTING" and not self.active_attempt:
            self.active_attempt = True
            self.grab_duration = 0.0

        # --- CONTINUOUS DECAY + SLIP ---
        if claw.state in ["LIFTING", "RETURNING"] and claw.held_toy:
            self.grab_duration += dt
            
            # Decaying grip
            effective_grip = max(
                0.1,
                float(self.config["grip_strength"]) - (self.decay_rate * self.grab_duration)
            )

            # Dynamic slip probability
            dynamic_slip = float(self.config["slip_probability"]) + (1.0 - effective_grip) * 0.01
            
            if random.random() < dynamic_slip:
                claw.held_toy.grabbed = False
                claw.held_toy.y = bin_obj.y + bin_obj.height - 10
                claw.held_toy = None
                self.message = "Lost Grip!"

        # --- ATTEMPT END ---
        if self.active_attempt and claw.state == "IDLE":
            self.attempts_used += 1
            self.active_attempt = False

        # HUD
        if not self.message:
            status["message"] = (
                f"Toys: {self.toys_collected}/{self.toys_needed} | "
                f"Chances: {self.max_attempts - self.attempts_used}"
            )
        else:
            status["message"] = self.message

        self.message = ""
        self.last_score_awarded = 0

        # WIN / LOSE
        if self.toys_collected >= self.toys_needed:
            status["game_over"] = True
            status["success"] = True
            status["message"] = "Level Cleared!"
        elif self.attempts_used >= self.max_attempts and claw.state == "IDLE":
            status["game_over"] = True
            status["success"] = False
            status["message"] = "Out of Attempts!"

        return status

    # =====================================
    # NORMAL DISTRIBUTION INITIAL GRAB
    # =====================================
    def grip_success(self):
        mean = self.config["grip_strength"]
        std = 0.12  # Slightly more chaotic than Level 2

        grip_value = random.gauss(mean, std)
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
        # Slip handled continuously in update()
        return False

    # =====================================
    # NORMAL DISTRIBUTION DROP OFFSET
    # =====================================
    def get_drop_offset(self):
        r = self.config["drop_offset_range"]

        # Wider spread than Level 2
        offset = random.gauss(0, r / 2.5)

        offset = max(-r, min(r, offset))
        return offset

    def on_toy_collected(self):
        self.toys_collected += 1
        self.message = "COLLECTED!"