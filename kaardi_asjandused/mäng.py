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
ekraan = pygame.display.set_mode((laius, kõrgus), pygame.SCALED | pygame.RESIZABLE) #Laseb fullscreenile panna ja skaleerib 640x480 fullscreeniks, et pixled ei läheks nihkesse.
#laeme kaardi faili
script_dir = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(script_dir, "level.tmx")
tmxdata = pytmx.load_pygame(map_path)
#taustamuss
bgm = pygame.mixer.Sound('medieval_muss.mp3')
bgm.play(-1)
#sfx
kababoom = pygame.mixer.Sound('kaboom.mp3')

#Hitboxi muutujad
Hitbox_laius = 43
Hitbox_kõrgus = 74

#Mündi koguja
mündid = 0
elud = 3
#spawn koht
spawn_koht = None

for layer in tmxdata.visible_layers:
    if isinstance(layer, pytmx.TiledTileLayer):
        for x, y, gid in layer:
            props = tmxdata.get_tile_properties_by_gid(gid)
            if props and props.get("spawn") is True:
                spawn_koht = (x, y)
                break
        if spawn_koht:
            break
if spawn_koht is not None:
    spawn_x = spawn_koht[0] * tmxdata.tilewidth
    spawn_y = spawn_koht[1] * tmxdata.tileheight
else:
    spawn_x, spawn_y = 0, 0  # fallback
#tegelase värk + lõpu pilt
tegelase_suurus = 100
tegelane_seisab = laadi_pilt("tegelane_seisab.png")
tegelane_konnib1 = laadi_pilt("tegelane_konnib(1).png")
tegelane_konnib2 = laadi_pilt("tegelane_konnib(2).png")
tegelane_surnud = laadi_pilt("tegelane_surnud.png")
aar_pilt = laadi_pilt("aar_haige_küsimus.png")
aar_pilt = pygame.transform.smoothscale(aar_pilt, (300, 200))
mängija_rect = pygame.Rect(
    spawn_x,
    spawn_y,
    Hitbox_laius,
    Hitbox_kõrgus
)

tavaline = tegelane_seisab
animatsiooni_framed = 0
animatsiooni_kounter = 0
tegelase_kiirus = 30
#mängu_režiim
tegelase_tegevus = "kõnnib"
kui_kõnnib = False
#sõnastik küsimustele
küsimused = {
    "mata_küssa": {"küsimus": "Kas nullmaatriksi pöördmaatriks on nullmaatriks (ei/jah)?", "vastus": "jah", "salanumber": 1000},
    "proge_küssa": {"küsimus": "Kas ennikuse saab lisada elemente? (ei/jah)", "vastus": "ei", "salanumber": 500},
    "sissejuh_küssa": {"küsimus": "Kas Mirjamile meeldivad kassid(jah/ei)", "vastus": "jah", "salanumber": 100},
    "opsüs_küssa": {"küsimus": "Kas Terry Davis on proge kunn (jah/ei)?", "vastus": "jah", "salanumber": 67},
                    }

vastatud_küsimused = []
munch_ostetud = False

#tick kiirus
clock = pygame.time.Clock()

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

#söökla asukoha leidmine
söökla_koht = []
for kiht in tmxdata.visible_layers:
    if isinstance(kiht, pytmx.TiledTileLayer):
        for x, y, gid in kiht:
            omadused = tmxdata.get_tile_properties_by_gid(gid)
            if omadused:
                if omadused.get("söök"):
                    söögi_koht = pygame.Rect(x * tmxdata.tilewidth, y * tmxdata.tileheight, tmxdata.tilewidth, tmxdata.tileheight)
                    söökla_koht.append(söögi_koht)
# final boss leidmine
boss_koht = []
for kiht in tmxdata.visible_layers:
    if isinstance(kiht, pytmx.TiledTileLayer):
        for x, y, gid in kiht:
            omadused = tmxdata.get_tile_properties_by_gid(gid)
            if omadused:
                if omadused.get("aari_ava"):
                    bossi_koht = pygame.Rect(x * tmxdata.tilewidth, y * tmxdata.tileheight, tmxdata.tilewidth, tmxdata.tileheight)
                    boss_koht.append(bossi_koht)

