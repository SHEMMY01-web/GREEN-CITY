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

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
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
                                self.screen, self.switch_to_village
                            )

            if self.state == VILLAGE:
                self.village_level.run(dt)
            elif self.state == PLATFORMER and self.platformer_level:
                self.platformer_level.run(dt)

            pygame.display.flip()

    def switch_to_village(self):
        """Callback function to return from platformer"""
        self.state = VILLAGE
        self.platformer_level = None  # Free up memory


if __name__ == "__main__":
    game = Game()
    game.run()
