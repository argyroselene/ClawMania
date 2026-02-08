from src.utils import WHITE, BLACK, GRAY, LIGHT_GRAY, HOT_PINK, DEEP_PURPLE, NEON_GREEN, CYAN, PIXEL_YELLOW, BG_COLOR, UI_BG_COLOR, TEXT_COLOR, HIGHLIGHT_COLOR, get_font
import pygame

class Button:
    def __init__(self, x, y, width, height, text, action=None, color=UI_BG_COLOR, hover_color=HOT_PINK, text_color=TEXT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = get_font(24)
        self.border_color = CYAN

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        current_color = self.hover_color if is_hovered else self.color
        current_text_color = DEEP_PURPLE if is_hovered else self.text_color
        
        # Pixelated shadow
        pygame.draw.rect(screen, (30, 0, 30), (self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height))
        
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 3) # Thicker border
        
        text_surf = self.font.render(self.text, False, current_text_color) # False for aliasing (pixel look)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.handle_rect = pygame.Rect(x, y - 5, 20, 30) # Wider handle
        self.update_handle_pos()

    def update_handle_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.left + self.rect.width * ratio

    def draw(self, screen):
        # Draw label
        font = get_font(20)
        label_surf = font.render(f"{self.label}: {self.value:.2f}", False, CYAN)
        screen.blit(label_surf, (self.rect.x, self.rect.y - 25))
        
        # Draw track
        pygame.draw.rect(screen, UI_BG_COLOR, self.rect)
        pygame.draw.rect(screen, HOT_PINK, self.rect, 2)
        
        # Draw handle
        pygame.draw.rect(screen, NEON_GREEN, self.handle_rect)
        pygame.draw.rect(screen, WHITE, self.handle_rect, 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
            elif self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])

    def update_value(self, mouse_x):
        relative_x = mouse_x - self.rect.left
        ratio = max(0, min(1, relative_x / self.rect.width))
        self.value = self.min_val + (self.max_val - self.min_val) * ratio
        self.update_handle_pos()
