# ...existing code...
import pygame

pygame.init()

ruudu_suurus = 64

# --- Kaardi andmed ---
map_andmed = [
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
    [0]*30,
]

# arvuta mõõtmed alles pärast map_andmed määramist
map_pikkus = len(map_andmed)
map_laius = len(map_andmed[0]) if map_andmed else 0

ekraan = pygame.display.set_mode((map_laius * ruudu_suurus, map_pikkus * ruudu_suurus))
clock = pygame.time.Clock()

# --- Lae pilt (turvaliselt) ---
try:
    linux = pygame.image.load("pildid/linux.png").convert_alpha()
    linux = pygame.transform.scale(linux, (ruudu_suurus, ruudu_suurus))
except Exception:
    linux = None

# --- Pildid või värvid sõnastikus ---
tiles = {
    0: (218, 230, 238),  # taustavärv
    1: linux if linux is not None else (150, 150, 150)  # pilt või fallback värv
}
# --- Tegelase omadused ---
x = (map_laius * ruudu_suurus) // 2
y = (map_pikkus * ruudu_suurus) // 2
  # tegelase algpositsioon X
  # tegelase algpositsioon Y
width = 40
height = 40
vel = 10  # liikumise kiirus


def main():
    global x, y
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Tegelase liikumine ---
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and x > 0:
            x -= vel
        if keys[pygame.K_RIGHT] and x < map_laius * ruudu_suurus - width:
            x += vel
        if keys[pygame.K_UP] and y > 0:
            y -= vel
        if keys[pygame.K_DOWN] and y < map_pikkus * ruudu_suurus - height:
            y += vel

        ekraan.fill(tiles[0])

        # --- Joonista kaart ---
        for j, row in enumerate(map_andmed):
            for i, tile in enumerate(row):
                val = tiles.get(tile, tiles[0])
                if isinstance(val, tuple):
                    pygame.draw.rect(
                        ekraan,
                        val,
                        (i * ruudu_suurus, j * ruudu_suurus, ruudu_suurus, ruudu_suurus)
                    )
                elif val is not None:
                    ekraan.blit(val, (i * ruudu_suurus, j * ruudu_suurus))

        # --- Joonista tegelane ---
        pygame.draw.rect(ekraan, (255, 0, 0), (x, y, width, height))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    finally:
        pygame.quit()