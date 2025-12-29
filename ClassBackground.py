import pygame
from settings import *


class Background():

    def __init__(self):
        # Create the sky image
        self.skyImage = pygame.image.load(SPRITESHEET_PATH + "/Background/1.png").convert()
        self.skyImage = pygame.transform.scale(self.skyImage, (SCREEN_WIDTH, SCREEN_HEIGHT))


    def draw(self, displaySurface):
        # Draw sky image
        displaySurface.blit(self.skyImage, (0, 0))
