import pygame
from pytmx.util_pygame import load_pygame
from settings import *
from ClassHero import Hero
from ClassBee import Bee
from ClassTile import Tile
from ClassBackground import Background
from SPRITES import Generic

class level():
    def __init__(self, displaySurface, switch_back):  # Fixed parameter name
        self.displaySurface = displaySurface
        self.switch_back = switch_back
        
        
        self.levelData = load_pygame(LEVELS_PATH + "/level-1.tmx")
        self.background = Background()
        
        # Create spriteGroups
        self.hero = pygame.sprite.GroupSingle()
        self.bees = pygame.sprite.Group()
        
        
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.platformTiles = pygame.sprite.Group()
        
        
        
        for layer_name, z_index in LAYERS2.items():
            try:
                layer = self.levelData.get_layer_by_name(layer_name)
                
                # Check if it's a Tile Layer
                if hasattr(layer, 'tiles'):
                    for x, y, tileSurface in layer.tiles():
                        pos = (x * TILESIZE2, y * TILESIZE2)
                        
                        # Create the tile with its Z-layer
                        tile = Tile(pos, tileSurface, z_index) 
                        
                        self.all_sprites.add(tile)
                        
                        # If it's a solid layer, add to collision group
                        # if layer_name in ['Platforms', 'Objects']:
                        #     self.platformTiles.add(tile)
                            
            except ValueError:
                print(f"Warning: Layer '{layer_name}' not found in Tiled.")
        
        # 1. Get the object layer by name
        # try:
        #     object_layer = self.levelData.get_layer_by_name('Objects')
            
        #     for obj in object_layer:
        #         # 2. Convert Tiled coordinates (bottom-left) to Pygame (top-left)
        #         # Objects in Tiled usually have their Y coordinate at the bottom
        #         if obj.image:
        #             y_pos = obj.y - obj.image.get_height()
        #             pos = (obj.x, y_pos)
                    
        #             # 3. Create the sprite based on the object's NAME or TYPE
        #             if obj.name == 'bee':
        #                 new_bee = Bee(pos, moveRight=True)
        #                 self.bees.add(new_bee)
        #                 self.all_sprites.add(new_bee, layer=LAYERS2['player'])
                        
        #             elif obj.name == 'chest':
        #                 # Assuming you have a Chest class in SPRITES
        #                 Generic(pos, obj.image, [self.all_sprites], LAYERS2['Objects'])
                        
        #             else:
        #                 # If it's just a generic decorative object
        #                 Generic(pos, obj.image, [self.all_sprites], LAYERS2['Objects'])

        # except ValueError:
        #     print("No Object layer found")
        
        
       # Hero and Enemies
        self.hero_sprite = Hero((32, 304), faceRight=True)
        self.hero.add(self.hero_sprite)
        self.all_sprites.add(self.hero_sprite, layer=LAYERS2['player'])
        
        # Add bees to all_sprites so they draw in the correct order too
       # In ClassLevel.py __init__
        bee_data = [((200, 200), True), ((300, 380), False),((400, 400), True),((500, 450), False),((600, 480), True)]
        for pos, move_right in bee_data:
            new_bee = Bee(pos, move_right)
            self.bees.add(new_bee)
            self.all_sprites.add(new_bee, layer=LAYERS2['player'])
    def update(self, dt):
        self.hero.update(self, dt)
        self.bees.update(self, dt)
    
    def draw(self):
        """Draw all game elements"""
        self.background.draw(self.displaySurface)
        
        # 2. Everything else (Tiles, Hero, Bees) in Z-order
        self.all_sprites.draw(self.displaySurface)
    
    def run(self, dt):  # Added dt parameter
        self.update(dt)  # Pass dt to update
        self.draw()
        
        # Check for ESC key to return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.switch_back()