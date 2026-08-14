# SymptomTracker telepítési útmutató

Ez az útmutató a SymptomTracker nyilvános alfa kiadásának friss szerverre történő telepítését írja le.

> **Alfa szoftver:** a ``0.1.0-alpha.1`` tesztelésre szánt kiadás. A telepítési és frissítési folyamat az első stabil verzióig még változhat. Fontos adatokról mindig legyen külön biztonsági mentés.

## Támogatott telepítési környezet

Az automatikus telepítő jelenleg az alábbi környezetet célozza:

- Ubuntu 24.04 LTS
- x86_64 / amd64
- systemd
- működő internetkapcsolat a telepítés alatt
- root (`sudo`) jogosultság

A telepítő előkészíti a szükséges rendszerkomponenseket, Python-környezetet, Docker-komponenseket, PostgreSQL-adatbázist és systemd szolgáltatást.

## Mit végez el a telepítő?

Friss telepítéskor a telepítő:

1. ellenőrzi az operációs rendszert és a szükséges release fájlokat;
2. meglévő SymptomTracker telepítés észlelésekor nem írja azt felül;
3. telepíti a szükséges Ubuntu csomagokat;
4. szükség esetén telepíti a Docker Engine-t és Docker Compose-t, illetve megfelelő meglévő telepítés esetén azt használja;
5. automatikusan szabad portokat keres, tehát nem feltételezi, hogy az ``5432`` és ``5060`` szabad;
6. létrehozza a ``symptomtracker`` rendszerfelhasználót;
7. telepíti az alkalmazást a ``/opt/symptomtracker`` könyvtárba;
8. egyedi PostgreSQL-jelszót és Flask titkos kulcsot generál;
9. létrehozza a privát ``.env`` konfigurációt;
10. elindít egy külön PostgreSQL 16 konténert;
11. létrehozza a Python virtuális környezetet és telepíti a ``requirements.txt`` fájlban rögzített Python-függőségeket;
12. lefuttatja az összes adatbázis-migrációt;
13. betölti a kiadásban található újrahasznosítható referenciaadatokat;
14. létrehozza és engedélyezi a ``symptomtracker.service`` szolgáltatást;
15. elindítja az alkalmazást és működési ellenőrzéseket végez.

## Release letöltése

Töltsd le a kívánt SymptomTracker kiadáshoz csatolt archívumot a projekt GitHub Releases oldaláról.

Az első nyilvános alfa kiadás:

`v0.1.0-alpha.1`

Friss telepítéshez ne másolj át ``.env`` fájlt, adatbázismentést, személyes feltöltéseket vagy más privát adatokat a fejlesztői telepítésből.

## Kicsomagolás

A pontos fájlnév a GitHub Release-hez publikált csomagtól függhet. Például:

```bash
tar -xzf symptomtracker-0.1.0-alpha.1.tar.gz
cd symptomtracker
```

## Opcionális próbaüzem

A telepítő valódi rendszermódosítás nélkül is futtatható:

```bash
./installer/install.sh --dry-run
```

Induláskor kiválasztható a telepítő nyelve:

- Magyar
- English

A próbaüzem ellenőrzi a telepítőcsomagot és a környezetet, valamint megmutatja a tervezett portokat, de nem telepít és nem módosítja a rendszert.

## Telepítés

Indítsd el a telepítőt root jogosultsággal:

```bash
sudo ./installer/install.sh
```

Válaszd ki a kívánt nyelvet, majd kövesd a telepítő kimenetét.

## Automatikus portválasztás

A SymptomTracker telepítője szándékosan nem követeli meg, hogy az alapértelmezett portok szabadok legyenek.

Az adatbázis host portjához innen kezd szabad portot keresni:

`5432`

Az alkalmazáshoz pedig innen:

`5060`

Ha például egy másik PostgreSQL már használja az ``5432`` portot, és egy másik alkalmazás az ``5060`` portot, a telepítő automatikusan választhatja az ``5433`` és ``5061`` portokat.

A kiválasztott portokat elmenti a telepítés konfigurációjába, és ugyanazokat használja a Docker, az adatbázis-kapcsolat és a systemd szolgáltatás konfigurálásakor.

A PostgreSQL konténeren belül továbbra is a szabványos ``5432`` port használatos; dinamikusan csak a host oldali port kerül kiválasztásra.

## Telepítési könyvtár

Az alkalmazás ide kerül:

```text
/opt/symptomtracker
```

Fontos könyvtárak és fájlok:

