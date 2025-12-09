import pygame
import pytmx

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Load TMX Map ---
tmx_data = pytmx.load_pygame("level.tmx")
tile_width = tmx_data.tilewidth
tile_height = tmx_data.tileheight

# --- Player Setup (MUST BE BEFORE GAME LOOP) ---
player_size = 32
player_x = WIDTH // 2  # Start in middle of screen
player_y = HEIGHT // 2
player_speed = 4

# Create player rect for position and collision
player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

# Player color
player_color = (255, 100, 100)  # Red

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
    pygame.draw.rect(screen, player_color, (screen_x, screen_y, player_size, player_size))
    
    # Draw a simple face
    eye_size = 4
    # Eyes
    pygame.draw.circle(screen, (255, 255, 255), 
                      (screen_x + 10, screen_y + 10), eye_size)
    pygame.draw.circle(screen, (255, 255, 255), 
                      (screen_x + 22, screen_y + 10), eye_size)
    # Pupils
    pygame.draw.circle(screen, (0, 0, 0), 
                      (screen_x + 10, screen_y + 10), 2)
    pygame.draw.circle(screen, (0, 0, 0), 
                      (screen_x + 22, screen_y + 10), 2)

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
    
    # WASD or Arrow keys
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
    
    draw_map(camera_x, camera_y)
    draw_player(camera_x, camera_y)
    
    # Debug info
    font = pygame.font.Font(None, 24)
    pos_text = font.render(f"Position: ({player_rect.x}, {player_rect.y})", True, (255, 255, 255))
    screen.blit(pos_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()