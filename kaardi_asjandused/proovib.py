import pygame
import pytmx
import os

pygame.init()
#ekraani värk
laius = 640
kõrgus = 480
ekraan = pygame.display.set_mode((laius, kõrgus))

#tegelase värk
tegelase_kiirus = 5
tegelase_rect = pygame.Rect(300, 200, 50, 50)

#tick kiirus
clock = pygame.time.Clock()

#laeme kaardi faili
script_dir = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(script_dir, "level.tmx")
tmxdata = pytmx.load_pygame(map_path)

mäng_töötab = True

while mäng_töötab:
    #Kinni panemine
    for vajutus in pygame.event.get():
        if vajutus.type == pygame.QUIT:
            mäng_töötab = False

    #tegelase liikumine
    klahvid = pygame.key.get_pressed()
    if klahvid[pygame.K_LEFT]:
        tegelase_rect.x -= tegelase_kiirus
    if klahvid[pygame.K_RIGHT]:
        tegelase_rect.x += tegelase_kiirus  
    if klahvid[pygame.K_UP]:
        tegelase_rect.y -= tegelase_kiirus
    if klahvid[pygame.K_DOWN]:
        tegelase_rect.y += tegelase_kiirus

    #kaamera asukoht    
    kaamera_x = tegelase_rect.x - laius // 2
    kaamera_y = tegelase_rect.y - kõrgus // 2

    #joonistame ekraanile midagi
    ekraan.fill((0, 0, 0))
    #kaardi joonistamine
    #alustab iga kaardi kontrollimist
    for kiht in tmxdata.visible_layers:
        #kui see on ruudu  kiht (ehk mitte pildi või object kiht)
        if isinstance(kiht, pytmx.TiledTileLayer):
            #vaatab kihi asukohta ning tema global id
            for x, y, gid in kiht:
                #võtab ruudu pildi
                ruut = tmxdata.get_tile_image_by_gid(gid)
                #kui ruut eksisteerib
                if ruut:
                    ekraan_x = x * tmxdata.tilewidth - kaamera_x
                    ekraan_y = y * tmxdata.tileheight - kaamera_y
                    ekraan.blit(ruut, (ekraan_x, ekraan_y))
    #tegelase joonistamine
    tegelase_joonistus_rect = pygame.Rect(
        tegelase_rect.x - kaamera_x,
        tegelase_rect.y - kaamera_y,
        tegelase_rect.width,
        tegelase_rect.height
    )
    pygame.draw.rect(ekraan, (255, 0, 0), tegelase_rect)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
    