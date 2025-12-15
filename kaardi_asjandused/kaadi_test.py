import pygame
import pytmx
import os

# --- Constants ---
VISUAL_SIZE = 100       # Size to draw the player
HITBOX_WIDTH = 43       # Width of collision
HITBOX_HEIGHT = 74      # Full height
PLAYER_SPEED = 8

# --- Minimap Constants ---
MINIMAP_WIDTH = 200     
BORDER_PADDING = 10     

# --- Hearts ---
HEARTS_MAX = 3
HEART_ICON_SIZE = (22, 20)
HEART_PADDING = 6
HEART_SPACING = 6
HEART_OFFSET_Y = 12     

# --- Quiz Configuration ---
GAME_STATE = "walking" # Options: "walking", "quiz", "success"
current_quiz = None    # Holds active quiz data
user_text = ""         # Stores player typing
collected_numbers = [] # Stores rewards
completed_quizzes = [] # Tracks finished quizzes to prevent re-triggering

# QUIZ DATABASE
# keys must match the 'quiz_id' property in Tiled
QUIZ_DATA = {
    "math_1": {
        "question": "What is 5 * 5 + 2?",
        "answer": "27",
        "reward": "4"
    },
    "prog_1": {
        "question": "Python function keyword?",
        "answer": "def",
        "reward": "9"
    },
    "arch_1": {
        "question": "What does CPU stand for?",
        "answer": "central processing unit",
        "reward": "1"
    }
}

# --- Functions ---

def load_heart_images(script_dir, size=(22, 20)):
    candidates = [os.path.join(script_dir, "süda.png")]
    path = next((p for p in candidates if os.path.exists(p)), None)
    
    if not path:
        # Fallback if image missing: create red square
        surf = pygame.Surface(size)
        surf.fill((255, 0, 0))
        return surf, surf

    heart_full = pygame.image.load(path).convert_alpha()
    if size is not None:
        heart_full = pygame.transform.scale(heart_full, size)

    heart_empty = heart_full.copy()
    heart_empty.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return heart_full, heart_empty

def draw_hearts_above_player(screen, player_rect, camera_x, camera_y, hearts, hearts_max, heart_full, heart_empty, padding=6, spacing=6, offset_y=12):
    hearts = max(0, min(hearts_max, int(hearts)))
    cx = player_rect.centerx - camera_x
    top = player_rect.top - camera_y
    hw, hh = heart_full.get_width(), heart_full.get_height()
    box_w = padding * 2 + hearts_max * hw + (hearts_max - 1) * spacing
    box_h = padding * 2 + hh
    box_x = int(cx - box_w // 2)
    box_y = int(top - box_h - offset_y)
    
    # Clamp to screen
    box_x = max(0, min(box_x, screen.get_width() - box_w))
    box_y = max(0, min(box_y, screen.get_height() - box_h))

    for i in range(hearts_max):
        img = heart_full if i < hearts else heart_empty
        screen.blit(img, (box_x + padding + i*(hw+spacing), box_y + padding))

def load_image(filename):
    paths_to_check = [os.path.join(script_dir, "pildid", filename), os.path.join(script_dir, filename)]
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (VISUAL_SIZE, VISUAL_SIZE))
            except Exception: pass
    return pygame.Surface((VISUAL_SIZE, VISUAL_SIZE)) # Return blank surface if missing

