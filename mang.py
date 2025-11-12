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

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ekraan.fill(tiles[0])

        # --- Joonista kaart ---
        for y, row in enumerate(map_andmed):
            for x, tile in enumerate(row):
                val = tiles.get(tile, tiles[0])
                if isinstance(val, tuple):
                    pygame.draw.rect(
                        ekraan,
                        val,
                        (x * ruudu_suurus, y * ruudu_suurus, ruudu_suurus, ruudu_suurus)
                    )
                elif val is not None:
                    ekraan.blit(val, (x * ruudu_suurus, y * ruudu_suurus))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    finally:
        pygame.quit()