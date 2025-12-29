import pygame
from settings import *
from support import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group,collision_sprites,map_size):
        super().__init__(group)
        self.import_assets()
        self.status = "idle_walkdown"
        self.frame_index = 0

        # general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS["Building"]

        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200
        # collision
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.4, -self.rect.height * 0.7)
        self.collision_sprites = collision_sprites
        self.map_width = map_size[0]
        self.map_height = map_size[1]
        

    def import_assets(self):
        self.scale = 2
        self.animations = {
            "attack": [],
            "dead": [],
            "idle_walkdown": [],  # Start with a default direction
            "idle_walkup": [],
            "idle_walkleft": [],
            "idle_walkright": [],
            "walkdown": [],  # New keys for movement directions
            "walkup": [],
            "walkleft": [],
            "walkright": [],
            "item": [],
            "jump": [],
            "special": [],
        }
        # work on the walk animation
        frame_width = 16
        frame_height = 16

        # Handle the walk sheet separately due to its grid structure

        # Load and split the 4x4 Walk sheet
        walk_sheet_path = "Inspector/SeparateAnim/walk.png"

        # The new function loads and returns one list of all 16 frames
        all_walk_frames = import_and_split_spritesheet(
            walk_sheet_path, frame_width, frame_height, self.scale
        )

        # Map the frames to the animation lists (assuming standard RPG Maker order)
        # Order: Down (Row 1), up (Row 2), left (Row 3), right (Row 4)
        walk_directions = ["down", "up", "left", "right"]  # Standard order for 4x4
        frames_per_direction = 4

        for i, direction in enumerate(walk_directions):
            start_index = i * frames_per_direction
            end_index = start_index + frames_per_direction

            # Slice the list to get only the 4 frames for the current direction
            walk_frames = all_walk_frames[start_index:end_index]

            # Assign the 4 frames to the correct keys
            self.animations[f"walk{direction}"] = walk_frames

            # Use the first frame of the walk cycle as the idle frame
            self.animations[f"idle_walk{direction}"].append(walk_frames[0])

        # 2. Load the remaining single-row/column sheets (Attack, Dead, etc.)
        for anim_name in ["attack", "dead", "item", "jump", "special"]:
            file_path = f"Inspector/SeparateAnim/{anim_name}.png"
            self.animations[anim_name] = import_and_split_spritesheet(
                file_path, frame_width, frame_height, self.scale
            )
        # print(self.animations)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = "walkup"

        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = "walkdown"

        if keys[pygame.K_LSHIFT]:
            self.speed = 400 # Faster
        else:
            self.speed = 200 # Normal
        
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = "walkleft"
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = "walkright"

    def get_status(self):
        # IDLE
        # check if player is not moving
        if self.direction.magnitude() == 0:
            # add idle to the status
            idle_state = "idle_"
            if len(self.status.split("_")) >= 2:
                split = self.status.split("_")[1]
            else:
                split = self.status.split("_")[0]

            self.status = idle_state + split
    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite,"hitbox"):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == "horizontal":
                        if self.direction.x > 0:  # moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:  # moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.pos.x = self.hitbox.centerx
                        self.rect.centerx = self.hitbox.centerx
                    if direction == "vertical":
                        if self.direction.y > 0:  # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:  # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.pos.y = self.hitbox.centery
                        self.rect.centery = self.hitbox.centery
        
        
    def move(self, dt):
    # 1. Normalize direction
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # 2. Horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        
        # --- Horizontal Boundaries ---
        if self.hitbox.left < 0:
            self.hitbox.left = 0
            self.pos.x = self.hitbox.centerx
        elif self.hitbox.right > self.map_width:
            self.hitbox.right = self.map_width
            self.pos.x = self.hitbox.centerx
            
        self.collision("horizontal")
        self.rect.centerx = self.hitbox.centerx

        # 3. Vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        
        # --- Vertical Boundaries ---
        if self.hitbox.top < 0:
            self.hitbox.top = 0
            self.pos.y = self.hitbox.centery
        elif self.hitbox.bottom > self.map_height:
            self.hitbox.bottom = self.map_height
            self.pos.y = self.hitbox.centery
            
        self.collision("vertical")
        self.rect.centery = self.hitbox.centery        

    def update(self, dt):
        self.input()
        self.get_status()

        self.move(dt)
        self.animate(dt)
