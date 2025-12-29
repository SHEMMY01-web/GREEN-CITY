# import pygame
# from settings import *
# from player_platformer import PlayerPlatformer 
# from SPRITES import Generic
# from pytmx.util_pygame import load_pygame
# from pathlib import Path

# class PlatformerLevel:
#     def __init__(self, switch_back):
#         self.display_surface = pygame.display.get_surface()
#         self.switch_back = switch_back 
        
#         # Groups
#         self.all_sprites = pygame.sprite.Group()
#         self.collision_sprites = pygame.sprite.Group()
        
#         self.setup()

#     def setup(self):
#        # Load the level.tmx 
#         tmx_path = Path(__file__).resolve().parent / "data" / "tmx" / "level.tmx"
#         tmx_data = load_pygame(str(tmx_path))
#         # Load Tiles/Platforms
#         for layer in ["Background4","Background3","Background2","Background1","Platforms","Foreground"]:
#             for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
#                 Generic((x*16, y*16), surf, [self.all_sprites, self.collision_sprites])

        
#         for layer_name in ["Objects"]:
#             layer = tmx_data.get_layer_by_name(layer_name)
#             z_layer = LAYERS.get(layer_name, LAYERS["building-layer upper"])

#             for obj in layer:
#                 if obj.image:
#                     top_left_y = obj.y - obj.image.get_height()
#                     Generic(
#                         (obj.x, top_left_y),
#                         obj.image,
#                         [self.all_sprite, self.collision_sprite],
#                         z_layer,
#                     )
        
#         # Setup Player
#         self.player = PlayerPlatformer((100, 100), self.all_sprites, self.collision_sprites)

#     def run(self, dt):
#         # Update
#         self.all_sprites.update(dt)
        
#         # Draw
#         self.display_surface.fill('lightblue') # Sky color
#         self.all_sprites.draw(self.display_surface)

#         # Win/Loss Logic
#         if self.player.pos.y > 1000: # Fell off map
#             self.switch_back()
        
#         # Press 'Esc' to exit manually
#         keys = pygame.key.get_pressed()
#         if keys[pygame.K_ESCAPE]:
#             self.switch_back()