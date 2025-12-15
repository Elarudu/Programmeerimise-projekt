import pygame
import pytmx
import os

# --- Constants ---
VISUAL_SIZE = 100       # Size to draw the player
HITBOX_WIDTH = 43       # Width of collision (Slightly smaller than tile to fit in doors)
HITBOX_HEIGHT = 74      # Full height
PLAYER_SPEED = 8

# --- Minimap Constants ---
MINIMAP_WIDTH = 200     # Width of the minimap in pixels
BORDER_PADDING = 10     # Space from the top-right corner

# --- Hearts (3 hearts above player) ---
HEARTS_MAX = 3
HEART_ICON_SIZE = (22, 20)
HEART_PADDING = 6
HEART_SPACING = 6
HEART_OFFSET_Y = 12     # pixels above the player's hitbox top

#Mündid
Mündid = 0

def lae_mündi_pilt(script_dir, size=(16, 16)):
    candidates = [
        os.path.join(script_dir, "münt.png"),
    ]

    path = next((p for p in candidates if os.path.exists(p)), None)

    münt_img = pygame.image.load(path).convert_alpha()
    if size is not None:
        münt_img = pygame.transform.scale(münt_img, size)

    return münt_img



def load_heart_images(script_dir, size=(22, 20)):
    candidates = [
        os.path.join(script_dir, "süda.png"),
    ]

    path = next((p for p in candidates if os.path.exists(p)), None)

    heart_full = pygame.image.load(path).convert_alpha()
    if size is not None:
        heart_full = pygame.transform.scale(heart_full, size)

    heart_empty = heart_full.copy()
    heart_empty.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return heart_full, heart_empty


