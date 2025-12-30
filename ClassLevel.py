import pygame
from pytmx.util_pygame import load_pygame
from settings import *
from ClassHero import Hero
from ClassBee import Bee
from ClassTile import Tile
from ClassBackground import Background
from SPRITES import Generic

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
        self.all_sprites = pygame.sprite.LayeredUpdates()
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
                        if layer_name == 'Platforms': # Adjust based on your Tiled layer name
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
        self.all_sprites.draw(self.displaySurface) 
    def run(self, dt):
        self.update(dt)
        self.draw()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.switch_back()