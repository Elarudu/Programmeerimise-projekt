#Alfaversiooni fail, Elar Udumets, Mio Cristopher Vahtra, käivitamiseks: python projekti_alfaversioon.py

import pygame
import sys

pygame.init()

# Get monitor resolution
info = pygame.display.Info()
laius = info.current_w
kõrgus = info.current_h

ekraan = pygame.display.set_mode((laius, kõrgus))  # NOT fullscreen
pygame.display.set_caption("Värviline Mäng")


# Värvid
valge = (255, 255, 255)
punane = (255, 0, 0)
sinine = (0, 0, 255)
kollane = (255, 255, 0)
roheline = (0, 255, 0)

# Tegelane
tegelane_suurus = 50
tegelane_x = laius // 2
tegelane_y = kõrgus // 2
kiirus = 5

# Mängu tsükkel
kell = pygame.time.Clock()
töötab = True

while töötab:
    # Sündmused
    for sündmus in pygame.event.get():
        if sündmus.type == pygame.QUIT:
            töötab = False
    
    # Klaviatuuri sisend
    klahvid = pygame.key.get_pressed()
    
    # Ctrl+Z sulgemine
    if klahvid[pygame.K_LCTRL] and klahvid[pygame.K_z]:
        töötab = False
    if klahvid[pygame.K_RCTRL] and klahvid[pygame.K_z]:
        töötab = False
    
    # Liikumine
    if klahvid[pygame.K_LEFT] or klahvid[pygame.K_a]:
        tegelane_x -= kiirus
    if klahvid[pygame.K_RIGHT] or klahvid[pygame.K_d]:
        tegelane_x += kiirus
    if klahvid[pygame.K_UP] or klahvid[pygame.K_w]:
        tegelane_y -= kiirus
    if klahvid[pygame.K_DOWN] or klahvid[pygame.K_s]:
        tegelane_y += kiirus
    
    # Piiri kontroll
    if tegelane_x < 0:
        tegelane_x = 0
    if tegelane_x > laius - tegelane_suurus:
        tegelane_x = laius - tegelane_suurus
    if tegelane_y < 0:
        tegelane_y = 0
    if tegelane_y > kõrgus - tegelane_suurus:
        tegelane_y = kõrgus - tegelane_suurus
    
    # Joonistamine
    # Neli värvilist nurka
    pygame.draw.rect(ekraan, punane, (0, 0, laius//2, kõrgus//2))
    pygame.draw.rect(ekraan, sinine, (laius//2, 0, laius//2, kõrgus//2))
    pygame.draw.rect(ekraan, kollane, (0, kõrgus//2, laius//2, kõrgus//2))
    pygame.draw.rect(ekraan, roheline, (laius//2, kõrgus//2, laius//2, kõrgus//2))
    
    # Tegelane (valge ruut)
    pygame.draw.rect(ekraan, valge, (tegelane_x, tegelane_y, tegelane_suurus, tegelane_suurus))
    
    # Uuenda ekraani
    pygame.display.flip()
    kell.tick(60)

# Sulge pygame
pygame.quit()
sys.exit()