font = pygame.font.Font(None, 32)
praegune_küsimus = None
söökla_küsimus = None
mängija_sisestus = ""
uksekood = "1667"
                    
mäng_töötab = True

while mäng_töötab:
    #Kinni panemine ja muu loogika asjandused
    for vajutus in pygame.event.get():
        if vajutus.type == pygame.QUIT:
            mäng_töötab = False
        #küsimusele vastamine
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
                    mündid += 1
                    vastatud_küsimused.append(küsimused[id])
                else:
                    tegelase_tegevus = "vale_vastus"
                    elud -= 1
                    mängija_sisestus = ""
            else:
                mängija_sisestus += vajutus.unicode

        #söökla munchi ostmine
        elif tegelase_tegevus == "ostab_munchi" and vajutus.type == pygame.KEYDOWN:
            if vajutus.key == pygame.K_BACKSPACE:
                mängija_sisestus = mängija_sisestus[:-1]
            elif vajutus.key == pygame.K_RETURN:
                    if mängija_sisestus.strip().lower() == "osta":
                        if mündid >= 2:
                            print("Ostetud!")
                            kababoom.play()
                            mündid -= 2
                            elud += 1
                            mängija_sisestus = ""
                            tegelase_tegevus = "kõnnib"
                            munch_ostetud = True
                        else:
                            print("Pole piisavalt münte!")
                            tegelase_tegevus = "kõnnib"
                            mängija_sisestus = "" 
                    else:
                        tegelase_tegevus = "kõnnib"
                        mängija_sisestus = ""
            else:
                mängija_sisestus += vajutus.unicode
        #vale vastuse kinnitamine
        elif tegelase_tegevus == "vale_vastus" and vajutus.type == pygame.KEYDOWN:
            if vajutus.key == pygame.K_RETURN:
                tegelase_tegevus = "vastab_küssale"
        #salanumbri vaatamine
        elif tegelase_tegevus == "näeb_salanumbrit" and vajutus.type == pygame.KEYDOWN:
            if vajutus.key == pygame.K_RETURN:
                tegelase_tegevus = "kõnnib"
        elif tegelase_tegevus == "võit" and vajutus.type == pygame.KEYDOWN:
            if vajutus.key == pygame.K_RETURN:
                mäng_töötab = False
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
                    tegelase_tegevus = "vale_vastus"
                    mängija_sisestus = ""
            else:
                mängija_sisestus += vajutus.unicode
        #lõpuraundi vastamine
        elif tegelase_tegevus == "lõpuraund" and vajutus.type == pygame.KEYDOWN:
            if vajutus.key == pygame.K_BACKSPACE:
                mängija_sisestus = mängija_sisestus[:-1]
            elif vajutus.key == pygame.K_RETURN:
                if mängija_sisestus.strip().lower() == "b":
                    tegelase_tegevus = "võit"
                else:
                    tegelase_tegevus = "vale_vastus"
                    elud -= 1
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
                mängija_rect.left = sein.right #muudad tegelase vasaku külje sama asukohaks nagu seina parem külg
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
            if tegelase_tegevus == "kõnnib" and id not in vastatud_küsimused:
                tegelase_tegevus = "vastab_küssale"
                praegune_küsimus = küsimused[id]
                print("alustame küsimisega!", id)
                mängija_rect.y -= 10
                vastatud_küsimused.append(id)
    #uksekoodi trigger
    for koht in uksekoodi_kohad:
        if mängija_rect.colliderect(koht) and tegelase_tegevus == "kõnnib":
            tegelase_tegevus = "uksekoodi_vastamine"
            mängija_rect.y += 10
    #söökla trigger
    for söögi_nämnäm in söökla_koht:
        if mängija_rect.colliderect(söögi_nämnäm):
            if munch_ostetud != True and tegelase_tegevus == "kõnnib":
                tegelase_tegevus = "ostab_munchi"
                mängija_rect.y += 100
    #bossi trigger
    for boss in boss_koht:
        if mängija_rect.colliderect(boss):
            if tegelase_tegevus == "kõnnib":
                tegelase_tegevus = "lõpuraund"

    #kaamera asukoht    
    kaamera_x = mängija_rect.x - laius // 2 + Hitbox_laius // 2
    kaamera_y = mängija_rect.y - kõrgus // 2 + Hitbox_kõrgus // 2
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
    #vale vastuse aken
    elif tegelase_tegevus == "vale_vastus":
        pygame.draw.rect(ekraan, (50, 50, 60), (100, 100, 400, 200))
        vale_vastus_aken = font.render("Vale vastus! Proovi uuesti.", True, (255, 0, 0))
        ekraan.blit(vale_vastus_aken, (175, 150))
    #salanumbri aken   
    elif tegelase_tegevus == "näeb_salanumbrit":
        pygame.draw.rect(ekraan, (50, 50, 60), (100, 100, 400, 200))
        salalanumber = praegune_küsimus["salanumber"]
        salanumbri_aken = font.render(f"Salanumber: {salalanumber}", True, (255, 255, 0))
        ekraan.blit(salanumbri_aken, (225, 150))
    #uksekoodi aken
    elif tegelase_tegevus == "uksekoodi_vastamine":
        pygame.draw.rect(ekraan, (50, 50, 50), (0, 100, 800, 200))
        uksekoodi_tekst = font.render("Sisesta uksekood: (liida salakoodid kokku)", True, (255, 255, 255))
        ekraan.blit(uksekoodi_tekst, (25, 120))
        uksekoodi_aken = font.render("Kood: " + mängija_sisestus, True, (100, 255, 100))
        ekraan.blit(uksekoodi_aken, (25, 160))
    #söökla aken
    elif tegelase_tegevus == "ostab_munchi":
        pygame.draw.rect(ekraan, (50, 50, 50), (0, 100, 800, 200))
        söökla_tekst = font.render("Tere tulemast sööklasse! Lõuna maksab 2 münti.", True, (255, 255, 255))
        ekraan.blit(söökla_tekst, (25, 120))
        munchi_aken = font.render(f"Sisesta 'osta' et saada lõuna: " + mängija_sisestus, True, (100, 255, 100))
        ekraan.blit(munchi_aken, (25, 160))
    #lõpuraundi aken
    elif tegelase_tegevus == "lõpuraund":
        pygame.draw.rect(ekraan, (142, 44, 44), (0, 0, 640, 480))
        lõpu_tekst = font.render("Tere tulemast lõppu!!! Lahenda ülesanne, et võita!", True, (255, 255, 255))
        ekraan.blit(lõpu_tekst, (100, 70))
        ülesanne_tekst_1 = (font.render(f"Milline joonisel kujutatud dekoodri väljunditest on aktiivne (1)", True, (255, 255, 255)))
        ekraan.blit(ülesanne_tekst_1, (25, 120))
        ülesanne_tekst_2 = (font.render(f", kui sisendis x1 on väärtus 0 ja sisendis x2 on väärtus 1...  " + mängija_sisestus, True, (255, 255, 255)))
        ekraan.blit(ülesanne_tekst_2, (25, 160))
        ekraan.blit(aar_pilt, (220, 200))
    #võidu aken
    elif tegelase_tegevus == "võit":
        pygame.draw.rect(ekraan, (44, 142, 44), (0, 0, 640, 480))
        võidu_tekst = font.render("Palju õnne! Sa võitsid mängu!", True, (255, 255, 255))
        ekraan.blit(võidu_tekst, (170, 70))
    
    if tegelase_tegevus != "surnud" and tegelase_tegevus != "kõnnib":
        tavaline = None
    #surma joonistus"
    if elud == 0:
        tegelase_tegevus = "surnud"
        tavaline = tegelane_surnud
        tekst = font.render("Kukkusid delta majamängu läbi!", True, (255, 0, 0))
        ekraan.blit(tekst, (170, 70))
    #elude joonistus
    elude_kogus = font.render(f"Elud: {elud}", True, (255, 0, 255))
    ekraan.blit(elude_kogus, (564, 0))
    #müntide joonistus
    müntide_kogus = font.render(f"Mündid: {mündid}", True, (255, 105, 55))
    ekraan.blit(müntide_kogus, (538, 30))
    #joonistame mängija
    if tavaline != None:
        ekraan_x = mängija_rect.x - kaamera_x
        ekraan_y = mängija_rect.y - kaamera_y
        ekraan.blit(tavaline, (ekraan_x, ekraan_y))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()