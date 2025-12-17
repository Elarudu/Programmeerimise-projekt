import pygame
import pytmx
import os

pygame.init()
pygame.mixer.init()
#ekraani värk
laius = 640
kõrgus = 480
ekraan = pygame.display.set_mode((laius, kõrgus))
#taustamuss
bgm = pygame.mixer.Sound('medieval_muss.mp3')
bgm.play(-1)
#sfx
kababoom = pygame.mixer.Sound('kaboom.mp3')

#tegelase värk
tegelase_kiirus = 30
tegelase_rect = pygame.Rect(100, 500, 50, 50)

#mängu_režiim
tegelase_tegevus = "kõnnib"

#sõnastik küsimustele
küsimused = {
    "mata_küssa": {"küsimus": "Kas nullmaatriksi pöördmaatriks on nullmaatriks?", "vastus": "jah", "salanumber": 67},
    "proge_küssa": {"küsimus": "Kas ennikuse saab lisada elemente?", "vastus": "ei", "salanumber": 7},
}

#tick kiirus
clock = pygame.time.Clock()

#laeme kaardi faili
script_dir = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(script_dir, "level.tmx")
tmxdata = pytmx.load_pygame(map_path)

#seinad
seinad = []
for kiht in tmxdata.visible_layers:
    if isinstance(kiht, pytmx.TiledTileLayer):
        for x, y, gid in kiht:
            omadused = tmxdata.get_tile_properties_by_gid(gid)
            if omadused:
                if omadused.get("solid"):
                    sein = pygame.Rect(x * tmxdata.tilewidth, y * tmxdata.tileheight, tmxdata.tilewidth, tmxdata.tileheight)
                    seinad.append(sein)
print(len(seinad), "seina ruutu leitud.")

#küssa kohade leidmine
küsimuste_kohad = []
for kiht in tmxdata.visible_layers:
    if isinstance(kiht, pytmx.TiledTileLayer):
        for x, y, gid in kiht:
            omadused = tmxdata.get_tile_properties_by_gid(gid)
            if omadused:
                if omadused.get("quiz_id"):
                    küssa_koht = pygame.Rect(x * tmxdata.tilewidth, y * tmxdata.tileheight, tmxdata.tilewidth, tmxdata.tileheight)
                    küsimuste_kohad.append((küssa_koht, omadused["quiz_id"]))
#uksekoodi asukoha leidmine                    
uksekoodi_kohad = []
for kiht in tmxdata.visible_layers:
    if isinstance(kiht, pytmx.TiledTileLayer):
        for x, y, gid in kiht:
            omadused = tmxdata.get_tile_properties_by_gid(gid)
            if omadused:
                if omadused.get("uksekood"):
                    uksekoodi_koht = pygame.Rect(x * tmxdata.tilewidth, y * tmxdata.tileheight, tmxdata.tilewidth, tmxdata.tileheight)
                    uksekoodi_kohad.append(uksekoodi_koht)

font = pygame.font.Font(None, 32)
praegune_küsimus = None
mängija_sisestus = ""
uksekood = "67"
                    
mäng_töötab = True

