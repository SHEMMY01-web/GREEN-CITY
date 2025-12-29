import pygame
from settings import *


class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups, z=LAYERS["Building"]):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(
            -self.rect.width * 0.2, -self.rect.height * 0.75
        )
    # def __init__(self, pos, surface, groups, z=LAYERS["building-layer"]):
    #     super().__init__(groups)
    #     self.image = surface
        
    #     # 1. FORCE INTEGER COORDINATES
    #     # This prevents the 'broken' look by ensuring everything is on the same pixel grid
    #     self.rect = self.image.get_rect(topleft = (round(pos[0]), round(pos[1])))
        
    #     self.z = z
        
    #     # 2. IMPROVE HITBOX PLACEMENT
    #     # For top-down games, the hitbox should be at the feet/bottom of the object
    #     self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)
    #     self.hitbox.bottom = self.rect.bottom