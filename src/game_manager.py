import pygame
from src.ui import Button, Slider
from src.utils import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, get_font, BG_COLOR, TEXT_COLOR, load_image
from src.machine import Machine

# Import Levels
try:
    from src.levels.level1 import Level1
    from src.levels.level2 import Level2
    from src.levels.level3 import Level3
except ImportError:
    # Fallback/Placeholder
    Level1 = None
    Level2 = None
    Level3 = None

class GameManager:
    def __init__(self):
        self.state = "MENU" # MENU, MODE_SELECT, PRACTICE_PARAMS, GAME, LEVEL_INTRO
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
        
        # Level System
        self.levels = [Level1, Level2, Level3] # registry
        self.current_level_index = 0

        # Assets
        self.menu_background = load_image("game_bg.png", SCREEN_WIDTH, SCREEN_HEIGHT) # Load global background

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
        
        # LEVEL INTRO DIALOG
        self.btn_start_level = Button(center_x - 100, 300, 200, 50, "Start Level", action=self.start_current_level)

        # LEVEL COMPLETE / GAME OVER UI
        self.btn_menu_lc = Button(center_x - 100, 370, 200, 50, "Main Menu", action=lambda: self.set_state("MENU"))
        # Next level button removed for auto progression, or we can use it on the "Win" screen to confirm proceeding?
        # Requirement: "after completing it will automaticallly go to level 2"
        # Let's interpret "automatically" as transition to Level 2 Intro.
        # But we probably want a "Next Level" button on the win screen so the player can see their score first.
        # Wait, user said "automaticallly go to level 2". Let's show "Level Complete", wait 2 seconds, then go to Level 2 Intro?
        # Or just a "Next" button is safer for UX.
        # User: "automaticallly go to level 2 else it will show game over"
        # I will make it: Win Screen -> Timer (2s) -> Next Level Intro.
        
        self.level_transition_timer = 0

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
            # Start Game Mode Sequence
            self.current_level_index = 0
            self.set_state("LEVEL_INTRO")

    def start_current_level(self):
        index = self.current_level_index
        if 0 <= index < len(self.levels):
            lvl_class = self.levels[index]
            if lvl_class:
                level_logic = lvl_class()
                config = level_logic.get_config()
                self.machine = Machine(config, level_logic=level_logic)
                self.set_state("GAME")
            else:
                print("Level class not found.")
        else:
            print("Level index out of bounds.")
            self.set_state("MENU")

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
        # Starts PRACTICE mode (no level logic)
        self.machine = Machine(self.config) 
        self.mode = "PRACTICE"
        self.set_state("GAME")

    def update(self):
        if self.state == "GAME":
            if self.machine:
                self.machine.update()
                
                # Check for Level Win / Loss
                if self.mode == "GAME" and self.machine.game_over:
                    if self.machine.won:
                        # Victory Logic with auto-progression timer
                        if self.level_transition_timer == 0:
                            self.level_transition_timer = pygame.time.get_ticks()
                        
                        # Wait 2 seconds then next level
                        if pygame.time.get_ticks() - self.level_transition_timer > 2000:
                            self.level_transition_timer = 0
                            self.current_level_index += 1
                            if self.current_level_index < len(self.levels):
                                self.set_state("LEVEL_INTRO")
                            else:
                                # All levels done
                                print("All levels completed!")
                                self.set_state("MENU") # Or a "Victory" screen
                    else:
                        # Loss Logic - Game Over screen (handled in draw/event)
                        pass

            # Check for back to menu?
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.set_state("MENU")

    def draw(self, screen):
        # Draw Background
        if self.menu_background and self.state != "GAME":
             screen.blit(self.menu_background, (0, 0))
        elif self.state != "GAME":
             screen.fill(BG_COLOR)
        
        if self.state == "MENU":
            # self.draw_title(screen, "ClawMania") # Removed as per user request
            self.btn_start.draw(screen)
            self.btn_settings.draw(screen)
            self.btn_quit.draw(screen)
            
        elif self.state == "MODE_SELECT":
            self.btn_practice.draw(screen)
            self.btn_game_mode.draw(screen)
            self.btn_back_main.draw(screen)
            
        elif self.state == "LEVEL_INTRO":
            # Dialog Box Style
            # Draw semi-transparent background
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 100))
            screen.blit(s, (0,0))
            
            # Dialog Box
            dialog_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 150, 400, 300)
            pygame.draw.rect(screen, BG_COLOR, dialog_rect)
            pygame.draw.rect(screen, WHITE, dialog_rect, 3)
            
            # Text
            level_num = self.current_level_index + 1
            font = get_font(36)
            title = font.render(f"Level {level_num}", True, TEXT_COLOR)
            screen.blit(title, (dialog_rect.centerx - title.get_width()//2, dialog_rect.y + 40))
            
            # Button
            self.btn_start_level.rect.center = (dialog_rect.centerx, dialog_rect.y + 200)
            self.btn_start_level.draw(screen)

        elif self.state == "PRACTICE_PARAMS":

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
                
                # If Game Over/Level Complete, draw overlay logic
                if self.machine.game_over:
                     # Draw simple overlay
                     s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                     s.fill((0, 0, 0, 150))
                     screen.blit(s, (0, 0))
                     
                     msg = "LEVEL COMPLETE!" if self.machine.won else "GAME OVER"
                     color = (0, 255, 0) if self.machine.won else (255, 0, 0)
                     
                     font = get_font(48)
                     res_surf = font.render(msg, True, color)
                     screen.blit(res_surf, (SCREEN_WIDTH//2 - res_surf.get_width()//2, SCREEN_HEIGHT//2 - 50))
                     
                     if not self.machine.won:
                         self.btn_menu_lc.draw(screen)
                     else:
                         # Show "Loading..." or just wait for auto transition
                         wait_surf = get_font(24).render("Proceeding...", True, WHITE)
                         screen.blit(wait_surf, (SCREEN_WIDTH//2 - wait_surf.get_width()//2, SCREEN_HEIGHT//2 + 50))

    def handle_event(self, event):
        if self.state == "MENU":
            self.btn_start.handle_event(event)
            self.btn_settings.handle_event(event)
            self.btn_quit.handle_event(event)
            
        elif self.state == "MODE_SELECT":
            self.btn_practice.handle_event(event)
            self.btn_game_mode.handle_event(event)
            self.btn_back_main.handle_event(event)
            
        elif self.state == "LEVEL_INTRO":
            self.btn_start_level.handle_event(event)

        elif self.state == "PRACTICE_PARAMS":
            self.btn_default.handle_event(event)
            self.btn_custom.handle_event(event)
            self.btn_back_mode.handle_event(event)

        elif self.state == "PRACTICE_CONFIG_CUSTOM":
            for slider in self.sliders:
                slider.handle_event(event)
            self.btn_start_custom.handle_event(event)
            self.btn_back_config.handle_event(event)
            
        elif self.state == "GAME":
            # Handle overlay buttons if game over
            if self.machine and self.machine.game_over:
                if not self.machine.won:
                    self.btn_menu_lc.handle_event(event)

    def draw_title(self, screen, text):
        font = get_font(48)
        title_surface = font.render(text, False, TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        # Shadow
        shadow_surface = font.render(text, False, (30, 0, 30))
        screen.blit(shadow_surface, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_surface, title_rect)
