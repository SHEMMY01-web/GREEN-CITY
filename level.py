import pygame
from pathlib import Path
from settings import *
from player import Player
from SPRITES import Generic
from pytmx.util_pygame import load_pygame


class Level:
    def __init__(self):
        # get display surface
        self.display_surface = pygame.display.get_surface()
        self.setup()

    def check_platformer_trigger(self):
        if self.portal_trigger and hasattr(self, "player"):
            if self.player.hitbox.colliderect(self.portal_trigger):
                return True
        return False

    def setup(self):
        tmx_path = Path(__file__).resolve().parent / "data" / "tmx" / "latest-map.tmx"
        tmx_data = load_pygame(str(tmx_path))
        TILE_SIZE = tmx_data.tilewidth
        map_width = tmx_data.width * TILE_SIZE  # 2048
        map_height = tmx_data.height * TILE_SIZE  # 1152
        self.map_limits = pygame.Rect(0, 0, map_width, map_height)
        self.all_sprite = CameraGroup(self.map_limits)
        self.collision_sprite = pygame.sprite.Group()

        # LOAD PORTAL TRIGGER FROM TMX
        # Inside Level.setup()
        self.portal_trigger = None
        portal_layer = tmx_data.get_layer_by_name("portal")
        for obj in portal_layer:
            if obj.name == "portal":
                w = obj.width if obj.width > 0 else 64
                h = obj.height if obj.height > 0 else 64
                y_pos = obj.y - h
                self.portal_trigger = pygame.Rect(obj.x, y_pos, w, h)
                # print("Layers in latest-map.tmx:")
                for layer in tmx_data.layers:
                    if hasattr(layer, "name"):
                        # print(f"  - {layer.name}")
                        pass

        for layer_name in ["Ground", "Roads", "Stones", "Trees", "Building"]:
            layer = tmx_data.get_layer_by_name(layer_name)
            for x, y, surf in layer.tiles():
                # 1. FIX POSITION: Shift tall tiles up so they sit on the 64px grid
                y_offset = surf.get_height() - 64
                pos = (x * 64, (y * 64) - y_offset)

                # 2. ADD COLLISION: Add trees and buildings to the collision group
                groups = [self.all_sprite]
                if layer_name in ["Trees", "Building", "Stones"]:
                    groups.append(self.collision_sprite)

                Generic(pos=pos, surface=surf, groups=groups, z=LAYERS[layer_name])

        for obj in tmx_data.get_layer_by_name("player"):
            if obj.name == "start":
                spawn_x = obj.x + (64 - PLAYER_WIDTH) // 2
                spawn_y = obj.y - 64
                self.player = Player(
                    (spawn_x, spawn_y),
                    self.all_sprite,
                    self.collision_sprite,
                    (map_width, map_height),
                )

        # floor
        # img = pygame.image.load("Sample.png").convert_alpha()
        # Generic(pos=(0, 0), surface=img, groups=[self.all_sprite], z=LAYERS["ground"])

    def run(self, dt):
        self.display_surface.fill("black")
        # self.display_surface.fill("#55ad5d")
        self.all_sprite.custom_draw(self.player)
        self.all_sprite.update(dt)

        if self.portal_trigger:
            # We must subtract the camera offset so the box moves with the world
            debug_rect = self.portal_trigger.copy()
            debug_rect.topleft -= self.all_sprite.offset
            pygame.draw.rect(self.display_surface, (255, 0, 0), debug_rect, 2)

        if hasattr(self, "portal_trigger"):
            font = pygame.font.Font(None, 24)
            portal_text = f"Portal: ({self.portal_trigger.x}, {self.portal_trigger.y})"
            text_surface = font.render(portal_text, True, (255, 255, 255))
            self.display_surface.blit(text_surface, (10, 10))

            player_text = f"Player: ({self.player.hitbox.x}, {self.player.hitbox.y})"
            text_surface2 = font.render(player_text, True, (255, 255, 255))
            self.display_surface.blit(text_surface2, (10, 40))


class CameraGroup(pygame.sprite.Group):
    def __init__(self, map_limits):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.map_limits = map_limits

    def custom_draw(self, player):

        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        # 2. CLAMP the offset so it doesn't show the black bars
        # Left/Right limits
        if self.offset.x < 0:
            self.offset.x = 0
        if self.offset.x > self.map_limits.width - SCREEN_WIDTH:
            self.offset.x = self.map_limits.width - SCREEN_WIDTH

        # Top/Bottom limits
        if self.offset.y < 0:
            self.offset.y = 0
        if self.offset.y > self.map_limits.height - SCREEN_HEIGHT:
            self.offset.y = self.map_limits.height - SCREEN_HEIGHT

        self.offset.x = round(self.offset.x)
        self.offset.y = round(self.offset.y)
        final_offset_x = int(self.offset.x)
        final_offset_y = int(self.offset.y)

        for layer in LAYERS.values():
            for sprite in sorted(
                self.sprites(), key=lambda sprite: sprite.rect.centery
            ):
                if sprite.z == layer:
                    # Use the pre-calculated integer offsets
                    dest_pos = (
                        sprite.rect.x - final_offset_x,
                        sprite.rect.y - final_offset_y,
                    )
                    self.display_surface.blit(sprite.image, dest_pos)
