# 2D-plus-Depth Stereometrické Renderování pro Blender

Tento plugin byl navržen pro aplikaci Blender a umožňuje renderovat libovolný model pro vícepohledovou 3D auto-stereoskopickou obrazovku. Zajišťuje nejenom samotné renderování 2D obrazu, ale také generování příslušné hloubkové mapy. Hloubková mapa je automaticky kombinována s obrazem a specifickým headerem pro vytvoření výsledného souboru vhodného pro 3D displeje značky DIMENCO.

## Uživatelská dokumentace

Plugin je napsaný v jazyce Python a je určený pro aplikaci Blender. 

### Použití:
1. Otevřete Blender a přejděte do Edit > Preferences > Add-ons.
2. Nainstalujte plugin a poté jej aktivujte zaškrtnutím políčka.
3. Spusťte plugin pomocí tlačítka Render > Render 2D Plus Depth Stereo.
4. Vyberte adresář a název pro výsledný render a následně stiskněte pro potvrzení tlačítko "Render 2D Plus Depth Stereo".
5. Chvíli počkejte. Pokud máte složitější objekt k renderování může tato operace trvat déle.
6. Výsledek máte uložený v zadaném adresáři.

## Programátorská dokumentace

Plugin je napsaný v jazyce Python a využívá následující knihovny:
  - `bpy`: Pro přístup k Blender Python API.
  - `os`: Pro práci se souborovým systémem.
  - `Pillow`: Pro práci s obrázky.
  - `tempfile`: Pro ukládání vyrenderovaných obrázků v dočasném adresáři.

### Průběh pluginu

**1. Aktivace pluginu**
  - Uživatel aktivuje plugin prostřednictvím menu: **Render -> 2D Plus Depth Stereo Renderer**.
  - Zavolá se metoda `execute()`, která řídí hlavní logiku pluginu.

**2. Výběr cesty pro uložení výsledného souboru**
  - Plugin vyzve uživatele k výběru adresáře a názvu pro uložení výsledného obrázku.
  
  - **Uživatel zvolí cestu a název souboru:**
    - Pokud soubor již existuje, zobrazí se chybová hláška: "File name already exists." a plugin se ukončí.
    - Pokud název souboru končí příponou `.bmp`, přípona je odstraněna.
    - Program si uloží výslednou cestu, název souboru a spouští renderování výsledného obrázku.

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
- **Dokumentace Blender Python API:** Poskytla základní informace o rozhraní pro vývoj pluginů pro Blender.
- **DIMENCO specifikace Displeje:** Technické specifikace pro formát 2D-plus-Depth.
- **Dotazování ChatGPT:** Použito hlavně k doplňkovým dotazům ohledně dokumentace Blender Python API.

