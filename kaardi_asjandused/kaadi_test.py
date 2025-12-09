import pygame
import pytmx
import os

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Load TMX Map ---
script_dir = os.path.dirname(__file__)
tmx_data = pytmx.load_pygame(os.path.join(script_dir, "level.tmx"))
tile_width = tmx_data.tilewidth
tile_height = tmx_data.tileheight

# --- Load Player Sprites ---
player_standing = pygame.image.load(os.path.join(script_dir, "tegelane_seisab.png")).convert_alpha()
player_walk1 = pygame.image.load(os.path.join(script_dir, "tegelane_konnib(1).png")).convert_alpha()
player_walk2 = pygame.image.load(os.path.join(script_dir, "tegelane_konnib(2).png")).convert_alpha()

# --- Player Setup (MUST BE BEFORE GAME LOOP) ---
player_size = 32
player_x = WIDTH // 2  # Start in middle of screen
player_y = HEIGHT // 2
player_speed = 4

# Create player rect for position and collision
player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

# Animation variables
current_sprite = player_standing
animation_frame = 0
animation_speed = 10
animation_counter = 0
is_moving = False

def draw_map(camera_x, camera_y):
    """Draw the tilemap with camera offset"""
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen_x = x * tile_width - camera_x
                    screen_y = y * tile_height - camera_y
                    
                    # Only draw tiles visible on screen
                    if (-tile_width < screen_x < WIDTH and 
                        -tile_height < screen_y < HEIGHT):
                        screen.blit(tile, (screen_x, screen_y))

def draw_player(camera_x, camera_y):
    """Draw the player"""
    screen_x = player_rect.x - camera_x
    screen_y = player_rect.y - camera_y
    screen.blit(current_sprite, (screen_x, screen_y))

# --- Game Loop ---
running = True
print("Controls: WASD or Arrow Keys to move, ESC to quit")

while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # --- Player Movement ---
    keys = pygame.key.get_pressed()
    
    is_moving = False
    
    # WASD or Arrow keys
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_rect.x -= player_speed
        is_moving = True
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_rect.x += player_speed
        is_moving = True
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_rect.y -= player_speed
        is_moving = True
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_rect.y += player_speed
        is_moving = True
    
    # Update animation
    if is_moving:
        animation_counter += 1
        if animation_counter >= animation_speed:
            animation_counter = 0
            animation_frame = (animation_frame + 1) % 2
            
            if animation_frame == 0:
                current_sprite = player_walk1
            else:
                current_sprite = player_walk2
    else:
        current_sprite = player_standing
        animation_frame = 0
        animation_counter = 0
    
    # Keep player within map bounds
    max_x = tmx_data.width * tile_width - player_size
    max_y = tmx_data.height * tile_height - player_size
    player_rect.x = max(0, min(player_rect.x, max_x))
    player_rect.y = max(0, min(player_rect.y, max_y))
    
    # --- Camera follows player ---
    camera_x = player_rect.centerx - WIDTH // 2
    camera_y = player_rect.centery - HEIGHT // 2
    
    # Keep camera within map bounds
    camera_x = max(0, min(camera_x, tmx_data.width * tile_width - WIDTH))
    camera_y = max(0, min(camera_y, tmx_data.height * tile_height - HEIGHT))
    
    # --- Drawing ---
    screen.fill((30, 30, 30))
    
    draw_map(camera_x, camera_y)
    draw_player(camera_x, camera_y)
    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()