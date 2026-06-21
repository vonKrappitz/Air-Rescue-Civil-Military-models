# Modele integracji cywilno-wojskowej ratownictwa lotniczego

Suplement obliczeniowy do pracy.

> M. M. Kasperek (2026). *Civil-military integration of a reformed national
> air-rescue network.* (preprint).

Repozytorium zawiera dwa deterministyczne modele, które regenerują ryciny pracy.
Ich uruchomienie odtwarza każdy wynik liczbowy z Appendiksu 1 i Appendiksu 2 co
do jednostki. Jedyny wyjątek, opisany niżej, dotyczy minut rozmieszczenia.

Wersja angielska tego pliku znajduje się w `README.md`.

## Zawartość

| Plik | Odtwarza | Co robi |
| --- | --- | --- |
| `economic_model.py` | Tabele 2 i 3 (Appendix 1) | Dziesięcioletnia symulacja spółki LEM-PPP, wartość bieżąca netto, scenariusz optymistyczny oraz wrażliwość bilansu inwestycyjnego netto na stopę dyskonta. |
| `reserve_placement.py` | Appendix 2 | Rozmieszczenie czterech cywilnych AW101 metodą p-środka, przez wyczerpującą enumerację wszystkich 35 kombinacji siedmiu Centrów Regionalnych, plus wariant dwufilarowy dodający bazę marynarki w Darłowie. |
| `poland_boundary.geojson` | Appendix 2 | Kontur kraju (ADM0) Polski z geoBoundaries, siatka lądowa rozmieszczenia jest z niego budowana. |
| `poland_voivodeships.geojson` | Figura A2.1 | Granice województw (ADM1) z geoBoundaries, rysowane na mapie dla orientacji. |
| `figure_a2_1.py` | Figura A2.1 | Rysuje mapę reach układu dwufilarowego, pięć baz i dwa południowe występy rezydualne. Wymaga matplotlib i numpy. |
| `tests/` | oba | Dziewiętnaście testów jednostkowych, które sprawdzają odtworzone liczby względem pracy. |

## Wymagania

Python 3.8 lub nowszy. Oba modele korzystają wyłącznie z biblioteki standardowej,
więc nie mają zależności wykonawczych. Zestaw testów używa `pytest`.

```bash
pip install -r requirements.txt   # potrzebne tylko do testów
```

## Uruchamianie modeli

```bash
python economic_model.py
python reserve_placement.py
```

`economic_model.py` wypisuje Tabelę 2, czyli symulację spółki z przepływami
realnymi i nominalnymi, wartość bieżącą netto, wartość optymistyczną oraz
korzyść dla skarbu państwa. Wypisuje też Tabelę 3, czyli wrażliwość bilansu
inwestycyjnego netto przy 3, 4 i 5 procent. Każda liczba zgadza się z pracą.

`reserve_placement.py` wypisuje optimum jednofilarowe, Kraków, Lublin, Poznań i
Olsztyn, jego najgorszy przypadek dotarcia, odniesienie do konwencjonalnego
zestawu czterech miast oraz najgorszy przypadek dwufilarowy po dodaniu bazy w
Darłowie. Podaje także czas dotarcia do nazwanych punktów odniesienia na
wybrzeżu Bałtyku i na południowych występach górskich.

## Uruchamianie testów

```bash
python -m pytest tests/ -v
```

## Generowanie Figury A2.1

```bash
python figure_a2_1.py
```

Zapisuje `figure_A2_1.png`, mapę reach układu dwufilarowego. Koloruje każdy punkt
lądu czasem dotarcia do najbliższej bazy, zaznacza pięć baz i krzyżuje dwa
południowe występy rezydualne koło Kłodzka i w Bieszczadach, oba około 57 minut.
Skrypt wymaga matplotlib i numpy.

## Granica i zgodność figur

Rozmieszczenie działa na `poland_boundary.geojson`, konturze kraju (ADM0) Polski
z otwartej bazy geoBoundaries. Z tą granicą model odtwarza pracę. Optimum to
Kraków, Lublin, Poznań i Olsztyn. Najgorszy przypadek jednofilarowy wynosi 58,6
minuty, na środkowym wybrzeżu Bałtyku koło Rowów, wobec 69,8 dla konwencjonalnego
zestawu czterech miast. Baza marynarki w Darłowie leży na tym samym środkowym
pasie wybrzeża, więc jej dodanie sprowadza środkowe wybrzeże do około 15 minut, a
róg północno-zachodni do około 37. Ogólnokrajowy najgorszy przypadek dwufilarowy
to 57,3 minuty, na południowych występach górskich, Kłodzko na południowym
zachodzie i Bieszczady na południowym wschodzie, niemal remis. Model ekonomiczny
jest ścisły co do jednostki. Przy oczku pięciu kilometrów najgorszy przypadek
jednofilarowy mieści się między 58 a 59 minut zależnie od próbkowanej komórki
wybrzeża. Podstawienie innej granicy kraju w `poland_boundary.geojson` nie
zmienia niczego w algorytmie.

## Metoda w skrócie

Rozmieszczenie idzie regułą p-środka. Dla każdej kombinacji czterech z siedmiu
Centrów Regionalnych model liczy najgorszy przypadek dotarcia po siatce lądowej
o oczku pięciu kilometrów. Dotarcie to odległość po kole wielkim podzielona
przez prędkość przelotową 278 km/h plus pięć minut na rozruch. Kombinacja o
najmniejszym najgorszym przypadku jest globalnym optimum, znalezionym przez
enumerację, nie heurystykę.

Model ekonomiczny wycenia spółkę jako podmiot finansowy w dziesięcioletnim
oknie. Liczy wynik netto, wolny przepływ pieniężny doliczający amortyzację i
odejmujący nakłady odtworzeniowe oraz końcową wartość rezydualną. Spółkę
dyskontuje stopą realną 4 procent, bilans publiczny stopą społeczną 3 procent.
Wariant nominalny narosły celem inflacyjnym 2,5 procent i dyskontowany
odpowiadającą stopą nominalną daje tę samą wartość bieżącą, przez relację
Fishera.

## Dane granicy

`poland_boundary.geojson` (ADM0) i `poland_voivodeships.geojson` (ADM1) to
kontury Polski z geoBoundaries, wydanie gbOpen. geoBoundaries rozpowszechniany
jest na licencji CC BY 4.0, osobno od kodu na licencji Apache. Zachowaj tę
atrybucję przy redystrybucji plików.

> Runfola, D., i in. (2020). geoBoundaries, a global database of political
> administrative boundaries. *PLoS ONE* 15(4), e0231866.
> https://www.geoboundaries.org

## Jak cytować

Jeśli korzystasz z tego oprogramowania, cytuj pracę i rekord oprogramowania.

Praca.

> Kasperek, M. M. (2026). Civil-military integration of a reformed national
> air-rescue network. (preprint).

Oprogramowanie.

> Kasperek, M. M. (2026). *Air-rescue civil-military integration models*
> (wersja 1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.20734498

## Autor

Maciej M. Kasperek. ORCID 0009-0008-7419-0851.

## Licencja

Apache License 2.0. Zobacz pliki `LICENSE` i `NOTICE`.
