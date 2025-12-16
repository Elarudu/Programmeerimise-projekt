import pygame

pygame.init()
#ekraani värk
laius = 640
kõrgus = 480
ekraan = pygame.display.set_mode((laius, kõrgus))

#tick kiirus
clock = pygame.time.Clock()

mäng_töötab = True

while mäng_töötab:
    #Kinni panemine
    for vajutus in pygame.event.get():
        if vajutus.type == pygame.QUIT:
            mäng_töötab = False
    #joonistame ekraanile midagi
    ekraan.fill((0, 0, 0))  # Must taust
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
    