import pygame
import sys
from src.utils import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ClawMania")
    clock = pygame.time.Clock()
    
    from src.game_manager import GameManager
    game_manager = GameManager()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_manager.handle_event(event)

        # Update
        game_manager.update()
        
        # Draw
        game_manager.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
