import pygame
from pytmx.util_pygame import load_pygame
from settings import *
from ClassHero import Hero
from ClassBee import Bee
from ClassTile import Tile
from ClassBackground import Background
from SPRITES import Generic
from ClassMovingTile import MovingTile


class CameraGroup(pygame.sprite.LayeredUpdates):
    def __init__(self, map_width, map_height):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.map_width = map_width
        self.map_width = map_width
        self.map_height = map_height
        self.fixed_y = None # New attribute for locking camera Y
        
    def custom_draw(self, player):
        # Center camera on player
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        
        # Vertical Camera Logic
        if self.fixed_y is not None:
            self.offset.y = self.fixed_y
        else:
            self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
            # Clamp camera to map boundaries (only when following)
            self.offset.y = max(0, min(self.offset.y, self.map_height - SCREEN_HEIGHT))
        
        # Clamp camera X (always active)
        self.offset.x = max(0, min(self.offset.x, self.map_width - SCREEN_WIDTH))
        
        # Draw all sprites with offset
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

class level():
    def __init__(self, displaySurface, switch_back, switch_to_game_over):
        self.displaySurface = displaySurface
        self.switch_back = switch_back
        self.switch_to_game_over = switch_to_game_over
        self.safe_zone_unlocked = False
        
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
        self.sliders = pygame.sprite.Group()
        
        # --- TILE LOADING (One loop only) ---
        for layer_name, z_index in LAYERS2.items():
            try:
                layer = self.levelData.get_layer_by_name(layer_name)
                if hasattr(layer, 'tiles'):
                    for x, y, tileSurface in layer.tiles():
                        # APPLY OFFSET HERE
                        pos = (x * TILESIZE2, (y * TILESIZE2) + self.vertical_offset)
                        
                        # Add to collision group if the layer is a platform
                        if layer_name == 'slider':
                            tile = MovingTile(pos, tileSurface, z_index, self.map_height)
                            self.all_sprites.add(tile)
                            self.platformTiles.add(tile)
                            self.sliders.add(tile)
                        elif layer_name == 'Platforms': # Adjust based on your Tiled layer name
                            tile = Tile(pos, tileSurface, z_index) 
                            self.all_sprites.add(tile)
                            self.platformTiles.add(tile)
                        else:
                            tile = Tile(pos, tileSurface, z_index)
                            self.all_sprites.add(tile)
                            
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
        self.sliders.update(dt) # Update sliders before hero
        self.hero.update(self, dt)
        self.bees.update(self, dt)
        
        # Check for fall death (Conditional)
        # Danger zone is falling below the initial screen height
        DANGER_LINE = SCREEN_HEIGHT 
        
        # Safe Zone Logic:
        # If player is below line AND (on slider OR on ground), they have safely arrived.
        if self.hero_sprite.rect.top > DANGER_LINE:
            if self.hero_sprite.on_slider or self.hero_sprite.on_ground:
                self.safe_zone_unlocked = True
        else:
            # If they go back up, reset the safety (optional, keeps strictness)
            self.safe_zone_unlocked = False

        # If player is below danger line
        if self.hero_sprite.rect.top > DANGER_LINE:
            # If safety is NOT unlocked, check for death condition
            if not self.safe_zone_unlocked:
                # Use Coyote Timer for safety buffer against bouncing/jitter
                # If coyote_timer > 0, we were recently on ground/slider, so we are safe.
                if self.hero_sprite.coyote_timer <= 0:
                     self.switch_to_game_over()
        
        # Check for absolute map bottom death (just in case they clip through bottom)
        if self.hero_sprite.rect.top > self.map_height:
             self.switch_to_game_over()
             
        # Check for animation death (wait for animation to finish)
        if self.hero_sprite.currentState == 'DIE' and int(self.hero_sprite.animationIndex) >= len(self.hero_sprite.currentAnimation) - 1:
            self.switch_to_game_over()

        # --- Dynamic Camera Logic ---
        # 1. Deep Zone (Safe Zone Unlocked): Lock to Bottom
        if self.safe_zone_unlocked:
            self.all_sprites.fixed_y = self.map_height - SCREEN_HEIGHT
        
        # 2. Elevator Ride (On Slider): Follow Player (Concealment lifting)
        elif self.hero_sprite.on_slider:
            self.all_sprites.fixed_y = None 
            
        # 3. Top Zone (Village, default): Lock to Top
        else:
            self.all_sprites.fixed_y = 0
    
    def draw(self):
        self.background.draw(self.displaySurface)
        self.all_sprites.custom_draw(self.hero_sprite)
    def run(self, dt):
        self.update(dt)
        self.draw()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.switch_back()