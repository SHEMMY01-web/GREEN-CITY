import pygame


class Tile(pygame.sprite.Sprite):

    def __init__(self, position, surface,z_index):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft = position)
        self.mask = pygame.mask.from_surface(self.image)
        self._layer = z_index
