import pygame
pygame.init()
ruudu_suurus = 64
map_pikkus = 12
map_laius = 15
ekraan = pygame.display.set_mode((map_laius * ruudu_suurus, map_pikkus * ruudu_suurus))
clock = pygame.time.Clock()
map_andmed = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ,0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ,0 ,0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0],

]

värvid = {
    0: (218, 230, 238),
    1: (255, 0, 0)
}
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


 # Joonista kaart
    for y, row in enumerate(map_andmed):
        for x, tile in enumerate(row):
            pygame.draw.rect(
                ekraan,
                värvid[tile],
                (x * ruudu_suurus, y * ruudu_suurus, ruudu_suurus, ruudu_suurus)
            )

    pygame.display.flip()
    clock.tick(60)
pygame.quit()

