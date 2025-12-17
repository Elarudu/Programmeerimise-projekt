import pygame
import pytmx
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
def laadi_pilt(faili_nimi):
    koht = os.path.join(script_dir, faili_nimi)
    if os.path.exists(koht):
        try:
            img = pygame.image.load(koht)
            return pygame.transform.scale(img, (tegelase_suurus, tegelase_suurus))
        except Exception:
            pass
    return pygame.Surface((tegelase_suurus, tegelase_suurus))


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

#Hitboxi muutujad
Hitbox_laius = 43
Hitbox_kõrgus = 74


#tegelase värk
tegelase_suurus = 100
tegelase_kiirus = 12
tegelane_seisab = laadi_pilt("tegelane_seisab.png")
tegelane_konnib1 = laadi_pilt("tegelane_konnib(1).png")
tegelane_konnib2 = laadi_pilt("tegelane_konnib(2).png")
tegelane_surnud = laadi_pilt("tegelane_surnud.png")
tegelane_x, tegelane_y = 300, 1200
mängija_rect = pygame.Rect(tegelane_x, tegelane_y, Hitbox_laius, Hitbox_kõrgus)
tavaline = tegelane_seisab
animatsiooni_framed = 0
animatsiooni_kounter = 0
tegelase_tegevus = "kõnnib"
kui_kõnnib = False

#sõnastik küsimustele
küsimused = {
    "mata_küssa": {"küsimus": "Kas nullmaatriksi pöördmaatriks on nullmaatriks?", "vastus": "jah"},
    "proge_küssa": {"küsimus": "Kas ennikuse saab lisada elemente?", "vastus": "ei"},
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

#küssad
küsimuste_kohad = []
for kiht in tmxdata.visible_layers:
    if isinstance(kiht, pytmx.TiledTileLayer):
        for x, y, gid in kiht:
            omadused = tmxdata.get_tile_properties_by_gid(gid)
            if omadused:
                if omadused.get("quiz_id"):
                    küssa_koht = pygame.Rect(x * tmxdata.tilewidth, y * tmxdata.tileheight, tmxdata.tilewidth, tmxdata.tileheight)
                    küsimuste_kohad.append((küssa_koht, omadused["quiz_id"]))

font = pygame.font.Font(None, 32)
praegune_küsimus = None
mängija_sisestus = ""
                    
mäng_töötab = True

while mäng_töötab:
    #Kinni panemine
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
                        tegelase_tegevus = "kõnnib"
                        mängija_sisestus = ""
                    else:
                        print("lollaka alert!")
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
    kui_kõnnib = muutus_x != 0 or muutus_y != 0
    #Animatsioon
    if kui_kõnnib:
        animatsiooni_framed += 1
        if animatsiooni_framed >= 5:
            animatsiooni_framed = 0
            animatsiooni_kounter = (animatsiooni_kounter + 1) % 2
            tavaline = tegelane_konnib1 if animatsiooni_kounter == 0 else tegelane_konnib2
    else:
        tavaline = tegelane_seisab

    #tegelase liikumine vol.2 (vasak, parem)
    mängija_rect.x += muutus_x
    for sein in seinad:
        #kas tegelase rect puutub seina rect
        if mängija_rect.colliderect(sein):
            if muutus_x > 0:  # liikudes paremalt seina vastu
                mängija_rect.right = sein.left  # muudad tegelase parema külje sama asukohaks nagu seina vasak külg
            if muutus_x < 0:  # liikudes vasakult seina vastu
                mängija_rect.left = sein.right  #muudad tegelase vasaku külje sama asukohaks nagu seina parem külg
    #tegelase liikumine vol.2 jätkub (üles, alla)
    mängija_rect.y += muutus_y
    for sein in seinad:
        #kas tegelase rect puutub seina rect
        if mängija_rect.colliderect(sein):
            if muutus_y > 0:  # liikudes alt seina vastu
                mängija_rect.bottom = sein.top  # muudad tegelase alumise külje sama asukohaks nagu seina ülemine külg
            if muutus_y < 0:  # liikudes ülevalt seina vastu
                mängija_rect.top = sein.bottom  #muudad tegelase ülemise külje sama asukohaks nagu seina alumine külg
    
    #küsimuse trigger
    for ala, id in küsimuste_kohad:
        if mängija_rect.colliderect(ala):
            tegelase_tegevus = "vastab_küssale"
            praegune_küsimus = küsimused[id]
            print("alustame küsimisega!", id)
            mängija_rect.y -= 1

    #kaamera asukoht    
    kaamera_x = mängija_rect.x - 300
    kaamera_y = mängija_rect.y - 200

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

    #joonistame kasti küssale
    if tegelase_tegevus == "vastab_küssale":
        #küsimuse aken
        pygame.draw.rect(ekraan, (50, 50, 50), (0, 100, 800, 200))
        küsimus_tekst = font.render(praegune_küsimus["küsimus"], True, (255, 255, 255))
        ekraan.blit(küsimus_tekst, (25, 120))
        vastus_aken = font.render("Vastus: " + mängija_sisestus, True, (100, 255, 100))
        ekraan.blit(vastus_aken, (25, 160))
    
    pygame.draw.rect(ekraan, (255, 0, 0), mängija_rect)
    ekraan.blit(tavaline, (300, 200))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()