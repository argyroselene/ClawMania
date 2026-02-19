import pygame
from src.utils import SCREEN_WIDTH, SCREEN_HEIGHT, get_font, BLACK, WHITE, TEXT_COLOR

class MapScreen:
    def __init__(self, persistence, game_manager):
        self.persistence = persistence
        self.game_manager = game_manager
        
        self.scroll_x = 0
        self.max_scroll = 0
        self.min_scroll = - (5 * 250 - SCREEN_WIDTH + 100) # Assuming 5 levels, 250px spacing
        if self.min_scroll > 0: self.min_scroll = 0 # Don't scroll if content fits
        
        self.dragging = False
        self.last_mouse_x = 0
        
        self.node_radius = 40
        self.spacing = 250
        self.start_x = 150
        self.y_pos = SCREEN_HEIGHT // 2
        
        # Level Data
        self.levels = [
            {"index": 0, "cost": 0, "pos": (0, 0)}, # Level 1
            {"index": 1, "cost": 60, "pos": (0, 0)}, # Level 2
            {"index": 2, "cost": 150, "pos": (0, 0)}, # Level 3
            {"index": 3, "cost": 300, "pos": (0, 0)}, # Level 4
            {"index": 4, "cost": 500, "pos": (0, 0)}, # Level 5
        ]
        
        # Calculate positions locally but apply scroll on draw/click
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.dragging = True
                self.last_mouse_x = event.pos[0]
                
                # Check clicks on nodes
                self.check_node_click(event.pos)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx = event.pos[0] - self.last_mouse_x
                self.scroll_x += dx
                self.last_mouse_x = event.pos[0]
                
                # Clamp
                self.scroll_x = max(self.min_scroll, min(self.max_scroll, self.scroll_x))

    def check_node_click(self, mouse_pos):
        mx, my = mouse_pos
        for i, level in enumerate(self.levels):
            # Calculate actual screen position
            bx = self.start_x + i * self.spacing + self.scroll_x
            by = self.y_pos
            
            # Simple distance check
            dist = ((mx - bx)**2 + (my - by)**2)**0.5
            if dist < self.node_radius:
                self.on_node_click(i)
                break

    def on_node_click(self, index):
        if self.persistence.is_level_unlocked(index):
            print(f"Starting Level {index + 1}")
            self.game_manager.current_level_index = index
            self.game_manager.start_current_level()
        else:
            # Try to unlock
            prev_unlocked = (index == 0) or self.persistence.is_level_unlocked(index - 1)
            if not prev_unlocked:
                print("Must unlock previous level first!")
                return
            
            cost = self.levels[index]["cost"]
            if self.persistence.get_xp() >= cost:
                self.persistence.spend_xp(cost)
                self.persistence.unlock_level(index)
                print(f"Unlocked Level {index + 1}!")
            else:
                print("Not enough XP!")

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((30, 30, 40)) # Dark map bg
        
        # Draw Title
        title = get_font(40).render("World Map", True, WHITE)
        screen.blit(title, (20, 20))
        
        # Draw XP
        xp = self.persistence.get_xp()
        c_surf = get_font(30).render(f"XP: {xp}", True, (0, 255, 255)) # Cyan for XP
        screen.blit(c_surf, (SCREEN_WIDTH - 200, 20))
        
        # Draw Connecting Lines first
        for i in range(len(self.levels) - 1):
            x1 = self.start_x + i * self.spacing + self.scroll_x
            y1 = self.y_pos
            x2 = self.start_x + (i+1) * self.spacing + self.scroll_x
            y2 = self.y_pos
            
            if x2 < 0 or x1 > SCREEN_WIDTH: continue # Cull
            
            pygame.draw.line(screen, (100, 100, 100), (x1, y1), (x2, y2), 5)

        # Draw Nodes
        for i, level in enumerate(self.levels):
            x = self.start_x + i * self.spacing + self.scroll_x
            y = self.y_pos
            
            if x < -100 or x > SCREEN_WIDTH + 100: continue
            
            unlocked = self.persistence.is_level_unlocked(i)
            
            # Circle
            color = (50, 200, 50) if unlocked else (100, 100, 100)
            if not unlocked and (i > 0 and self.persistence.is_level_unlocked(i-1)):
                 # Next purchasable
                 color = (200, 150, 50)

            pygame.draw.circle(screen, color, (int(x), int(y)), self.node_radius)
            pygame.draw.circle(screen, WHITE, (int(x), int(y)), self.node_radius, 3)
            
            # Text / Lock
            font = get_font(24)
            if unlocked:
                lbl = font.render(str(i + 1), True, WHITE)
                screen.blit(lbl, (x - lbl.get_width()//2, y - lbl.get_height()//2))
            else:
                # Lock Icon (simplistic)
                # Draw Lock
                rect = pygame.Rect(0, 0, 20, 15)
                rect.center = (x, y + 5)
                pygame.draw.rect(screen, (50, 50, 50), rect)
                pygame.draw.arc(screen, (50, 50, 50), (x - 7, y - 10, 14, 15), 0, 3.14, 2)
                
                # Cost below
                c_font = get_font(18)
                cost_txt = c_font.render(f"{level['cost']} XP", True, (0, 255, 255))
                screen.blit(cost_txt, (x - cost_txt.get_width()//2, y + 50))
