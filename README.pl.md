# Modele integracji cywilno-wojskowej ratownictwa lotniczego

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20734497.svg)](https://doi.org/10.5281/zenodo.20734497)

**Wersja 2.0.0**

Uzupełnienie obliczeniowe do pracy:

> Kasperek, M. M. (2026). *A Public–Private Mobilisation Reserve for Air Medical
> Evacuation: Institutional Design and Economic Appraisal.*

Autor: **Maciej M. Kasperek**, ORCID [0009-0008-7419-0851](https://orcid.org/0009-0008-7419-0851).

Kod na licencji Apache 2.0 (`LICENSE.md`).
Dane granic pochodzą z **geoBoundaries** (<https://www.geoboundaries.org>) i są
wykorzystywane na licencji CC BY 4.0. Szczegóły w `NOTICE.md`.

Paczka odtwarza ze źródeł każdą liczbę, tabelę i figurę z artykułu.

Angielska wersja tego pliku znajduje się w `README.md`.

## Zawartość

- `economic_model.py` — model finansowy i fiskalny (hipotezy H1 i H2). Uruchomienie `python economic_model.py` wypisuje wyniki scenariusza bazowego.
- `reserve_placement.py` — model przestrzenny zasięgu i dostępności (hipoteza H3). Uruchomienie `python reserve_placement.py` wypisuje lokalizację baz i pokrycie.
- `figure_zones.py` — generuje Figurę 1, macierz opłacalności (`figure_zones.png`).
- `figure_a2_1.py` — generuje Figurę 2, mapę zasięgu dwufilarowego (`figure_A2_1.png`).
- `tables.py` — generuje z modeli wszystkie tabele liczbowe (`tables.md`).
- `poland_boundary.geojson`, `poland_voivodeships.geojson` — granica państwa (ADM0) i granice województw (ADM1) z otwartej bazy geoBoundaries, rozpowszechniane bez zmian na licencji CC BY 4.0. Szczegóły w `NOTICE.md`.
- `tests/` — 37 testów jednostkowych zamrażających każdą kluczową liczbę.
- `requirements.txt` — zależności Pythona.
- `LICENSE.md`, `NOTICE.md` — licencja kodu oraz atrybucja rozpowszechnianych danych granic.
- `.gitattributes` — utrzymuje stałe końce linii, dzięki czemu sumy kontrolne z `MD5SUMS.txt` zgadzają się na każdej platformie.
- `.gitignore` — trzyma lokalne katalogi podręczne (`__pycache__`, `.pytest_cache`) i pliki generowane poza repozytorium.

## Jak odtworzyć wyniki

    pip install -r requirements.txt
    python -m pytest -q          # 37 testów, wszystkie kluczowe liczby
    python economic_model.py     # wyniki ekonomiczne scenariusza bazowego
    python reserve_placement.py  # wyniki pokrycia przestrzennego
    python figure_zones.py       # Figura 1
    python figure_a2_1.py        # Figura 2
    python tables.py             # wszystkie tabele

## Kluczowe wyniki scenariusza bazowego

- Wartość bieżąca netto dla partnera prywatnego +7, wewnętrzna stopa zwrotu 10,5 procent, opłata progowa 63 (H2).
- Koszt publiczny w ujęciu całego systemu: 601 zasobowo, 481 budżetowo, 399 ekonomicznie, wobec 681 przy własności publicznej i od 682 do 768 przy kontrakcie dostępności; oszczędności 80 oraz 282 (H1).
- Wartość końcowa spółki 582 (udział państwa 297, udział prywatny 285), jedno źródło prawdy.
- Pokrycie w 45 minut jest dokładnie liniowe względem dostępności filaru wojskowego, 90,5 procent plus 4,5 punktu na jednostkę dostępności (H3).

Wszystkie kwoty w milionach złotych, w cenach stałych 2026.

## Jak cytować

Przy korzystaniu z tego oprogramowania prosimy o cytowanie zarówno pracy, jak i oprogramowania.

Praca:
> Kasperek, M. M. (2026). A Public–Private Mobilisation Reserve for Air Medical
> Evacuation: Institutional Design and Economic Appraisal.

Oprogramowanie:
> Kasperek, M. M. (2026). *Air-rescue civil-military integration models*
> (wersja 2.0.0) [Oprogramowanie]. Zenodo. https://doi.org/10.5281/zenodo.21632716

## Autor

Maciej M. Kasperek. ORCID 0009-0008-7419-0851.

## Czego tu nie ma

Źródło manuskryptu celowo nie zostało dołączone. Repozytorium zawiera modele,
dane oraz skrypty odtwarzające każdą tabelę i figurę, czyli to, czego wymaga
reprodukcja wyników.
