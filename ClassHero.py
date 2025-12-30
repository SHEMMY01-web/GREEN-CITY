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
            print("Jump!")
        
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
        self.rect.centerx = int(new_x)
        collisions = pygame.sprite.spritecollide(self, level.platformTiles, False)
        for tile in collisions:
            if self.xDir > 0:  # Moving right
                self.rect.right = tile.rect.left
            elif self.xDir < 0:  # Moving left
                self.rect.left = tile.rect.right
            new_x = float(self.rect.centerx) # Keep center as anchor

        # 4. Platform collision (vertical)
        self.rect.bottom = int(new_y)
        collisions = pygame.sprite.spritecollide(self, level.platformTiles, False)
        self.on_ground = False
        
        for tile in collisions:
            if self.y_vel > 0:  # Falling down
                self.rect.bottom = tile.rect.top
                self.y_vel = 0
                self.on_ground = True
            elif self.y_vel < 0:  # Jumping up
                self.rect.top = tile.rect.bottom
                self.y_vel = 0
            # Reset float position to the bottom of the resolved rect
            new_y = float(self.rect.bottom)
        
        # Update positions
        self.xPos = new_x
        self.yPos = new_y
        
        # 5. Update rect based on state (for proper hitboxes)
        if self.currentState == 'IDLE':
            self.rect = pygame.Rect(self.xPos - 22, self.yPos - 52, 44, 52)
        elif self.currentState == 'RUN':
            self.rect = pygame.Rect(self.xPos - 20, self.yPos - 48, 40, 48)
        elif self.currentState == 'ATTACK':
            self.rect = pygame.Rect(self.xPos - 44, self.yPos - 64, 88, 64)
        elif self.currentState == 'DIE':
            self.rect = pygame.Rect(self.xPos - 32, self.yPos - 48, 64, 48)
        self.hitbox.midbottom = (int(self.xPos), int(self.yPos))
        self.rect.center = self.hitbox.center # Only for drawing
        # 6. Screen Boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.xPos = float(self.rect.centerx)
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.xPos = float(self.rect.centerx)
        
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
            
        collidedSprites = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in collidedSprites:
            if self.currentState == 'ATTACK':
                if self.facingRight:
                    if enemy.rect.left < self.rect.right - 30:
                        enemy.die()
                else:
                    if enemy.rect.right > self.rect.left + 30:
                        enemy.die()
            else:
                if enemy.currentState != 'DYING':
                    self.die()