# SymptomTracker

A SymptomTracker egy saját szerveren futtatható webalkalmazás
étel- és italfogyasztás, gyógyszerszedés és tünetek naplózására,
valamint a rögzített adatok elemzésére.

Célja egy strukturált személyes napló vezetése és a rögzített
események közötti lehetséges összefüggések vizsgálatának segítése.

## Főbb funkciók

- étel- és italnapló
- tünetnapló
- gyógyszerszedés naplózása
- tünetek erősségének rögzítése
- érintett testrészek megadása
- képek csatolása ételekhez és tünetekhez
- alapanyag-adatbázis
- rizikókomponens-adatbázis
- alapanyag/rizikókomponens kapcsolatok
- rögzített események statisztikai elemzése
- magyar és angol kezelőfelület
- többnyelvű referenciaadatok
- Excel-export
- mobilbarát webes felület
- saját PostgreSQL-adatbázis

## A telepítőben található referenciaadatok

Egy új telepítés tartalmazza az alkalmazás alapvető
referenciaadatait:

- alapanyagok
- alapanyagok fordításai
- rizikókomponensek
- rizikókomponensek fordításai
- alapanyag/rizikókomponens kapcsolatok
- tünettípusok
- tünettípusok fordításai
- testrészek
- testrészek fordításai
- alapértelmezett gyógyszerek

A kiadott programcsomag személyes naplóadatokat nem tartalmaz.

Nem kerülnek bele többek között a fejlesztő:

- eseményei
- ételei és receptjei
- ételfotói
- tüneteseményei
- tünetfotói
- gyógyszerbevételi eseményei

## Rendszerkövetelmények

A jelenleg támogatott telepítési cél:

- Ubuntu 24.04 LTS
- x86-64
- internetkapcsolat a telepítés során

A telepítőt úgy készítjük, hogy a szükséges futtatási
komponenseket lehetőség szerint automatikusan telepítse és
konfigurálja.

## Telepítés

A SymptomTracker jelenleg alpha fejlesztési állapotban van.

A publikus alpha kiadáshoz tartozó pontos telepítési útmutató a
kiadási csomag elkészülte után kerül ide.

## Nyelvek

Az alkalmazás jelenleg az alábbi nyelveket támogatja:

- magyar
- angol

A telepítő szintén magyar és angol nyelven használható.

## Adattárolás

A SymptomTracker saját szerveren futtatható alkalmazás.

Az alkalmazás adatai a telepítést üzemeltető személy által
felügyelt PostgreSQL-adatbázisban találhatók. A feltöltött képek
a SymptomTrackert futtató gépen kerülnek tárolásra.

A saját adatok megfelelő védelme, biztonsági mentése és kezelése
a felhasználó, illetve a rendszert üzemeltető személy feladata.

## Egészségügyi figyelmeztetés

A SymptomTracker naplózó és adatelemző eszköz. Nem orvostechnikai
eszköz, és nem szolgáltat orvosi diagnózist, orvosi tanácsot vagy
kezelési javaslatot.

Az alkalmazás által kimutatott statisztikai összefüggések vagy
kockázati jelzések önmagukban nem bizonyítanak ok-okozati
kapcsolatot, allergiát, intoleranciát vagy más betegséget.

A SymptomTracker nem helyettesíti az orvosi vizsgálatot,
diagnózist vagy kezelést.

További információ a [DISCLAIMER.md](DISCLAIMER.md) fájlban
található.

## Fejlesztési állapot

A SymptomTracker jelenleg alpha állapotú szoftver.

A funkciók, az adatbázis szerkezete, a telepítési folyamat és a
kezelőfelület a stabil verzió megjelenéséig változhat.

Fontos egészségügyi adatok egyetlen tárolási helyeként alpha
verzió használata nem javasolt.

## Licenc

A SymptomTracker szabad és nyílt forráskódú szoftver, amely a
GNU General Public License 3. verziója alatt kerül kiadásra.

A teljes licenc a [LICENSE](LICENSE) fájlban található.

## English documentation

English documentation is available in
[README.md](README.md).

## A fejlesztés támogatása

A SymptomTracker ingyenes és nyílt forráskódú szoftver.

Ha hasznosnak találod a projektet és támogatnád a további fejlesztését,
ezt Patreonon teheted meg:

https://www.patreon.com/c/ZoltanRigo
