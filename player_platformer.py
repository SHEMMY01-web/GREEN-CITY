# import pygame
# from settings import *
# from support import SpriteSheet # Uses the SpriteSheet helper from previous turn

# class PlayerPlatformer(pygame.sprite.Sprite):
#     def __init__(self, pos, group, collision_sprites):
#         super().__init__(group)
#         self.import_assets()
#         self.state = 'IDLE'
#         self.frame_index = 0
#         self.facing_right = True

#         self.image = self.animations['IDLE'].get_frames(False)[0]
#         self.rect = self.image.get_rect(center=pos)
        
#         # Physics
#         self.direction = pygame.math.Vector2()
#         self.pos = pygame.math.Vector2(self.rect.center)
#         self.on_ground = False
        
#         # Collision
#         self.hitbox = self.rect.copy().inflate(-30, -10)
#         self.collision_sprites = collision_sprites

#     def import_assets(self):
#         path = "../data/graphics/Character/"
#         self.animations = {
#             'IDLE': SpriteSheet(f'{path}Idle/Idle-Sheet.png', [(12,12,44,52), (76,12,44,52), (140,12,44,52), (204,12,44,52)]),
#             'RUN': SpriteSheet(f'{path}Run/Run-Sheet.png', [(24,16,40,52), (104,16,40,52), (184,16,40,52), (264,16,40,52)]),
#             'ATTACK': SpriteSheet(f'{path}Attack-01/Attack-01-Sheet.png', [(4,0,92,80), (100,0,92,80)])
#         }

#     def input(self):
#         keys = pygame.key.get_pressed()
#         if keys[pygame.K_RIGHT]:
#             self.direction.x = 1
#             self.facing_right = True
#             self.state = 'RUN'
#         elif keys[pygame.K_LEFT]:
#             self.direction.x = -1
#             self.facing_right = False
#             self.state = 'RUN'
#         else:
#             self.direction.x = 0
#             self.state = 'IDLE'

#         if keys[pygame.K_SPACE] and self.on_ground:
#             self.direction.y = JUMP_SPEED
#             self.on_ground = False

#     def collision(self, direction):
#         for sprite in self.collision_sprites.sprites():
#             if sprite.hitbox.colliderect(self.hitbox):
#                 if direction == 'horizontal':
#                     if self.direction.x > 0: self.hitbox.right = sprite.hitbox.left
#                     if self.direction.x < 0: self.hitbox.left = sprite.hitbox.right
#                     self.pos.x = self.hitbox.centerx
#                 if direction == 'vertical':
#                     if self.direction.y > 0: # Landing
#                         self.hitbox.bottom = sprite.hitbox.top
#                         self.direction.y = 0
#                         self.on_ground = True
#                     if self.direction.y < 0: # Head bonk
#                         self.hitbox.top = sprite.hitbox.bottom
#                         self.direction.y = 0
#                     self.pos.y = self.hitbox.centery

#     def update(self, dt):
#         self.input()
#         # Horizontal
#         self.pos.x += self.direction.x * PLATFORMER_SPEED * dt
#         self.hitbox.centerx = round(self.pos.x)
#         self.collision('horizontal')
#         # Vertical (Gravity)
#         self.direction.y += GRAVITY * dt
#         self.pos.y += self.direction.y * dt
#         self.hitbox.centery = round(self.pos.y)
#         self.on_ground = False
#         self.collision('vertical')
        
#         self.rect.center = self.hitbox.center