```text
/opt/symptomtracker/.env
/opt/symptomtracker/uploads
/opt/symptomtracker/uploads/foods
/opt/symptomtracker/uploads/symptoms
/opt/symptomtracker/backups
```

A ``.env`` telepítésspecifikus titkokat tartalmaz. **Ne publikáld, ne tedd Gitbe és ne oszd meg.**

## Adatbázis

Friss telepítéskor egy külön PostgreSQL 16 Docker-konténer készül, neve:

```text
symptomtracker-db
```

Az adatbázis neve:

```text
symptomtracker
```

Az adatbázis-felhasználó:

```text
symptomtracker_user
```

Az adatbázis jelszavát a telepítő automatikusan generálja, az nem része a nyilvános release-nek.

## Kezdeti referenciaadatok

Az új telepítés betölti a release-ben található újrahasznosítható referenciaadatokat, többek között:

- alapanyagokat és fordításaikat;
- rizikókomponenseket és fordításaikat;
- alapanyag/rizikókomponens kapcsolatokat;
- tünettípusokat és fordításaikat;
- testrészeket és fordításaikat;
- gyógyszereket.

A nyilvános seed adatok **nem** tartalmazzák a fejlesztő személyes naplóeseményeit, saját étel-/receptadatait, gyógyszereseményeit, tüneteseményeit vagy feltöltött személyes képeit.

## Alkalmazásszolgáltatás

Az alkalmazás systemd szolgáltatása:

```text
symptomtracker.service
```

Állapot ellenőrzése:

```bash
sudo systemctl status symptomtracker.service
```

Legutóbbi alkalmazásnaplók:

```bash
sudo journalctl -u symptomtracker.service -n 100 --no-pager
```

Az alkalmazás újraindítása:

```bash
sudo systemctl restart symptomtracker.service
```

## Adatbázis-konténer hibakeresése

Futó konténerek:

```bash
sudo docker ps
```

A SymptomTracker adatbázis-konténerének vizsgálata:

```bash
sudo docker inspect symptomtracker-db
```

Ha a telepítés a PostgreSQL indításánál hibázik, a napló ellenőrizhető:

```bash
cd /opt/symptomtracker
sudo docker compose --env-file .env -f docker-compose.yml logs --tail=100 db
```

## Biztonsági mentés és frissítés

Ez alfa kiadás. Fontos adatnak ne egy alfa telepítés legyen az egyetlen példánya.

Későbbi frissítések tesztelése előtt legalább ezekről készüljön mentés:

- PostgreSQL-adatbázis;
- ``/opt/symptomtracker/uploads``;
- a helyreállításhoz szükséges telepítésspecifikus konfiguráció.

Meglévő telepítést ne próbálj a friss telepítő ismételt futtatásával felülírni. A telepítő védi a felismert meglévő SymptomTracker telepítéseket. A frissítéshez külön update folyamat készül.

## Hibakeresés

Ha az alkalmazás nem indul, elsőként ezeket ellenőrizd:

```bash
sudo systemctl status symptomtracker.service
sudo journalctl -u symptomtracker.service -n 100 --no-pager
sudo docker ps
```

Ellenőrizd azt is, hogy létezik-e a ``/opt/symptomtracker/.env``, illetve a telepítő által kiválasztott alkalmazás- és adatbázisportot nem használja-e más folyamat.

Az ``.env`` tartalmát nyilvános hibajegyben vagy fórumon ne tedd közzé.

## Egészségügyi figyelmeztetés

A SymptomTracker személyes naplózó, adatrögzítő és információs elemzőeszköz.

**Nem orvostechnikai eszköz**, és nem helyettesíti az egészségügyi szakember tanácsát, diagnózisát vagy kezelését. Az alkalmazás által jelzett statisztikai összefüggések, pontszámok, rizikójelzések vagy más eredmények önmagukban nem jelentenek diagnózist és nem bizonyítanak ok-okozati kapcsolatot.

A teljes figyelmeztetés a ``DISCLAIMER.md`` fájlban található.

## Licenc

A SymptomTracker ingyenes és nyílt forráskódú szoftver, amely a GNU General Public License 3. verziója (GPL-3.0) alatt érhető el.

A teljes licenc a ``LICENSE`` fájlban található.

## A fejlesztés támogatása

Ha hasznosnak találod a SymptomTrackert és támogatnád a további fejlesztését, Patreonon megteheted:

https://www.patreon.com/c/ZoltanRigo
