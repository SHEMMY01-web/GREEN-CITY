import pygame
from settings import *
from ClassSpriteSheet import SpriteSheet

runSprites = [
    (24, 16, 40, 52),
    (104, 16, 40, 52),
    (184, 16, 40, 52),
    (264, 16, 40, 52),
    (344, 16, 40, 52),
    (424, 16, 40, 52),
    (504, 16, 40, 52),
    (584, 16, 40, 52)
]

idleSprites = [
    (12, 12, 44, 52),
    (76, 12, 44, 52),
    (140, 12, 44, 52),
    (204, 12, 44, 52)
]

attackSprites = [
    (4, 0, 92, 80),
    (100, 0, 92, 80),
    (196, 0, 92, 80),
    (294, 0, 92, 80),
    (388, 0, 92, 80),
    (484, 0, 92, 80),
    (580, 0, 92, 80),
    (676, 0, 92, 80)
]

deathSprites = [
    (0, 0, 64, 56),
    (80, 0, 64, 56),
    (160, 0, 64, 56),
    (240, 0, 64, 56),
    (320, 0, 64, 56),
    (400, 0, 64, 56),
    (480, 0, 64, 56),
    (560, 0, 64, 56)
]


jumpSprites = [
    (0,   0, 64, 64),
    (64,  0, 64, 64),
    (128, 0, 64, 64),
    (192, 0, 64, 64),
    (256, 0, 64, 64),
    (320, 0, 64, 64),
    (384, 0, 64, 64),
    (448, 0, 64, 64),
    (512, 0, 64, 64),
    (576, 0, 64, 64),
    (640, 0, 64, 64),
    (704, 0, 64, 64),
    (768, 0, 64, 64),
    (832, 0, 64, 64),
    (896, 0, 64, 64),
]


