import pygame
from src.ui import Button, Slider
from src.utils import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, get_font, BG_COLOR, TEXT_COLOR
from src.machine import Machine

class GameManager:
    def __init__(self):
        self.state = "MENU" # MENU, MODE_SELECT, PRACTICE_PARAMS, GAME
        self.mode = None # "PRACTICE" or "GAME"
        # Initial config based on presets
        self.config = {
            "grip_strength": 0.8,
            "lift_speed": 5.0,
            "slip_chance": 0.1,
            "drop_delay": 0.5,
            "release_offset": 5.0,
            "bin_speed": 0.0
        }
        
        self.machine = None

        # UI Elements
        self.init_ui()

    def init_ui(self):
        center_x = SCREEN_WIDTH // 2
        
        # MAIN MENU
        self.btn_start = Button(center_x - 100, 200, 200, 50, "Start Game", action=lambda: self.set_state("MODE_SELECT"))
        self.btn_settings = Button(center_x - 100, 270, 200, 50, "Settings", action=lambda: print("Settings clicked"))
        self.btn_quit = Button(center_x - 100, 340, 200, 50, "Quit", action=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))

        # MODE SELECT
        self.btn_practice = Button(center_x - 100, 200, 200, 50, "Practice Mode", action=lambda: self.choose_mode("PRACTICE"))
        self.btn_game_mode = Button(center_x - 100, 270, 200, 50, "Game Mode", action=lambda: self.choose_mode("GAME"))
        self.btn_back_main = Button(center_x - 100, 340, 200, 50, "Back", action=lambda: self.set_state("MENU"))

        # PRACTICE CONFIG CHOICE
        self.btn_default = Button(center_x - 100, 200, 200, 50, "Default Settings", action=self.start_default_practice)
        self.btn_custom = Button(center_x - 100, 270, 200, 50, "Custom Settings", action=lambda: self.set_state("PRACTICE_CONFIG_CUSTOM"))
        self.btn_back_mode = Button(center_x - 100, 340, 200, 50, "Back", action=lambda: self.set_state("MODE_SELECT"))

        # PRACTICE CUSTOM CONFIG SLIDERS (Full set)
        start_y = 100
        gap = 70
        self.sliders = [
            Slider(center_x - 150, start_y, 300, 0.0, 1.0, 0.8, "Grip Strength"),
            Slider(center_x - 150, start_y + gap, 300, 1.0, 10.0, 5.0, "Lift Speed"),
            Slider(center_x - 150, start_y + gap*2, 300, 0.0, 1.0, 0.1, "Slip Chance"),
            Slider(center_x - 150, start_y + gap*3, 300, 0.0, 2.0, 0.5, "Drop Delay (s)"),
            Slider(center_x - 150, start_y + gap*4, 300, 0.0, 50.0, 5.0, "Release Offset"),
            Slider(center_x - 150, start_y + gap*5, 300, 0.0, 10.0, 0.0, "Bin Speed")
        ]
        
        self.btn_start_custom = Button(center_x - 100, 520, 200, 50, "Start Session", action=self.start_custom_practice)
        self.btn_back_config = Button(10, 10, 100, 40, "Back", action=lambda: self.set_state("PRACTICE_PARAMS"))

    def set_state(self, state):
        self.state = state
        print(f"State changed to: {self.state}")

    def choose_mode(self, mode):
        self.mode = mode
        if mode == "PRACTICE":
            self.set_state("PRACTICE_PARAMS")
        else:
            # Game Mode logic (levels) - placeholder
            self.start_game()

    def start_default_practice(self):
        self.config = {
            "grip_strength": 0.8,
            "lift_speed": 5.0,
            "slip_chance": 0.1,
            "drop_delay": 0.5,
            "release_offset": 5.0,
            "bin_speed": 0.0
        }
        self.start_game()

    def start_custom_practice(self):
        # Apply slider values
        self.config["grip_strength"] = self.sliders[0].value
        self.config["lift_speed"] = self.sliders[1].value
        self.config["slip_chance"] = self.sliders[2].value
        self.config["drop_delay"] = self.sliders[3].value
        self.config["release_offset"] = self.sliders[4].value
        self.config["bin_speed"] = self.sliders[5].value
        
        self.start_game()

    def start_game(self):
        self.machine = Machine(self.config) 
        self.set_state("GAME")

    def update(self):
        if self.state == "GAME":
            if self.machine:
                self.machine.update()
            # Check for back to menu?
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.set_state("MENU")

    def draw(self, screen):
        screen.fill(BG_COLOR)
        
        if self.state == "MENU":
            self.draw_title(screen, "ClawMania")
            self.btn_start.draw(screen)
            self.btn_settings.draw(screen)
            self.btn_quit.draw(screen)
            
        elif self.state == "MODE_SELECT":
            self.draw_title(screen, "Select Mode")
            self.btn_practice.draw(screen)
            self.btn_game_mode.draw(screen)
            self.btn_back_main.draw(screen)

        elif self.state == "PRACTICE_PARAMS":
            self.draw_title(screen, "Practice Config")
            self.btn_default.draw(screen)
            self.btn_custom.draw(screen)
            self.btn_back_mode.draw(screen)

        elif self.state == "PRACTICE_CONFIG_CUSTOM":
            font = get_font(32)
            title_surf = font.render("Custom Settings", False, TEXT_COLOR)
            screen.blit(title_surf, (SCREEN_WIDTH//2 - 100, 40))
            
            for slider in self.sliders:
                slider.draw(screen)
            self.btn_start_custom.draw(screen)
            self.btn_back_config.draw(screen)

        elif self.state == "GAME":
            if self.machine:
                self.machine.draw(screen)
            # Draw HUD placeholders
            font = get_font(18)
            screen.blit(font.render("Press ESC to Exit", False, WHITE), (10, 10))

    def draw_title(self, screen, text):
        font = get_font(48)
        title_surface = font.render(text, False, TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        # Shadow
        shadow_surface = font.render(text, False, (30, 0, 30))
        screen.blit(shadow_surface, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_surface, title_rect)

    def handle_event(self, event):
        if self.state == "MENU":
            self.btn_start.handle_event(event)
            self.btn_settings.handle_event(event)
            self.btn_quit.handle_event(event)
            
        elif self.state == "MODE_SELECT":
            self.btn_practice.handle_event(event)
            self.btn_game_mode.handle_event(event)
            self.btn_back_main.handle_event(event)

        elif self.state == "PRACTICE_PARAMS":
            self.btn_default.handle_event(event)
            self.btn_custom.handle_event(event)
            self.btn_back_mode.handle_event(event)

        elif self.state == "PRACTICE_CONFIG_CUSTOM":
            for slider in self.sliders:
                slider.handle_event(event)
            self.btn_start_custom.handle_event(event)
            self.btn_back_config.handle_event(event)