while mäng_töötab:
    #Kinni panemine ja muu loogika asjandused
    for vajutus in pygame.event.get():
        if vajutus.type == pygame.QUIT:
            mäng_töötab = False
        elif tegelase_tegevus == "vastab_küssale" and vajutus.type == pygame.KEYDOWN:
            if vajutus.key == pygame.K_BACKSPACE:
                mängija_sisestus = mängija_sisestus[:-1]
            elif vajutus.key == pygame.K_RETURN:
                    if mängija_sisestus.strip().lower() == praegune_küsimus["vastus"].lower():
                        print("Õige!")
                        #lahe sfx
                        kababoom.play()
                        tegelase_tegevus = "näeb_salanumbrit"
                        mängija_sisestus = ""
                    else:
                        print("lollaka alert!")
                        mängija_sisestus = ""
            else:
                mängija_sisestus += vajutus.unicode
        #salanumbri vaatamine
        elif tegelase_tegevus == "näeb_salanumbrit" and vajutus.type == pygame.KEYDOWN:
            if vajutus.key == pygame.K_RETURN:
                tegelase_tegevus = "kõnnib"
        #uksekoodi vastamine
        elif tegelase_tegevus == "uksekoodi_vastamine" and vajutus.type == pygame.KEYDOWN:
            if vajutus.key == pygame.K_BACKSPACE:
                mängija_sisestus = mängija_sisestus[:-1]
            elif vajutus.key == pygame.K_RETURN:
                if mängija_sisestus.strip().lower() == uksekood:
                    print("Uks avatud!")
                    kababoom.play()
                    kababoom.play()
                    kababoom.play()
                    tegelase_tegevus = "kõnnib"
                    mängija_sisestus = ""
                    uks_kiht = tmxdata.get_layer_by_name("aari_uks")
                    uks_kiht.visible = False
                    uksekoodi_kohad = []
                else:
                    print("Vale uksekood!")
                    mängija_sisestus = ""
            else:
                mängija_sisestus += vajutus.unicode
    #tegelase liikumine
    klahvid = pygame.key.get_pressed()
    muutus_x = 0
    muutus_y = 0
    if tegelase_tegevus == "kõnnib":
        if klahvid[pygame.K_LEFT]: muutus_x = -tegelase_kiirus
        if klahvid[pygame.K_RIGHT]: muutus_x = tegelase_kiirus
        if klahvid[pygame.K_UP]: muutus_y = -tegelase_kiirus
        if klahvid[pygame.K_DOWN]: muutus_y = tegelase_kiirus

    #tegelase liikumine vol.2 (vasak, parem)
    tegelase_rect.x += muutus_x
    for sein in seinad:
        #kas tegelase rect puutub seina rect
        if tegelase_rect.colliderect(sein):
            if muutus_x > 0:  # liikudes paremalt seina vastu
                tegelase_rect.right = sein.left  # muudad tegelase parema külje sama asukohaks nagu seina vasak külg
            if muutus_x < 0:  # liikudes vasakult seina vastu
                tegelase_rect.left = sein.right  #muudad tegelase vasaku külje sama asukohaks nagu seina parem külg
    #tegelase liikumine vol.2 jätkub (üles, alla)
    tegelase_rect.y += muutus_y
    for sein in seinad:
        #kas tegelase rect puutub seina rect
        if tegelase_rect.colliderect(sein):
            if muutus_y > 0:  # liikudes alt seina vastu
                tegelase_rect.bottom = sein.top  # muudad tegelase alumise külje sama asukohaks nagu seina ülemine külg
            if muutus_y < 0:  # liikudes ülevalt seina vastu
                tegelase_rect.top = sein.bottom  #muudad tegelase ülemise külje sama asukohaks nagu seina alumine külg
    
    #küsimuse trigger
    for ala, id in küsimuste_kohad:
        if tegelase_rect.colliderect(ala):
            tegelase_tegevus = "vastab_küssale"
            praegune_küsimus = küsimused[id]
            print("alustame küsimisega!", id)
            tegelase_rect.y -= 1
    #uksekoodi trigger
    for koht in uksekoodi_kohad:
        if tegelase_rect.colliderect(koht):
            tegelase_tegevus = "uksekoodi_vastamine"
            tegelase_rect.y += 1
    #kaamera asukoht    
    kaamera_x = tegelase_rect.x - 300
    kaamera_y = tegelase_rect.y - 200

    #joonistame ekraanile backgroundi
    ekraan.fill((0, 0, 0))

    #KAARDI JOONISTAMINE
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
    #joonistame kasti küssale
    if tegelase_tegevus == "vastab_küssale":
        #küsimuse aken
        pygame.draw.rect(ekraan, (50, 50, 50), (0, 100, 800, 200))
        küsimus_tekst = font.render(praegune_küsimus["küsimus"], True, (255, 255, 255))
        ekraan.blit(küsimus_tekst, (25, 120))
        vastus_aken = font.render("Vastus: " + mängija_sisestus, True, (100, 255, 100))
        ekraan.blit(vastus_aken, (25, 160))
    #salanumbri aken   
    elif tegelase_tegevus == "näeb_salanumbrit":
        pygame.draw.rect(ekraan, (50, 50, 60), (100, 100, 400, 200))
        salalanumber = praegune_küsimus["salanumber"]
        salanumbri_aken = font.render(f"Salanumber: {salalanumber}", True, (255, 255, 0))
        ekraan.blit(salanumbri_aken, (225, 150))
    #uksekoodi aken
    elif tegelase_tegevus == "uksekoodi_vastamine":
        pygame.draw.rect(ekraan, (50, 50, 50), (0, 100, 800, 200))
        uksekoodi_tekst = font.render("Sisesta uksekood:", True, (255, 255, 255))
        ekraan.blit(uksekoodi_tekst, (25, 120))
        uksekoodi_aken = font.render("Kood: " + mängija_sisestus, True, (100, 255, 100))
        ekraan.blit(uksekoodi_aken, (25, 160))

    pygame.draw.rect(ekraan, (255, 0, 0), tegelase_joonistus_rect)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()