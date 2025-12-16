''' 1. 2. 3. projekti kirjelduse põhjal

'''
mängija_suurus = 100
hitbox_laius = 43
hitbox_pikkus = 74
mängija_kiirus = 12
mängu_režiim = "walking"
küsimustik = None
kirjutatud = ""
tehtud_küsimustikud = []
küsimustikud = {
"matmaatika": {"küsimus": "5 * 5 + 2", "vastus": 27, "auhind": 1},
"Programmeerimine": {"küsimus": "Kuidas kutsutakse muutujatüüpi mis on '_ _ _ _' vahel?", "vastus": "Sõne", "auhind": 2},
"Freebie": {"küsimus": "Kus majas me praegu oleme?", "vastus": "Delta majas", "auhind": "tegelane läheb suuremaks"},
"Operatsioonisüsteemid": {"küsimus": "Mis käsu abil saab liikuda ühest kaustast teise?", "vastus": "cd", "auhind": 3},
"Sissejuhatus erialasse": {"küsimus": "Mitu sõna minutis pead kirjutama IT tudengina?", "vastus": 60, "auhind": 4},
"Arvuti ja Arhitektuur": {"küsimus": "Mis on CPU?", "vastus": "Central Processing Unit"},
}
