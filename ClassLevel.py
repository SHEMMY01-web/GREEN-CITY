import pygame
from pytmx.util_pygame import load_pygame
from settings import *
from ClassHero import Hero
from ClassBee import Bee
from ClassTile import Tile
from ClassBackground import Background
from SPRITES import Generic


class CameraGroup(pygame.sprite.LayeredUpdates):
    def __init__(self, map_width, map_height):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.map_width = map_width
        self.map_height = map_height
        
    def custom_draw(self, player):
        # Center camera on player
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        
        # Clamp camera to map boundaries
        self.offset.x = max(0, min(self.offset.x, self.map_width - SCREEN_WIDTH))
        self.offset.y = max(0, min(self.offset.y, self.map_height - SCREEN_HEIGHT))
        
        # Draw all sprites with offset
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

class level():
    def __init__(self, displaySurface, switch_back):
        self.displaySurface = displaySurface
        self.switch_back = switch_back
        
        # Load Tiled Data
        self.levelData = load_pygame(LEVELS_PATH + "/level-1.tmx")
        self.map_width = self.levelData.width * self.levelData.tilewidth
        self.map_height = self.levelData.height * self.levelData.tileheight
        
        # Calculate vertical offset to pin map to bottom of screen
        self.vertical_offset = max(0, SCREEN_HEIGHT - self.map_height)
        self.background = Background()
        
        
        # Sprite Groups
        self.hero = pygame.sprite.GroupSingle()
        self.bees = pygame.sprite.Group()
        self.all_sprites = CameraGroup(self.map_width, self.map_height)
        self.platformTiles = pygame.sprite.Group()
        
        # --- TILE LOADING (One loop only) ---
        for layer_name, z_index in LAYERS2.items():
            try:
                layer = self.levelData.get_layer_by_name(layer_name)
                if hasattr(layer, 'tiles'):
                    for x, y, tileSurface in layer.tiles():
                        # APPLY OFFSET HERE
                        pos = (x * TILESIZE2, (y * TILESIZE2) + self.vertical_offset)
                        
                        tile = Tile(pos, tileSurface, z_index) 
                        self.all_sprites.add(tile)
                        
                        # Add to collision group if the layer is a platform
                        if layer_name == 'Platforms' or layer_name == 'slider': # Adjust based on your Tiled layer name
                            self.platformTiles.add(tile)
                            
            except ValueError:
                print(f"Warning: Layer '{layer_name}' not found.")
                
        # --- HERO ---

        # --- HERO ---
        # Apply vertical_offset so the hero starts on the ground of the shifted map
        hero_start_pos = (32, 304 + self.vertical_offset)
        self.hero_sprite = Hero(hero_start_pos, faceRight=True)
        self.hero.add(self.hero_sprite)
        self.all_sprites.add(self.hero_sprite, layer=LAYERS2['player'])
        
        # --- ENEMIES (Bees) ---
        bee_data = [((200, 200), True), ((300, 380), False), 
                    ((400, 400), True), ((500, 450), False), ((600, 480), True)]
        
        for pos, move_right in bee_data:
            # Apply offset to each bee position
            offset_pos = (pos[0], pos[1] + self.vertical_offset)
            new_bee = Bee(offset_pos, move_right)
            self.bees.add(new_bee)
            self.all_sprites.add(new_bee, layer=LAYERS2['player'])
    def update(self, dt):
        self.hero.update(self, dt)
        self.bees.update(self, dt)
    
    def draw(self):
        self.background.draw(self.displaySurface)
        self.all_sprites.custom_draw(self.hero_sprite)
    def run(self, dt):
        self.update(dt)
        self.draw()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.switch_back()