def draw_hearts_above_player(
    screen,
    player_rect,
    camera_x, camera_y,
    hearts, hearts_max,
    heart_full, heart_empty,
    padding=6, spacing=6,
    offset_y=12
):
    hearts = max(0, min(hearts_max, int(hearts)))

    # Player position in screen-space
    cx = player_rect.centerx - camera_x
    top = player_rect.top - camera_y

    hw, hh = heart_full.get_width(), heart_full.get_height()
    box_w = padding * 2 + hearts_max * hw + (hearts_max - 1) * spacing
    box_h = padding * 2 + hh

    box_x = int(cx - box_w // 2)
    box_y = int(top - box_h - offset_y)

    # Clamp so it's always visible
    box_x = max(0, min(box_x, screen.get_width() - box_w))
    box_y = max(0, min(box_y, screen.get_height() - box_h))

    box = pygame.Rect(box_x, box_y, box_w, box_h)

    x = box.x + padding
    y = box.y + padding
    for i in range(hearts_max):
        img = heart_full if i < hearts else heart_empty
        screen.blit(img, (x, y))
        x += hw + spacing

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Full Body Collision + Advanced Minimap")
clock = pygame.time.Clock()

# --- Path Setup ---
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Load Heart Images (süda.png) ---
player_hearts = HEARTS_MAX
try:
    heart_full, heart_empty = load_heart_images(script_dir, size=HEART_ICON_SIZE)
except Exception as e:
    print("CRITICAL ERROR: Could not load heart image(s).")
    print("Error details:", e)
    input("Press Enter to exit...")
    pygame.quit()
    raise

# --- Load TMX Map ---
try:
    map_path = os.path.join(script_dir, "level.tmx")
    tmx_data = pytmx.load_pygame(map_path)
except Exception as e:
    print(f"CRITICAL ERROR: Could not load map at {map_path}")
    print(f"Error details: {e}")
    input("Press Enter to exit...")  # Keeps window open to read error
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
                if gid == 10:
                    is_solid = True

                if is_solid:
                    wall_rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                    walls.append(wall_rect)

print(f"DEBUG: Found {len(walls)} solid walls.")

# --- Advanced Minimap Setup ---
map_pixel_width = tmx_data.width * tile_width
map_pixel_height = tmx_data.height * tile_height
minimap_scale = MINIMAP_WIDTH / map_pixel_width
minimap_height = int(map_pixel_height * minimap_scale)

minimap_img = pygame.Surface((MINIMAP_WIDTH, minimap_height))
minimap_img.fill((30, 30, 30))
minimap_img.set_alpha(220)

for layer in tmx_data.visible_layers:
    if isinstance(layer, pytmx.TiledTileLayer):
        for x, y, gid in layer:
            if gid:
                sx = x * tile_width * minimap_scale
                sy = y * tile_height * minimap_scale
                sw = tile_width * minimap_scale
                sh = tile_height * minimap_scale

                tile_props = tmx_data.get_tile_properties_by_gid(gid)
                is_solid = tile_props and tile_props.get("solid")

                if is_solid or gid == 10:
                    pygame.draw.rect(minimap_img, (180, 180, 180), (sx, sy, sw, sh))
                else:
                    pygame.draw.rect(minimap_img, (60, 80, 60), (sx, sy, sw, sh))

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

# --- Player Setup (Spawn Point) ---
player_x = 2140
player_y = 4085

try:
    spawn_object = tmx_data.get_object_by_name("SpawnPoint")
    player_x = spawn_object.x
    player_y = spawn_object.y
    print(f"DEBUG: Player spawned at {player_x}, {player_y}")
except ValueError:
    print("WARNING: No object named 'SpawnPoint' found in map. Using defaults.")
except Exception:
    print("WARNING: Could not read objects from map.")

player_rect = pygame.Rect(player_x, player_y, HITBOX_WIDTH, HITBOX_HEIGHT)

# Animation State
current_sprite = player_standing
animation_frame = 0
animation_speed = 10
animation_counter = 10

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

    image_x = hitbox_screen_x - (VISUAL_SIZE - HITBOX_WIDTH) // 2
    image_y = hitbox_screen_y - (VISUAL_SIZE - HITBOX_HEIGHT - 13)

    screen.blit(current_sprite, (image_x, image_y))

# --- Game Loop ---
running = True
print("Controls: WASD to move, F for Fullscreen, ESC to quit")
print("Heart test: H = damage, J = heal")

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

            # --- Test hearts ---
            elif event.key == pygame.K_h:
                player_hearts = max(0, player_hearts - 1)
            elif event.key == pygame.K_j:
                player_hearts = min(HEARTS_MAX, player_hearts + 1)

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

    camera_x = max(0, min(camera_x, map_pixel_width - WIDTH))
    camera_y = max(0, min(camera_y, map_pixel_height - HEIGHT))

    # --- Draw ---
    screen.fill((30, 30, 30))
    draw_map(camera_x, camera_y)
    draw_player(camera_x, camera_y)

    # --- Draw hearts above player's head ---
    draw_hearts_above_player(
        screen, player_rect, camera_x, camera_y,
        player_hearts, HEARTS_MAX,
        heart_full, heart_empty,
        padding=HEART_PADDING,
        spacing=HEART_SPACING,
        offset_y=HEART_OFFSET_Y
    )

    # --- Draw Advanced Minimap ---
    minimap_x = WIDTH - MINIMAP_WIDTH - BORDER_PADDING
    minimap_y = BORDER_PADDING
    screen.blit(minimap_img, (minimap_x, minimap_y))

    pygame.draw.rect(screen, (255, 255, 255), (minimap_x, minimap_y, MINIMAP_WIDTH, minimap_height), 2)

    player_mini_x = (player_rect.centerx * minimap_scale) + minimap_x
    player_mini_y = (player_rect.centery * minimap_scale) + minimap_y
    pygame.draw.circle(screen, (255, 50, 50), (int(player_mini_x), int(player_mini_y)), 3)

    camera_mini_x = (camera_x * minimap_scale) + minimap_x
    camera_mini_y = (camera_y * minimap_scale) + minimap_y
    camera_mini_w = WIDTH * minimap_scale
    camera_mini_h = HEIGHT * minimap_scale

    pygame.draw.rect(screen, (255, 255, 0), (camera_mini_x, camera_mini_y, camera_mini_w, camera_mini_h), 1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
