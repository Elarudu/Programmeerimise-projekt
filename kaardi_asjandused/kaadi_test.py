import pygame
import pytmx
import os

# --- Constants ---
VISUAL_SIZE = 42       # Size to draw the player
HITBOX_WIDTH = 32      # Width of collision (Slightly smaller than tile to fit in doors)
HITBOX_HEIGHT = 42     # Full height (Head will now hit walls)
PLAYER_SPEED = 4

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Full Body Collision")
clock = pygame.time.Clock()

# --- Path Setup ---
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Load TMX Map ---
try:
    map_path = os.path.join(script_dir, "level.tmx")
    tmx_data = pytmx.load_pygame(map_path)
except Exception as e:
    print(f"CRITICAL ERROR: Could not load map at {map_path}")
    print(f"Error details: {e}")
    pygame.quit()
    exit()

tile_width = tmx_data.tilewidth
tile_height = tmx_data.tileheight

# --- Build Wall List ---
walls = []
for layer in tmx_data.visible_layers:
    if isinstance(layer, pytmx.TiledTileLayer):
        for x, y, gid in layer:
            if gid:
                # 1. Check Tiled Property "solid"
                tile_props = tmx_data.get_tile_properties_by_gid(gid)
                is_solid = tile_props and tile_props.get("solid")
                
                # 2. Hardcoded Check for Black Tile (Safety check)
                if gid == 11:
                    is_solid = True
                
                if is_solid:
                    wall_rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                    walls.append(wall_rect)

print(f"DEBUG: Found {len(walls)} solid walls.")

# --- Load & Scale Images ---
def load_image(filename):
    paths_to_check = [
        os.path.join(script_dir, "pildid", filename),
        os.path.join(script_dir, filename)
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (VISUAL_SIZE, VISUAL_SIZE))
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                return None
    return None

player_standing = load_image("tegelane_seisab.png")
player_walk1 = load_image("tegelane_konnib(1).png")
player_walk2 = load_image("tegelane_konnib(2).png")

# Fallback Red Box
if not player_standing:
    player_standing = pygame.Surface((VISUAL_SIZE, VISUAL_SIZE))
    player_standing.fill((255, 0, 0))
    player_walk1 = player_standing
    player_walk2 = player_standing

# --- Player Setup ---
player_x = WIDTH // 2 
player_y = HEIGHT // 2

# HITBOX: Now covers the full height of the character
player_rect = pygame.Rect(player_x, player_y, HITBOX_WIDTH, HITBOX_HEIGHT)

# Animation State
current_sprite = player_standing
animation_frame = 0
animation_speed = 10
animation_counter = 0

def draw_map(camera_x, camera_y):
    """Draw the map tiles"""
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen_x = x * tile_width - camera_x
                    screen_y = y * tile_height - camera_y
                    
                    if -tile_width < screen_x < WIDTH and -tile_height < screen_y < HEIGHT:
                        screen.blit(tile, (screen_x, screen_y))

def draw_player(camera_x, camera_y):
    """Draw the player image aligned with the hitbox"""
    hitbox_screen_x = player_rect.x - camera_x
    hitbox_screen_y = player_rect.y - camera_y
    
    # Calculate offset to center the image horizontally on the hitbox
    image_x = hitbox_screen_x - (VISUAL_SIZE - HITBOX_WIDTH) // 2
    
    # Vertically, they are now the same height (or close to it), so minimal offset
    image_y = hitbox_screen_y - (VISUAL_SIZE - HITBOX_HEIGHT)
    
    screen.blit(current_sprite, (image_x, image_y))

    # DEBUG: Uncomment to see the full-body hitbox
    # pygame.draw.rect(screen, (0, 255, 0), (hitbox_screen_x, hitbox_screen_y, HITBOX_WIDTH, HITBOX_HEIGHT), 1)

# --- Game Loop ---
running = True
print("Controls: WASD to move, F for Fullscreen, ESC to quit")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_f:
                is_fullscreen = screen.get_flags() & pygame.FULLSCREEN
                if is_fullscreen:
                    screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
                else:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                WIDTH, HEIGHT = screen.get_size()

    # --- Movement & Collision ---
    keys = pygame.key.get_pressed()
    is_moving = False
    
    # Move X
    move_x = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        move_x = -PLAYER_SPEED
        is_moving = True
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move_x = PLAYER_SPEED
        is_moving = True
        
    player_rect.x += move_x
    
    for wall in walls:
        if player_rect.colliderect(wall):
            if move_x > 0: 
                player_rect.right = wall.left
            elif move_x < 0: 
                player_rect.left = wall.right

    # Move Y
    move_y = 0
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        move_y = -PLAYER_SPEED
        is_moving = True
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        move_y = PLAYER_SPEED
        is_moving = True
        
    player_rect.y += move_y
    
    for wall in walls:
        if player_rect.colliderect(wall):
            if move_y > 0: 
                player_rect.bottom = wall.top
            elif move_y < 0: 
                player_rect.top = wall.bottom

    # --- Animation ---
    if is_moving:
        animation_counter += 1
        if animation_counter >= animation_speed:
            animation_counter = 0
            animation_frame = (animation_frame + 1) % 2
            current_sprite = player_walk1 if animation_frame == 0 else player_walk2
    else:
        current_sprite = player_standing

    # --- Camera ---
    camera_x = player_rect.centerx - WIDTH // 2
    camera_y = player_rect.centery - HEIGHT // 2
    
    map_pixel_width = tmx_data.width * tile_width
    map_pixel_height = tmx_data.height * tile_height
    
    camera_x = max(0, min(camera_x, map_pixel_width - WIDTH))
    camera_y = max(0, min(camera_y, map_pixel_height - HEIGHT))
    
    # --- Draw ---
    screen.fill((30, 30, 30))
    draw_map(camera_x, camera_y)
    draw_player(camera_x, camera_y)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()