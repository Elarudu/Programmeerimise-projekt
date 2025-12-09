import pygame
import pytmx
import os

pygame.init()

# --- Screen Setup ---
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

# Set initial window size (mostly full screen, but windowed)
WIDTH, HEIGHT = screen_width - 100, screen_height - 100 

# Create the screen with the RESIZABLE flag
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Map Game")

clock = pygame.time.Clock()

# Track fullscreen state
is_fullscreen = False

# --- Load TMX Map ---
try:
    tmx_data = pytmx.load_pygame("level.tmx")
except Exception as e:
    print(f"Error loading map: {e}")
    pygame.quit()
    exit()

tile_width = tmx_data.tilewidth
tile_height = tmx_data.tileheight

# --- Player Setup ---
player_size = 32
player_x = WIDTH // 2 
player_y = HEIGHT // 2
player_speed = 4

player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

# --- Load Player Image ---
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "pildid", "tegelane_seisab.png")

try:
    original_image = pygame.image.load(image_path).convert_alpha()
    player_image = pygame.transform.scale(original_image, (player_size, player_size))
    print(f"✓ Player image loaded from {image_path}")
except FileNotFoundError:
    print(f"✗ Could not find image at {image_path}. Using red square fallback.")
    player_image = None 

def draw_map(camera_x, camera_y, current_width, current_height):
    """Draw the tilemap with camera offset"""
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen_x = x * tile_width - camera_x
                    screen_y = y * tile_height - camera_y
                    
                    # Only draw tiles visible on screen (Optimization)
                    if (-tile_width < screen_x < current_width and 
                        -tile_height < screen_y < current_height):
                        screen.blit(tile, (screen_x, screen_y))

def draw_player(camera_x, camera_y):
    """Draw the player image"""
    screen_x = player_rect.x - camera_x
    screen_y = player_rect.y - camera_y

    if player_image:
        screen.blit(player_image, (screen_x, screen_y))
    else:
        # Fallback: Red square
        pygame.draw.rect(screen, (255, 100, 100), (screen_x, screen_y, player_size, player_size))

# --- Game Loop ---
running = True
print("Controls:")
print("  WASD/Arrow Keys - Move")
print("  F - Toggle Fullscreen")
print("  ESC - Quit")

while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.VIDEORESIZE:
            # Update dimensions when window is resized
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                
            # Toggle Fullscreen with 'F' key
            elif event.key == pygame.K_f:
                is_fullscreen = not is_fullscreen
                
                if is_fullscreen:
                    # Switch to Fullscreen
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    WIDTH, HEIGHT = screen.get_size()
                    print(f"Switched to FULLSCREEN: {WIDTH}x{HEIGHT}")
                else:
                    # Switch back to Windowed mode
                    WIDTH, HEIGHT = screen_width - 100, screen_height - 100
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    print(f"Switched to WINDOWED: {WIDTH}x{HEIGHT}")

    # --- Player Movement ---
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_rect.x += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_rect.y -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_rect.y += player_speed
    
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
    
    draw_map(camera_x, camera_y, WIDTH, HEIGHT)
    draw_player(camera_x, camera_y)
    
    # Debug info
    font = pygame.font.Font(None, 24)
    mode_text = "FULLSCREEN" if is_fullscreen else "WINDOWED"
    pos_text = font.render(
        f"Pos: ({player_rect.x}, {player_rect.y}) | FPS: {int(clock.get_fps())} | {mode_text} ({WIDTH}x{HEIGHT})", 
        True, (255, 255, 255)
    )
    screen.blit(pos_text, (10, 10))
    
    # Controls reminder
    controls_text = font.render("F - Toggle Fullscreen | ESC - Quit", True, (200, 200, 200))
    screen.blit(controls_text, (10, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()