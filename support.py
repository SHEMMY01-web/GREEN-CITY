import pygame
import os

def import_and_split_spritesheet(sheet_path, frame_width, frame_height,scale):
    """Loads a single spritesheet file and splits it into a list of frames."""
    
    frame_list = []
    
    # 1. Check if the file exists (Important debugging step)
    if not os.path.exists(sheet_path):
        print(f"ERROR: Sprite sheet file not found at path: {sheet_path}")
        return frame_list

    try:
        # 2. Load the entire sprite sheet image
        sheet = pygame.image.load(sheet_path).convert_alpha()
    except pygame.error as e:
        print(f"ERROR: Could not load image file {sheet_path}: {e}")
        return frame_list
    
    # Calculate grid size
    sheet_width = sheet.get_width()
    sheet_height = sheet.get_height()
    cols = sheet_width // frame_width
    rows = sheet_height // frame_height
    
    # 3. Loop through the grid and extract each frame
    for row in range(rows):
        for col in range(cols):
            # Create a blank Surface for the frame with transparency
            frame_surface = pygame.Surface(
                (frame_width, frame_height), 
                flags=pygame.SRCALPHA
            )
            
            # Define the area to be copied from the sheet
            rect = pygame.Rect(
                col * frame_width, 
                row * frame_height, 
                frame_width, 
                frame_height
            )
            
            # Copy the frame from the sheet onto the new surface
            frame_surface.blit(sheet, (0, 0), rect)
            scaled_width=int(frame_width*scale)
            scaled_height=int(frame_height*scale)
            
            scaled_frame=pygame.transform.scale(frame_surface,(scaled_width,scaled_height))
            frame_list.append(scaled_frame)
    print(f"Loaded {len(frame_list)} frames from {sheet_path}")
    return frame_list


class SpriteSheet:
    def __init__(self, path, positions, scale=2):
        # Load the sheet once
        try:
            full_image = pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load spritesheet at {path}: {e}")
            return

        self.frames = []
        self.frames_flipped = []
        
        for pos in positions:
            # pos is a tuple: (x, y, width, height)
            cut_surface = full_image.subsurface(pygame.Rect(pos))
            # Scale the sprite (Tiled is 16px, your game is 64px, so we usually scale x2 or x4)
            scaled = pygame.transform.scale(cut_surface, (pos[2] * scale, pos[3] * scale))
            
            self.frames.append(scaled)
            self.frames_flipped.append(pygame.transform.flip(scaled, True, False))

    def get_frames(self, flipped):
        return self.frames_flipped if flipped else self.frames