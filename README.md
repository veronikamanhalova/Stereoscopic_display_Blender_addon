# 3D: Stereometrické Renderování v Blenderu

Semestrální práce je na téma stereometrického renderování pro vícepohledovou 3D auto-stereoskopickou obrazovku značky DIMENCO. 

![bitmap - obrázek](3d.jpg "EDIT|UPLOAD")

![bitmap - video](3d.mp4 "EDIT|UPLOAD")

Zajišťuje nejenom samotné renderování 2D obrazu, ale také renderování příslušné hloubkové mapy. Oba snímky jsou následně připojené k danému headeru, který má zakódované specifikace pro 3D displej značky DIMENCO.

## Uživatelská dokumentace

Plugin je napsaný v jazyce Python a je určený pro aplikaci Blender. 

### Použití:
1. Otevřete Blender a přejděte do Edit > Preferences > Add-ons.
2. Nainstalujte plugin a poté jej aktivujte zaškrtnutím políčka.
3. Spusťte plugin pomocí tlačítka Render > Render 2D Plus Depth Stereo.
4. Vyberte adresář a název pro výsledný snímek a následně stiskněte pro potvrzení tlačítko "Render 2D Plus Depth Stereo".
5. Chvíli počkejte. Pokud máte složitější objekt k renderování může tato operace trvat déle.
6. Výsledek máte uložený v zadaném adresáři.

## Teoretická dokumentace

Autostereoskopické displeje umožňují uživateli vnímat 3D obraz bez potřeby speciálních brýlí. 

### Princip

![image.png](./image.png)

Základem této technologie je speciální maska umístěná před LCD panelem, která je vybavena optickými hranoly. Tyto hranoly vychylují světlo do různých směrů tak, aby každé oko vidělo jinou část obrazu (levé oko vidí pouze obraz určený pro levé oko a pravé oko vidí obraz určený pro pravé oko). Dále v závislosti na pozici uživatele vůči displeji se mění úhel zobrazení jednotlivých objektů, což přispívá ke vnímání obrazu ve 3D.


### Proces načtení obrazu

#### Formát obrazu
Pro správné zobrazení na autostereoskopických displejích se používá formát kombinující:

1. **2D obraz:** Vyrenderovaný barevný obraz z dané perspektivy.
2. **Hloubkovou mapa:** Černobílá mapa, kde světlé oblasti reprezentují objekty blíž k uživateli a tmavé oblasti ty dál od uživatele.
3. **Header:** V obrazu zakódovaná metadata (s rozlišením 3840x1), která obsahují informace o rozlišení a dalších parametrech potřebných pro správné načtení obrazu pro televize DIMENCO.

**Načtení dat:** Televize přečte 2D obraz, hloubkovou mapu a metadata z headeru.

**Interpolace:** Provede se interpolace pixelů na základě dat získaných z hloubky. To znamená, že pixel, který je blíž k uživateli, se v rámci dané perspektivy posune víc než pixel, který je umístěný dál od uživatele.

**Výpočet paralaxy:** Pro každou perspektivu se vypočítá paralaxa (rozdíl v zobrazení objektů způsobený jejich odlišnou hloubkou).

**Generování obrazu:** Na základě paralaxy vzniká několik pohledů, které simulují různé úhly pohledu uživatele.

**Projekce přes masku:** Maska zajistí, že každý obraz bude směrován do konkrétního úhlu, tak aby levé oko vidělo jinou perspektivu než pravé.

### Proces generování hloubkové mapy
1. **Vykreslení scény:** Kamera vyrenderuje scénu z dané perspektivy.
2. **Záznam vzdáleností:** Pro každý pixel je spočítána vzdálenost objektu od kamery.
3. **Normalizace a inverze obrazu:** Hodnoty v obraze jsou normalizovány do rozsahu 0–255 a následně převrácené tak, aby:
   - 0 odpovídala nejvzdálenějšímu bodu.
   - 255 odpovídala nejbližšímu bodu.

## Programátorská dokumentace

Plugin je napsaný v jazyce Python a využívá následující knihovny:
  - `bpy`: Pro přístup k Blender Python API.
  - `os`: Pro práci se souborovým systémem.
  - `Pillow`: Pro práci s obrázky.
  - `tempfile`: Pro ukládání vyrenderovaných obrázků v dočasném adresáři.

### Průběh pluginu

**1. Aktivace pluginu**
  - Uživatel aktivuje plugin prostřednictvím menu: Render > 2D Plus Depth Stereo Renderer.
  - Zavolá se metoda `execute()`.

**2. Výběr cesty pro uložení výsledného souboru**
  - Plugin vyzve uživatele k výběru adresáře a názvu pro uložení výsledného obrázku.
  
  - **Uživatel zvolí cestu a název souboru:**
    - Pokud soubor již existuje, zobrazí se chybová hláška: "File name already exists." a plugin se ukončí.
    - Pokud název souboru končí příponou `.bmp`, přípona je odstraněna.
    - Program si uloží výslednou cestu, název souboru a spouští renderování výsledného obrázku voláním metody `render_stereo_2d_plus_depth(context)`.

  - **Uživatel nezvolí soubor:**
    - Plugin se ukončí.
    
**3. Příprava prostředí Blenderu**
    - Zavolá se metoda `setup_blender_env(context)`, kde se rozlišení renderovaného obrazu nastaví na 1920x2160.

**4. Renderování 2D obrazu**
  - Plugin použije metodu `render_2d_image(context, tmp_path)` k renderování 2D barevného obrázku a uloží ho do dočasného adresáře ve formátu `.bmp`.

**5. Renderování hloubkové mapy**
  - Plugin použije metodu `render_depth_image(context, tmp_path)` k renderování hloubkové mapy.
  - Metoda `setup_blender_for_depth(context)` nastaví požadované parametry pro renderování hloubkové mapy:
    - Černobílý režim barvy a 8-bitová hloubka barev.
    - Aktivuje pouze hloubkový (Z) pass v rámci view layeru k renderování pouze hloubky obrazu.
  - Využijí se Compositing nodes pro normalizaci a inverzi obrazu.
  - Výsledek je uložen jako hloubkový obrázek do dočasného adresáře ve formátu `.bmp`.
  
**6. Sestavení výsledného obrázku**
  - Po renderování 2D a hloubkového obrazu se volá metoda `render_combined_image(tmp_path, header_path)`, která:
    - Načte 2D obraz, hloubkový obraz a hlavičkový obraz.
    - Kombinuje je do jednoho souboru, kde je 2D obraz vpravo, hloubková mapa vlevo a hlavička je vepsaná na první řádce obrazu.
  - Výsledek je uložen do cílového souboru ve formátu `.bmp`.

**7. Informování uživatele**
  - Po dokončení renderování se plugin ukončí s informací, že obrázek byl úspěšně vygenerován a uložen na vybranou cestu: "Rendered image saved at {filepath}.bmp".

## Zdroje
- **Článek o autostereoskopických displejích (https://cs.gali-3d.com/autostereoskopie-3d/):** Poskytnul základní informace o principu autostereoskopických displejích a také názorný obrázek.
- **Dokumentace Blender Python API:** Poskytla základní informace o rozhraní pro vývoj pluginů pro Blender.
- **DIMENCO specifikace Displeje:** Technické specifikace pro formát 2D-plus-Depth.
- **Dotazování ChatGPT:** Použito hlavně k doplňkovým dotazům ohledně dokumentace Blender Python API a dovysvětlení teorie za projekcí obrazu na autostereoskopických dispejích.