# --- Init ---
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("RPG Quiz Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36) # Default font for quiz

script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Load Assets ---
player_hearts = HEARTS_MAX
heart_full, heart_empty = load_heart_images(script_dir, size=HEART_ICON_SIZE)

# --- Load TMX Map ---
try:
    map_path = os.path.join(script_dir, "level.tmx")
    tmx_data = pytmx.load_pygame(map_path)
except Exception as e:
    print(f"CRITICAL ERROR: Could not load map at {map_path}\n{e}")
    pygame.quit(); exit()

tile_width = tmx_data.tilewidth
tile_height = tmx_data.tileheight

# --- Build Wall & Quiz Lists ---
walls = []
quiz_triggers = []

for layer in tmx_data.visible_layers:
    if isinstance(layer, pytmx.TiledTileLayer):
        for x, y, gid in layer:
            if gid:
                tile_props = tmx_data.get_tile_properties_by_gid(gid)
                
                # Check for Solid Wall
                is_solid = tile_props and tile_props.get("solid")
                if gid == 10: is_solid = True 
                
                if is_solid:
                    rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                    walls.append(rect)

                # Check for Quiz Trigger (Property: 'quiz_id')
                if tile_props:
                    quiz_id = tile_props.get("quiz_id")
                    if quiz_id:
                        rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                        quiz_triggers.append((rect, quiz_id))

print(f"DEBUG: Found {len(walls)} solid walls and {len(quiz_triggers)} quiz triggers.")

# --- Minimap Setup ---
map_pixel_width = tmx_data.width * tile_width
map_pixel_height = tmx_data.height * tile_height
minimap_scale = MINIMAP_WIDTH / map_pixel_width
minimap_height = int(map_pixel_height * minimap_scale)
minimap_img = pygame.Surface((MINIMAP_WIDTH, minimap_height))
minimap_img.fill((30, 30, 30))
minimap_img.set_alpha(220)

# Draw static map to minimap surface
for layer in tmx_data.visible_layers:
    if isinstance(layer, pytmx.TiledTileLayer):
        for x, y, gid in layer:
            if gid:
                sx = x * tile_width * minimap_scale
                sy = y * tile_height * minimap_scale
                sw = tile_width * minimap_scale
                sh = tile_height * minimap_scale
                tile_props = tmx_data.get_tile_properties_by_gid(gid)
                color = (180, 180, 180) if (tile_props and tile_props.get("solid")) else (60, 80, 60)
                if tile_props and tile_props.get("quiz_id"): color = (0, 0, 200) # Blue for quiz
                pygame.draw.rect(minimap_img, color, (sx, sy, sw, sh))

# --- Player Setup ---
player_standing = load_image("tegelane_seisab.png")
player_walk1 = load_image("tegelane_konnib(1).png")
player_walk2 = load_image("tegelane_konnib(2).png")

player_x, player_y = 300, 1200
try:
    spawn_object = tmx_data.get_object_by_name("SpawnPoint")
    player_x, player_y = spawn_object.x, spawn_object.y
except Exception: pass

player_rect = pygame.Rect(player_x, player_y, HITBOX_WIDTH, HITBOX_HEIGHT)
current_sprite = player_standing
animation_frame = 0
animation_counter = 0

def draw_map_layer(camera_x, camera_y):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen_x = x * tile_width - camera_x
                    screen_y = y * tile_height - camera_y
                    if -tile_width < screen_x < WIDTH and -tile_height < screen_y < HEIGHT:
                        screen.blit(tile, (screen_x, screen_y))

# --- Main Game Loop ---
running = True
print("Controls: WASD to move. Type answer when quiz pops up.")

while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        
        # --- QUIZ & SUCCESS INPUT ---
        elif GAME_STATE == "quiz":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if user_text.lower() == current_quiz["answer"].lower():
                        GAME_STATE = "success"
                    else:
                        user_text = "" # Wrong answer
                elif event.key == pygame.K_ESCAPE:
                    GAME_STATE = "walking"
                else:
                    user_text += event.unicode

        elif GAME_STATE == "success":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if current_quiz["reward"] not in collected_numbers:
                    collected_numbers.append(current_quiz["reward"])
                completed_quizzes.append(current_quiz["id"])
                GAME_STATE = "walking"

        # --- WALKING INPUT ---
        elif GAME_STATE == "walking":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_f:
                    if screen.get_flags() & pygame.FULLSCREEN:
                        screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
                    else:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    WIDTH, HEIGHT = screen.get_size()
                elif event.key == pygame.K_h: player_hearts = max(0, player_hearts - 1)
                elif event.key == pygame.K_j: player_hearts = min(HEARTS_MAX, player_hearts + 1)

    # 2. Game Logic
    if GAME_STATE == "walking":
        keys = pygame.key.get_pressed()
        is_moving = False
        move_x, move_y = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]: move_x = -PLAYER_SPEED; is_moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_x = PLAYER_SPEED; is_moving = True
        
        player_rect.x += move_x
        for wall in walls:
            if player_rect.colliderect(wall):
                if move_x > 0: player_rect.right = wall.left
                elif move_x < 0: player_rect.left = wall.right

        if keys[pygame.K_UP] or keys[pygame.K_w]: move_y = -PLAYER_SPEED; is_moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]: move_y = PLAYER_SPEED; is_moving = True

        player_rect.y += move_y
        for wall in walls:
            if player_rect.colliderect(wall):
                if move_y > 0: player_rect.bottom = wall.top
                elif move_y < 0: player_rect.top = wall.bottom

        # Check for Quiz Trigger
        for rect, q_id in quiz_triggers:
            if player_rect.colliderect(rect):
                if q_id in QUIZ_DATA and q_id not in completed_quizzes:
                    GAME_STATE = "quiz"
                    current_quiz = QUIZ_DATA[q_id]
                    current_quiz["id"] = q_id
                    user_text = ""
                    # Push back slightly to avoid re-trigger loop immediately
                    if move_y < 0: player_rect.y += 10
                    elif move_y > 0: player_rect.y -= 10
                    elif move_x < 0: player_rect.x += 10
                    elif move_x > 0: player_rect.x -= 10

        # Animation
        if is_moving:
            animation_counter += 1
            if animation_counter >= 10:
                animation_counter = 0
                animation_frame = (animation_frame + 1) % 2
                current_sprite = player_walk1 if animation_frame == 0 else player_walk2
        else:
            current_sprite = player_standing

    # 3. Drawing
    camera_x = max(0, min(player_rect.centerx - WIDTH // 2, map_pixel_width - WIDTH))
    camera_y = max(0, min(player_rect.centery - HEIGHT // 2, map_pixel_height - HEIGHT))

    screen.fill((30, 30, 30))
    draw_map_layer(camera_x, camera_y)
    
    # Draw Player
    hitbox_screen_x = player_rect.x - camera_x
    hitbox_screen_y = player_rect.y - camera_y
    image_x = hitbox_screen_x - (VISUAL_SIZE - HITBOX_WIDTH) // 2
    image_y = hitbox_screen_y - (VISUAL_SIZE - HITBOX_HEIGHT - 13)
    screen.blit(current_sprite, (image_x, image_y))

    draw_hearts_above_player(screen, player_rect, camera_x, camera_y, player_hearts, HEARTS_MAX, heart_full, heart_empty)

    # Draw Minimap
    minimap_x = WIDTH - MINIMAP_WIDTH - BORDER_PADDING
    minimap_y = BORDER_PADDING
    screen.blit(minimap_img, (minimap_x, minimap_y))
    pygame.draw.rect(screen, (255, 255, 255), (minimap_x, minimap_y, MINIMAP_WIDTH, minimap_height), 2)
    
    # Player dot on minimap
    player_mini_x = (player_rect.centerx * minimap_scale) + minimap_x
    player_mini_y = (player_rect.centery * minimap_scale) + minimap_y
    pygame.draw.circle(screen, (255, 50, 50), (int(player_mini_x), int(player_mini_y)), 3)

    # Draw UI Overlays (Quiz)
    if GAME_STATE == "quiz" or GAME_STATE == "success":
        # Dim background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Box Dimensions
        box_w, box_h = 400, 250
        box_x = (WIDTH - box_w) // 2
        box_y = (HEIGHT - box_h) // 2
        
        pygame.draw.rect(screen, (50, 50, 60), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_w, box_h), 3)

        if GAME_STATE == "quiz":
            q_surf = font.render(current_quiz["question"], True, (255, 255, 255))
            screen.blit(q_surf, (box_x + 20, box_y + 40))
            
            ans_surf = font.render(f"Answer: {user_text}_", True, (100, 255, 100))
            screen.blit(ans_surf, (box_x + 20, box_y + 120))
            
            hint_surf = font.render("Type answer & press ENTER", True, (180, 180, 180))
            screen.blit(hint_surf, (box_x + 20, box_y + 200))

        elif GAME_STATE == "success":
            win_surf = font.render("CORRECT!", True, (0, 255, 0))
            screen.blit(win_surf, (box_x + 130, box_y + 40))
            
            code_surf = font.render(f"Secret Number: {current_quiz['reward']}", True, (255, 215, 0))
            screen.blit(code_surf, (box_x + 50, box_y + 120))
            
            cont_surf = font.render("Press ENTER to continue", True, (200, 200, 200))
            screen.blit(cont_surf, (box_x + 50, box_y + 200))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()