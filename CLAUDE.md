# Milujeme Baseball — grafiky pro sociální sítě

Tento repozitář slouží k tvorbě IG/FB grafik pro projekt **Milujeme Baseball**
(milujeme-baseball.cz). Grafiky se generují Pythonem (Pillow), ne Canvou.

## Šablony

### KRÁTKÉ ZPRÁVY (`templates/kratke_zpravy.py`)
Speciální šablona pro sérii krátkých zpráv na stories (1080×1920).
Vintage „stamp" styl podle razítkového loga: krémový papír, rezavá červená
(154,51,36), baseballové švy v rozích, „ZPRÁVY" jako nakloněné razítko,
text celý v grafice (žádné CTA na web — jde o samostatné zprávy).

```
python3 templates/kratke_zpravy.py --topic "MLB · APPLE TV" \
    --headline "Titulek zprávy" --text "Celý text zprávy…" [--date "19. 7."]
```

### Tmavý brand styl (rozpisy, GAMEDAY, medaile, rozhovory)
Ostatní grafiky používají tmavý vizuál: pozadí gradient (14,18,32)→(34,24,42),
brand červená (200,30,45), zlatá (216,178,92), krémová (240,236,226),
červené pruhy nahoře a dole. Fonty Liberation Sans (Bold/Regular/BoldItalic).

Formáty: story 1080×1920, příspěvek 4:5 1080×1350.

## Pravidla

- **VŽDY nejdřív navrhni text grafiky ke schválení** (klidně ve variantách)
  a grafiku generuj až po odsouhlasení uživatelem. Neplatí, jen když
  uživatel dodá finální znění sám.

- **Logo projektu** (`templates/assets/logo_project.png`, průhledné PNG)
  vždy NAHOŘE uprostřed, bez podkladové karty.
- **Logo sponzora** (`templates/assets/logo_sponsor_nobg.png`,
  BaseballShop.Online s odstraněným bílým pozadím) vždy DOLE uprostřed
  s popiskem „PARTNER", bez podkladové karty.
- **Hashtagy**: `#MilujemeBaseball  #BaseballCzechia`
  (nikdy #CzechBaseball — uživatel jej nahradil).
- Patička: `milujeme-baseball.cz  ·  #MilujemeBaseball  #BaseballCzechia`.
- U datumů vždy ověř den v týdnu přes `datetime` (už jednou byla chyba).
- České vlajky a vlajky soupeřů se kreslí vektorově (emoji vlajky
  v dostupných fontech nefungují — vykreslí se jako čtverečky).
- Fotky: uživatel je nahrává do chatu; z transkriptu se extrahují
  base64 obrázky (viz historie session). Fotku vždy doplň creditem
  (např. „foto: Matyáš Fous") přímo v grafice.
- U rozhovorů: sada = cover story + Q&A stories (9:16) + carousel 4:5
  (cover → Q&A slidy → závěrečný slide „CELÝ ROZHOVOR najdeš na
  milujeme-baseball.cz").
