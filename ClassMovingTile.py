import pygame
from settings import *

class MovingTile(pygame.sprite.Sprite):
    def __init__(self, position, surface, z_index, map_height):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.mask = pygame.mask.from_surface(self.image)
        self._layer = z_index
        
        # Movement properties
        self.start_y = position[1]
        self.end_y = map_height - self.rect.height # Stop at bottom of map
        self.speed = 200 # Pixels per second
        self.direction = 1 # 1 for down, -1 for up
        
        # State management
        self.state = 'MOVING' # 'MOVING' or 'WAITING'
        self.wait_timer = 0
        self.wait_duration = 3.0 # Seconds
        
        # Float position for smooth movement
        self.pos_y = float(self.rect.y)

    def update(self, dt):
        if self.state == 'WAITING':
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.state = 'MOVING'
                # Flip direction when done waiting
                self.direction *= -1
        
        elif self.state == 'MOVING':
            self.pos_y += self.speed * self.direction * dt
            self.rect.y = round(self.pos_y)
            
            # Check boundaries
            # Check boundaries
            if self.direction == 1: # Moving Down
                # Check if TOP has reached the target TOP (end_y)
                if self.rect.y >= self.end_y: 
                    self.rect.y = int(self.end_y)
                    self.pos_y = float(self.rect.y)
                    self.state = 'WAITING'
                    self.wait_timer = self.wait_duration
            
            elif self.direction == -1: # Moving Up
                if self.rect.top <= self.start_y:
                    self.rect.top = int(self.start_y)
                    self.pos_y = float(self.rect.y)
                    self.state = 'WAITING'
                    self.wait_timer = self.wait_duration
