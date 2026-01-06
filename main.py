import pygame, sys
from settings import *
from level import Level
from ClassLevel import level


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GREEN CITY")
        self.clock = pygame.time.Clock()

        # state management
        self.state = VILLAGE
        self.village_level = Level()
        self.running = True
        self.platformer_level = None
        self.game_over_start_time = 0


    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            if dt > 0.05: dt = 0.05 # Cap dt to prevent tunneling on lag spikes
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if self.state == VILLAGE:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        # Check if player is near the 'portal' or specific location
                        if self.village_level.check_platformer_trigger():
                            self.state = PLATFORMER
                            # Initialize the platformer level
                            self.platformer_level = level(
                                self.screen, self.switch_to_village, self.switch_to_game_over
                            )

            if self.state == VILLAGE:
                self.village_level.run(dt)
            elif self.state == PLATFORMER and self.platformer_level:
                self.platformer_level.run(dt)

            elif self.state == GAME_OVER:
                self.screen.fill((0, 0, 0))  # Black screen
                font = pygame.font.Font(None, 74)
                text = font.render("GAME OVER", True, (255, 0, 0))
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(text, text_rect)
                
                # Check timer
                if pygame.time.get_ticks() - self.game_over_start_time > 3000:  # 3 seconds
                    self.switch_to_village()

            pygame.display.flip()

    def switch_to_village(self):
        """Callback function to return from platformer"""
        self.state = VILLAGE
        self.platformer_level = None  # Free up memory

    def switch_to_game_over(self):
        """Callback to switch to game over screen"""
        self.state = GAME_OVER
        self.game_over_start_time = pygame.time.get_ticks()
        self.platformer_level = None


if __name__ == "__main__":
    game = Game() 
    game.run()
