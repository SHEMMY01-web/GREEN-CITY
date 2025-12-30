from pygame.math import Vector2
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREEN_WIDTH = 1302
SCREEN_HEIGHT = 736
FPS = 40  # Set to 60 for smoother platforming
TILE_SIZE = 64
PLAYER_WIDTH = 16

# Game States
VILLAGE = "village"
PLATFORMER = "platformer"

# Platformer Physics (tuned for dt)
GRAVITY = 1800
JUMP_SPEED = -1100
PLATFORMER_SPEED = 400
ANIMATION_SPEED = 10


# Assets:
# SPRITESHEET_PATH = os.path.join(BASE_DIR, "data", "graphics","Character")
SPRITESHEET_PATH = "data/graphics/Character/"
LEVELS_PATH = os.path.join(BASE_DIR, "data", "tmx")


TILESIZE2 = 32


SPEED_HERO = 4
ANIMSPEED_HERO_DEFAULT = 0.25
ANIMSPEED_HERO_IDLE = 0.1

SPEED_BEE = 2
ANIMSPEED_BEE = 0.2
ANIMSPEED_BEE_ATTACK = 0.5


LAYERS = {
    "Ground": 0,
    "Roads": 1,
    "Stones": 2,
    "Trees": 3,
    "Building": 4,
    "portal": 5,
    "player": 6
}


LAYERS2 = {
    "Ground":0,
    "Platforms":1,
    "Rails":2,
    # 'Background1': 0,
    # 'Background2': 1,
    # 'Background3': 2,
    # 'Background4': 3,
    # 'Platforms':   4,
    # 'Objects':     5,
    'player':      3, # Player is usually near the top
    # 'Foreground':  7  # Always on top of everything
}