class Hero(pygame.sprite.Sprite):
    def __init__(self, position, faceRight):
        super().__init__()
        self.hitbox = pygame.Rect(0, 0, 40, 50)

        # Load spritesheets
        idleSpriteSheet = SpriteSheet(SPRITESHEET_PATH + "/Idle/Idle-Sheet.png", idleSprites)
        runSpriteSheet = SpriteSheet(SPRITESHEET_PATH + "/Run/Run-Sheet.png", runSprites)
        attackSpriteSheet = SpriteSheet(SPRITESHEET_PATH + "/Attack-01/Attack-01-Sheet.png", attackSprites)
        deathSpriteSheet = SpriteSheet(SPRITESHEET_PATH + "/Dead/Dead-Sheet.png", deathSprites)
        jumpSpriteSheet = SpriteSheet(SPRITESHEET_PATH + "/jump/Jump-All-Sheet.png", jumpSprites)

        self.spriteSheets = {
            'IDLE': idleSpriteSheet,
            'RUN': runSpriteSheet,
            'ATTACK': attackSpriteSheet,
            'DIE': deathSpriteSheet,
            "JUMP": jumpSpriteSheet
        }

        # Physics properties
        self.x_vel = 0
        self.y_vel = 0
        self.on_ground = False
        self.gravity = GRAVITY  # Should be 1800 from settings
        self.jump_speed = JUMP_SPEED  # Should be -800 from settings
        
        # Jump control
        self.can_jump = True
        self.jump_held = False
        self.jump_buffer_time = 0.1  # Seconds to buffer jump input
        self.jump_buffer_timer = 0
        self.coyote_time = 0.1  # Time after leaving ground you can still jump
        self.coyote_timer = 0
        self.jump_cut_speed = JUMP_SPEED / 2  # Speed to set when jump is released early
        
        
        # Animation properties
        self.animationIndex = 0
        self.facingRight = faceRight
        self.currentState = 'IDLE'
        self.previousState = 'IDLE'
        self.xDir = 0
        self.speed = SPEED_HERO
        self.on_slider = False
        self.current_platform = None
        
        # Position (keep as floats for smooth movement)
        self.xPos = float(position[0])
        self.yPos = float(position[1])
        
        # Initial rect for collision (using idle state dimensions)
        self.rect = pygame.Rect(self.xPos - 22, self.yPos - 52, 44, 52)
        
        # Current animation
        self.currentAnimation = []
        self.animationSpeed = ANIMSPEED_HERO_DEFAULT
        self.selectAnimation()
        
        # Ensure self.image is set immediately
        if self.currentAnimation:
            self.image = self.currentAnimation[0]
        else:
            # Fallback if no animation found
            self.image = pygame.Surface((40, 50))
            self.image.fill((255, 0, 0)) # Red box for visibility

    def update(self, level, dt):
        self.previousState = self.currentState
        
        # Update timers
        if not self.on_ground:
            self.coyote_timer -= dt
        else:
            self.coyote_timer = self.coyote_time
        
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= dt
        
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= dt
        
        # Sticky Platform Logic
        # Move hero with the platform BEFORE input/physics to prevent 1-frame gaps
        if self.on_ground and self.current_platform:
            # Check if platform is a MovingTile (has speed attribute)
            # Apply sticky logic even if WAITING to prevent 'on_ground' flickering
            if hasattr(self.current_platform, 'speed'):
                 # Hard snap to the platform's new position
                 # The platform has already moved in Level.update()
                 # We place the player exactly on top (plus 1 pixel to ensure contact/collision next physics step)
                 self.hitbox.bottom = self.current_platform.rect.top + 1
                 self.yPos = float(self.hitbox.bottom)
                 self.y_vel = 1 # Set small positive velocity to ensure 'falling' logic triggers in collision check
                 
                 # Note: We add 1 pixel of overlap so that the subsequent physics/collision check 
                 # DEFINITELY sees us as "colliding" and keeps "on_ground" True.
                 # The Vertical collision resolution will snap us back to exactly .top anyway.
        
        # 1. Handle Input
        keys = pygame.key.get_pressed()
        
        # Jump input with buffering and coyote time
        jump_pressed = keys[pygame.K_UP]
        
        # Buffer jump input
        if jump_pressed:
            self.jump_buffer_timer = self.jump_buffer_time
        
        # Jump conditions
        can_jump_now = (self.on_ground or self.coyote_timer > 0) and self.can_jump and self.currentState != 'DIE'
        has_buffered_jump = self.jump_buffer_timer > 0
        
        # Perform jump
        if can_jump_now and has_buffered_jump:
            self.y_vel = self.jump_speed
            self.on_ground = False
            self.can_jump = False
            self.jump_buffer_timer = 0
            self.coyote_timer = 0
            # print("Jump!")
        
        # Variable jump height (release jump to fall faster)
        if not jump_pressed and self.y_vel < self.jump_cut_speed:
            self.y_vel = self.jump_cut_speed
        
        # Reset jump ability when back on ground
        if self.on_ground:
            self.can_jump = True
        
        # Movement input (LEFT/RIGHT)
        if self.currentState != 'ATTACK' and self.currentState != 'DIE':
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.xDir = -1
                self.facingRight = False
                self.currentState = 'RUN'
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.xDir = 1
                self.facingRight = True
                self.currentState = 'RUN'
            else:
                self.currentState = 'IDLE'
                self.xDir = 0
        
        # Attack input(left,right)
        if keys[pygame.K_SPACE] and self.currentState != 'DIE':
            self.currentState = 'ATTACK'
        # 2. Apply physics
        # Apply gravity
        if not self.on_ground:
            self.y_vel += self.gravity * dt
        
        # Update position
        new_x = self.xPos + (self.xDir * PLATFORMER_SPEED * dt)
        new_y = self.yPos + (self.y_vel * dt)
        
        # 3. Platform collision (horizontal)
        self.hitbox.centerx = int(new_x)
        # Rect Collision (Standard)
        collisions = []
        for tile in level.platformTiles:
            if self.hitbox.colliderect(tile.rect):
                collisions.append(tile)

        for tile in collisions:
            # Ignore the platform we are standing on to prevent getting stuck/pushed
            if self.current_platform and tile == self.current_platform:
                continue

            # NEW: If on a slider, ignore all other slider tiles (adjacent segments)
            # This prevents treating the next tile of the elevator as a "wall"
            if self.current_platform and hasattr(self.current_platform, 'speed'):
                if hasattr(tile, 'speed'):
                    continue

            if self.xDir > 0:  # Moving right
                self.hitbox.right = tile.rect.left
            elif self.xDir < 0:  # Moving left
                self.hitbox.left = tile.rect.right
            new_x = float(self.hitbox.centerx) # Keep center as anchor

        # 4. Platform collision (vertical)
        self.hitbox.bottom = int(new_y)
        # Rect Collision (Standard)
        collisions = []
        for tile in level.platformTiles:
            if self.hitbox.colliderect(tile.rect):
                collisions.append(tile)
        
        self.on_ground = False
        self.on_slider = False # Default to False
        self.current_platform = None # Default to None
        
        for tile in collisions:
            if self.y_vel > 0:  # Falling down
                self.hitbox.bottom = tile.rect.top
                self.y_vel = 0
                self.on_ground = True
                self.current_platform = tile # Store the platform we landed on
                
                # Check if it's a slider (MovingTile)
                # MovingTile class name check or isinstance if imported, but simple attribute check works
                if hasattr(tile, 'speed') and hasattr(tile, 'direction'): 
                     self.on_slider = True
                     
            elif self.y_vel < 0:  # Jumping up
                self.hitbox.top = tile.rect.bottom
                self.y_vel = 0
            # Reset float position to the bottom of the resolved hitbox
            new_y = float(self.hitbox.bottom)
        
        # Update positions
        self.xPos = new_x
        self.yPos = new_y
        
        # 5. Update rect based on state (for drawing only)
        # We align the bottom center of the drawing rect to the bottom center of the hitbox
        if self.currentState == 'IDLE':
            self.rect = pygame.Rect(0, 0, 44, 52)
        elif self.currentState == 'RUN':
            self.rect = pygame.Rect(0, 0, 40, 48)
        elif self.currentState == 'ATTACK':
            self.rect = pygame.Rect(0, 0, 92, 80) # Use actual sprite size
        elif self.currentState == 'DIE':
            self.rect = pygame.Rect(0, 0, 64, 56)
            
        self.rect.midbottom = self.hitbox.midbottom
        
        # 6. Screen Boundaries
        # Use map boundaries from the level object
        if self.hitbox.left < 0:
            self.hitbox.left = 0
            self.xPos = float(self.hitbox.centerx)
        elif self.hitbox.right > level.map_width:
            self.hitbox.right = level.map_width
            self.xPos = float(self.hitbox.centerx)
        
        # Sync rect again (in case boundary check moved hitbox)
        self.rect.midbottom = self.hitbox.midbottom
        
        # 7. Handle Animations
        self.selectAnimation()
        if self.previousState != self.currentState:
            self.animationIndex = 0
        
        # Progress animation frame
        self.animationIndex += self.animationSpeed
        if self.animationIndex >= len(self.currentAnimation):
            if self.currentState == 'DIE':
                self.animationIndex = len(self.currentAnimation) - 1
            elif self.currentState == 'ATTACK':
                self.animationIndex = 0
                self.currentState = 'IDLE'  # Return to idle after attack
            else:
                self.animationIndex = 0
        
        if len(self.currentAnimation) > 0:
            self.image = self.currentAnimation[int(self.animationIndex)]
            self.mask = pygame.mask.from_surface(self.image)
        
        # 8. Check for enemy collisions
        self.checkEnemyCollisions(level.bees)

    def selectAnimation(self):
        self.animationSpeed = ANIMSPEED_HERO_DEFAULT
        if self.currentState == 'IDLE':
            self.animationSpeed = ANIMSPEED_HERO_IDLE
        elif self.currentState == 'ATTACK':
            self.animationSpeed = ANIMSPEED_HERO_DEFAULT * 2  # Faster attack animation

        spriteSheet = self.spriteSheets.get(self.currentState, self.spriteSheets['IDLE'])
        self.currentAnimation = spriteSheet.getSprites(flipped=not self.facingRight)

    def die(self):
        if self.currentState != 'DIE':
            self.currentState = 'DIE'
            self.animationIndex = 0
            # Stop movement when dying
            self.xDir = 0
            self.y_vel = 0

    def checkEnemyCollisions(self, enemies):
        if self.currentState == 'DIE':
            return
            
        collidedSprites = pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_mask)
        for enemy in collidedSprites:
            if self.currentState == 'ATTACK':
                if self.facingRight:
                    if enemy.rect.left < self.rect.right - 30:
                        # enemy.die()
                        pass
                else:
                    if enemy.rect.right > self.rect.left + 30:
                        # enemy.die()
                        pass
            else:
                if enemy.currentState != 'DYING':
                    # self.die()
                    pass