import pygame
import pytmx
import os

script_dir = os.path.dirname(__file__)
map_path = os.path.join(script_dir, "level.tmx")

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Load TMX Map ---
try:
    tmx_data = pytmx.load_pygame(map_path)
    print(f"✓ Map loaded: {map_path}")
    print(f"  Map size: {tmx_data.width} x {tmx_data.height} tiles")
    print(f"  Tile size: {tmx_data.tilewidth} x {tmx_data.tileheight} px")
    
    # Check tilesets and their images
    for tileset in tmx_data.tilesets:
        print(f"  Tileset: {tileset.name}")
        
        # Check if tileset has an image
        if hasattr(tileset, 'source') and tileset.source:
            print(f"    Image source: {tileset.source}")
            
            # Check if the image file actually exists
            image_path = os.path.join(script_dir, tileset.source)
            if os.path.exists(image_path):
                print(f"    ✓ Image file exists at: {image_path}")
            else:
                print(f"    ✗ ERROR: Image file NOT FOUND at: {image_path}")
                print(f"    Please make sure this PNG file exists in the same folder as level.tmx")
        else:
            print(f"    ✗ ERROR: No image source defined in tileset!")
            print(f"    You need to open map.tsx and add an image source")
        
except FileNotFoundError:
    print(f"✗ Error: Could not find {map_path}")
    pygame.quit()
    exit()
except Exception as e:
    print(f"✗ Error loading map: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    exit()

tile_width = tmx_data.tilewidth
tile_height = tmx_data.tileheight

# Camera offset for scrolling
camera_x = 0
camera_y = 0
CAMERA_SPEED = 5

def draw_map():
    tiles_drawn = 0
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen_x = x * tile_width - camera_x
                    screen_y = y * tile_height - camera_y
                    
                    # Only draw tiles that are visible on screen
                    if (-tile_width < screen_x < WIDTH and 
                        -tile_height < screen_y < HEIGHT):
                        screen.blit(tile, (screen_x, screen_y))
                        tiles_drawn += 1
    
    # Print debug info once at startup
    if not hasattr(draw_map, 'debug_printed'):
        print(f"  Tiles drawn on screen: {tiles_drawn}")
        if tiles_drawn == 0:
            print(f"  ✗ WARNING: No tiles visible! Check tileset image path.")
        draw_map.debug_printed = True

# --- Game Loop ---
running = True
print("\nControls: Arrow keys to move camera, ESC to quit")

while running:
    screen.fill((50, 50, 50))  # Dark gray background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Camera movement with arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        camera_x -= CAMERA_SPEED
    if keys[pygame.K_RIGHT]:
        camera_x += CAMERA_SPEED
    if keys[pygame.K_UP]:
        camera_y -= CAMERA_SPEED
    if keys[pygame.K_DOWN]:
        camera_y += CAMERA_SPEED
    
    # Keep camera in bounds
    camera_x = max(0, min(camera_x, tmx_data.width * tile_width - WIDTH))
    camera_y = max(0, min(camera_y, tmx_data.height * tile_height - HEIGHT))

    draw_map()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()