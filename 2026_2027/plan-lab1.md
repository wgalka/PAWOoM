# Plan LAB1 — pierwsza mikrousługa w Pythonie

## Temat

**System paczkomatów — `Locker Service`**

Pierwsze laboratorium prowadzi studentów od opisu problemu biznesowego do uruchomienia prostej mikrousługi HTTP. Usługa będzie odpowiedzialna za paczkomaty i ich skrytki.

---

## 1. Zgodność z sylabusem

Laboratorium realizuje pierwszy punkt ćwiczeń laboratoryjnych:

> Tworzenie podstawowej mikrousługi: definiowanie API, porty, przechowywanie danych.

Podczas zajęć student:

- utworzy osobną aplikację webową,
- zdefiniuje odpowiedzialność jednej mikrousługi,
- zaprojektuje kontrakt HTTP/REST,
- uruchomi usługę na własnym porcie,
- zaimplementuje podstawowe endpointy,
- przechowa i zmodyfikuje dane,
- obsłuży podstawowe błędy,
- przetestuje API.

W pierwszym laboratorium nie wdrażamy jeszcze Eureki, API Gateway, RabbitMQ ani Dockera. Te elementy pojawią się później, gdy podstawowa usługa będzie już działała samodzielnie.

---

## 2. Cel dydaktyczny

Po wykonaniu ćwiczenia student powinien rozumieć:

- czym różni się mikrousługa od zwykłego modułu programu,
- dlaczego usługa ma jedną określoną odpowiedzialność,
- czym jest kontrakt API,
- dlaczego usługa działa na własnym porcie,
- jak obsługiwać dane wejściowe i błędy,
- jak sprawdzić działanie usługi z poziomu klienta HTTP.

### Zasada prowadzenia laboratorium

Laboratorium nie powinno polegać na przepisaniu kompletnego kodu z prezentacji. Kod prowadzącego ma być krótkim przykładem startowym, a główna implementacja powinna powstać jako seria decyzji i zadań wykonywanych przez studentów.

Student powinien umieć odpowiedzieć:

- dlaczego dana usługa ma właśnie taką odpowiedzialność,
- dlaczego endpoint ma określoną metodę i ścieżkę,
- dlaczego dane mają określony kształt,
- dlaczego zwracany jest konkretny kod HTTP,
- co stanie się w przypadku błędu,
- jak sprawdzono poprawność implementacji.

---

## 2.1. Model pracy: przykład, decyzja, implementacja, weryfikacja

Każdy większy etap powinien mieć cztery części:

1. **Przykład prowadzącego** — maksymalnie mały fragment pokazujący mechanizm.
2. **Decyzja studenta** — student sam uzupełnia kontrakt, model albo regułę.
3. **Implementacja** — student pisze kod lub modyfikuje kod startowy.
4. **Weryfikacja** — student wykonuje testy i wyjaśnia wynik.

Przykład:

```text
Prowadzący pokazuje GET /health
Student projektuje GET /lockers
Student implementuje endpoint
Student testuje przypadek poprawny i błędny
```

---

## 2.2. Korzystanie z AI

Korzystanie z AI jest dozwolone i może być elementem pracy programisty. Nie zwalnia jednak z odpowiedzialności za rozwiązanie.

Student może używać AI do:

- wyjaśnienia błędu,
- zaproponowania kilku wariantów API,
- wygenerowania szkieletu kodu,
- przygotowania przykładowych testów,
- znalezienia dokumentacji,
- refaktoryzacji kodu.

Student powinien:

- zweryfikować wygenerowany kod,
- uruchomić go lokalnie,
- napisać lub uruchomić testy,
- rozumieć każdą istotną część rozwiązania,
- umieć wyjaśnić decyzje podczas krótkiej rozmowy z prowadzącym.

Nie zalicza się rozwiązania, którego student nie potrafi uruchomić, przetestować albo wyjaśnić.

### Minimalna informacja o użyciu AI

W README student dopisuje krótką sekcję:

```text
AI usage:
- narzędzie: ...
- wykorzystano do: ...
- samodzielnie zweryfikowano przez: ...
```

Nie chodzi o karanie za użycie AI, tylko o wymuszenie świadomej weryfikacji rezultatu.

---

## 3. Rekomendowany stos technologiczny

### Wersja podstawowa

- Python 3.12 lub nowszy,
- FastAPI,
- Uvicorn,
- Pydantic,
- dane przechowywane w pamięci procesu,
- Swagger/OpenAPI generowany automatycznie przez FastAPI.

### Wersja późniejsza

W kolejnych laboratoriach można dodać:

- PostgreSQL,
- SQLAlchemy,
- Alembic,
- Redis,
- RabbitMQ,
- Docker Compose,
- Eureka lub inne service discovery.

---

## 4. Przykład domeny

System paczkomatów składa się docelowo z kilku obszarów:

```text
Locker Service        — paczkomaty i skrytki
Parcel Service        — paczki i ich statusy
Tracking Service      — historia zdarzeń
Notification Service  — powiadomienia
Delivery Service      — transport i dostawy
```

W LAB1 implementujemy tylko:

```text
Locker Service
```

### Odpowiedzialność `Locker Service`

Usługa:

- przechowuje listę paczkomatów,
- przechowuje listę skrytek,
- informuje o statusie skrytki,
- pozwala dodać paczkomat,
- pozwala zmienić status skrytki.

Usługa nie zajmuje się:

- użytkownikami,
- płatnościami,
- historią przesyłek,
- wysyłaniem SMS-ów,
- dostarczaniem paczek.

To ograniczenie jest ważną częścią ćwiczenia z wyznaczania granic mikrousługi.

`Locker Service` jest jednak tylko krótkim przykładem wspólnym. Główne zadanie LAB1 polega na samodzielnym wymyśleniu tematu i utworzeniu własnej mikrousługi.

### Obowiązkowe zadanie własne

Po przeanalizowaniu przykładu paczkomatów każdy student lub para:

1. wybiera własny prosty problem,
2. nazywa własną usługę,
3. określa jej odpowiedzialność,
4. projektuje własny model danych i API,
5. implementuje usługę w Pythonie/FastAPI,
6. przygotowuje testy i dokumentację.

Przykładowe tematy:

- rezerwacja sal,
- biblioteka,
- plan zajęć,
- zgłoszenia IT,
- wypożyczalnia rowerów,
- wydarzenia i bilety,
- platforma gier,
- inteligentny budynek.

Student może zaproponować własny temat, ale musi umieć wyjaśnić go w kilku zdaniach.

### Warunki akceptacji własnej usługi

- aplikacja uruchamia się na własnym porcie,
- działa endpoint zdrowia usługi,
- działa minimum jeden endpoint odczytu,
- działa minimum jeden endpoint modyfikacji,
- dane wejściowe są walidowane,
- obsłużone są minimum trzy przypadki błędne,
- API można przetestować bez zaglądania do kodu,
- student potrafi wyjaśnić, dlaczego usługa ma właśnie taki zakres.

---

## 5. Model danych

### Paczkomat

```text
id          — identyfikator paczkomatu
name        — nazwa lub kod paczkomatu
address     — adres
city        — miasto
status      — online albo offline
```

### Skrytka

```text
id          — identyfikator skrytki
locker_id   — identyfikator paczkomatu
size        — S, M albo L
status      — free, reserved, occupied albo out_of_service
```

### Przykładowe dane

```json
{
  "id": "KRK-1024",
  "name": "Kraków Galeria",
  "address": "ul. Długa 10",
  "city": "Kraków",
  "status": "online"
}
```

---

## 6. Projekt API

### Paczkomaty

| Metoda | Endpoint | Opis | Sukces |
|---|---|---|---:|
| GET | `/lockers` | Pobiera listę paczkomatów | 200 |
| GET | `/lockers/{locker_id}` | Pobiera jeden paczkomat | 200 |
| POST | `/lockers` | Dodaje paczkomat | 201 |
| DELETE | `/lockers/{locker_id}` | Usuwa paczkomat | 204 |

### Skrytki

| Metoda | Endpoint | Opis | Sukces |
|---|---|---|---:|
| GET | `/lockers/{locker_id}/compartments` | Pobiera skrytki paczkomatu | 200 |
| POST | `/lockers/{locker_id}/compartments` | Dodaje skrytkę | 201 |
| PATCH | `/compartments/{compartment_id}/status` | Zmienia status skrytki | 200 |

### Minimalny zakres implementacji

Na zajęciach obowiązkowe są:

- `GET /lockers`,
- `GET /lockers/{locker_id}`,
- `POST /lockers`,
- `GET /lockers/{locker_id}/compartments`,
- `PATCH /compartments/{compartment_id}/status`.

Pozostałe endpointy mogą być wykonane jako rozszerzenie.

---

## 7. Plan realizacji krok po kroku

Każdy krok zawiera część pokazową i część samodzielną. Prowadzący nie powinien udostępniać kompletnego rozwiązania przed zakończeniem pracy studentów.

### Krok 0 — przygotowanie środowiska

Sprawdzić:

- wersję Pythona,
- działanie terminala,
- działanie edytora kodu,
- utworzenie katalogu projektu,
- utworzenie i aktywację środowiska wirtualnego.

Rezultat: pusty projekt Python gotowy do instalacji zależności.

### Krok 1 — instalacja FastAPI i uruchomienie aplikacji

Student:

- instaluje FastAPI i Uvicorn,
- tworzy plik aplikacji,
- definiuje obiekt aplikacji,
- uruchamia serwer na porcie `8000`.

Rezultat:

- działa adres `http://localhost:8000`,
- działa dokumentacja `http://localhost:8000/docs`.

**Samodzielne zadanie:** student sam wybiera nazwę projektu i port z przedziału ustalonego przez prowadzącego, np. `8101–8199`. Dzięki temu każdy może uruchomić własną usługę bez konfliktu portów.

### Krok 2 — pierwszy endpoint kontrolny

Student dodaje endpoint:

```http
GET /health
```

Odpowiedź:

```json
{
  "status": "ok",
  "service": "locker-service"
}
```

Cel: sprawdzenie, czy usługa działa niezależnie od właściwego modelu domenowego.

**Samodzielne zadanie:** student ma samodzielnie zaprojektować odpowiedź dla endpointu `/health`, tak aby zawierała nazwę usługi i jej wersję. Następnie powinien uzasadnić, dlaczego health check nie powinien zwracać całej zawartości bazy danych.

### Krok 3 — model danych i dane początkowe

Student:

- definiuje model paczkomatu,
- definiuje model skrytki,
- dodaje kilka danych początkowych,
- przechowuje dane w strukturze pamięciowej.

Na tym etapie należy wyjaśnić, że dane znikną po restarcie procesu. Jest to świadome uproszczenie pierwszego laboratorium.

**Samodzielne zadanie:** student wybiera, czy model skrytki będzie osobnym obiektem, czy częścią modelu paczkomatu. Musi zapisać decyzję i jej uzasadnienie. Prowadzący może zaakceptować oba warianty, jeśli są konsekwentnie zaimplementowane.

### Krok 4 — odczyt danych

Student implementuje:

```http
GET /lockers
GET /lockers/{locker_id}
GET /lockers/{locker_id}/compartments
```

Należy pokazać różnicę między:

- listą zasobów,
- pobraniem konkretnego zasobu,
- zasobem zagnieżdżonym.

**Samodzielne zadanie:** student projektuje własny format odpowiedzi dla listy i pojedynczego paczkomatu. Następnie sprawdza, czy API zachowuje spójność nazw pól i typów danych.

### Krok 5 — walidacja danych wejściowych

Student definiuje model żądania dla `POST /lockers`.

Sprawdza między innymi:

- czy wymagane pola są obecne,
- czy status ma dozwoloną wartość,
- czy identyfikator nie jest pusty,
- czy nie ma drugiego paczkomatu o tym samym identyfikatorze.

**Samodzielne zadanie:** student otrzymuje listę przypadków granicznych i sam wybiera sposób ich obsługi. Nie dostaje gotowych modeli walidacji.

### Krok 6 — modyfikacja stanu

Student implementuje zmianę statusu skrytki:

```http
PATCH /compartments/{compartment_id}/status
```

Przykładowe żądanie:

```json
{
  "status": "occupied"
}
```

Należy omówić, kto może zmieniać status i jakie przejścia są dozwolone.

**Samodzielne zadanie:** student definiuje dozwolone przejścia statusów, np. `free → reserved → occupied → free`, oraz przygotowuje przypadek, w którym przejście powinno zostać odrzucone.

### Krok 7 — obsługa błędów

Student obsługuje co najmniej:

- nieistniejący paczkomat — `404 Not Found`,
- nieistniejącą skrytkę — `404 Not Found`,
- duplikat identyfikatora — `409 Conflict`,
- niepoprawny status — `422 Unprocessable Entity` albo `400 Bad Request`.

**Samodzielne zadanie:** student tworzy tabelę błędów API zawierającą: warunek, kod HTTP, treść odpowiedzi i sposób testowania.

### Krok 8 — testowanie API

Student testuje API w Swaggerze, Postmanie albo przy użyciu `curl`.

Testy obejmują:

1. sprawdzenie `/health`,
2. pobranie listy paczkomatów,
3. pobranie istniejącego paczkomatu,
4. pobranie nieistniejącego paczkomatu,
5. dodanie paczkomatu,
6. pobranie jego skrytek,
7. zmianę statusu skrytki,
8. próbę wysłania niepoprawnych danych.

**Wymaganie jakościowe:** student nie oddaje wyłącznie zrzutu ekranu ze Swaggera. Powinien mieć powtarzalny zestaw przypadków testowych oraz umieć wskazać, jaki błąd wykrywa każdy test.

### Krok 9 — implementacja własnego tematu

Po krótkim przykładzie `Locker Service` student nie kopiuje jego modelu ani endpointów. Tworzy własny katalog projektu, własną nazwę usługi, własny model danych i własny kontrakt API.

Prowadzący może udostępnić wspólny szkielet techniczny, ale nie powinien narzucać studentom gotowego modelu domenowego.

Student przygotowuje kolejno:

1. jednozdaniowy opis problemu,
2. listę odpowiedzialności usługi,
3. listę danych,
4. propozycję endpointów,
5. listę błędów,
6. implementację,
7. testy i dokumentację.

### Krok 10 — dokumentacja i porządkowanie kodu

Student przygotowuje:

- instrukcję uruchomienia,
- opis endpointów,
- przykładowe żądania i odpowiedzi,
- opis struktury katalogów,
- listę znanych ograniczeń.

Dokumentacja powinna zawierać również krótką sekcję:

- jakie decyzje projektowe podjęto,
- jakie alternatywy rozważono,
- z czego student skorzystał podczas pracy,
- jak zweryfikowano kod wygenerowany lub konsultowany z AI.

---

## 7.1. Zadania celowo niekompletne

W materiałach dla studentów warto pozostawić kilka elementów do samodzielnego zaprojektowania:

- nazwy pól modelu,
- format odpowiedzi listy,
- statusy skrytek,
- dozwolone przejścia statusów,
- kod błędu dla konfliktu,
- sposób podziału plików,
- zestaw testów.

Nie należy pozostawiać niejasnego celu. Student ma mieć jasno określony problem i warunki akceptacji, ale niekoniecznie jedną z góry ustaloną implementację.

---

## 7.2. Punkty kontrolne podczas zajęć

Prowadzący może zatrzymać pracę po każdym punkcie kontrolnym:

### Checkpoint A — API

Student potrafi pokazać i wyjaśnić endpointy.

### Checkpoint B — model danych

Student potrafi uzasadnić podział paczkomatu i skrytek.

### Checkpoint C — błędy

Student potrafi pokazać działający przypadek `404` i przypadek błędnych danych.

### Checkpoint D — testy

Student potrafi uruchomić test i wyjaśnić, co on sprawdza.

### Checkpoint E — rozmowa techniczna

Student odpowiada na dwa lub trzy pytania dotyczące własnego kodu. Pytania mogą być generowane losowo na podstawie implementacji.

---

## 8. Proponowana struktura projektu

W planowanej implementacji można rozpocząć od prostego układu:

```text
locker-service/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── storage.py
│   └── routes/
│       ├── lockers.py
│       └── compartments.py
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
```

Struktura może początkowo być prostsza. Ważne jest stopniowe oddzielenie:

- modeli domenowych,
- modeli wejścia i wyjścia API,
- przechowywania danych,
- routingu HTTP.

---

## 9. Zakres kodu do przygotowania w następnym kroku

Implementacja powinna zawierać przykłady pokazujące:

1. utworzenie aplikacji FastAPI,
2. uruchomienie Uvicorna,
3. model Pydantic,
4. dane w pamięci,
5. endpointy `GET`, `POST` i `PATCH`,
6. parametry ścieżki,
7. walidację żądania,
8. kody błędów HTTP,
9. testowanie w Swaggerze i przez `curl`.

Nie należy jeszcze dodawać RabbitMQ, Eureki, API Gateway ani bazy PostgreSQL do pierwszego przykładu kodu. Najpierw student powinien zrozumieć pojedynczą działającą usługę.

---

## 10. Porównanie architektur — obowiązkowe podsumowanie

Na zakończenie student przygotowuje krótkie porównanie własnej usługi z innymi sposobami organizacji tego samego systemu.

| Pytanie | Monolit | Mikrousługi | Modularny monolit |
|---|---|---|---|
| Czy wszystkie funkcje są wdrażane razem? | Tak | Nie musi | Zwykle tak |
| Czy moduły komunikują się przez sieć? | Zwykle nie | Tak | Zwykle nie |
| Czy każda część może mieć osobny proces? | Zwykle nie | Tak | Niekoniecznie |
| Czy awaria procesu może objąć cały system? | Często tak | Zwykle ogranicza się do usługi | Tak, zależnie od wdrożenia |
| Czy dane mogą być rozdzielone między usługi? | Często wspólne | Zwykle rozdzielone | Mogą być logicznie rozdzielone |
| Czy wdrożenie jest niezależne? | Zwykle nie | Tak | Zwykle nie |

Student odpowiada własnymi słowami:

1. Dlaczego moja usługa może być mikroserwisem?
2. Dlaczego nie jest tylko klasą albo modułem?
3. Jak wyglądałaby moja aplikacja jako monolit?
4. Co zmieniłoby się po podzieleniu jej na mikroserwisy?
5. Jakie byłyby koszty takiego podziału?
6. Czy w moim przypadku mikroserwisy są rzeczywiście uzasadnione?

Nie wymagamy odpowiedzi, że mikroserwisy zawsze są najlepsze. Poprawną odpowiedzią może być również stwierdzenie, że dla małego systemu lepszy byłby monolit lub modularny monolit.

## 11. Zadania rozszerzające

Po wykonaniu minimum student może:

- dodać `DELETE /lockers/{locker_id}`,
- dodać wyszukiwanie po mieście,
- dodać filtrowanie po statusie,
- dodać automatyczne tworzenie skrytek dla nowego paczkomatu,
- zabronić niepoprawnych przejść statusów,
- dodać testy automatyczne,
- uruchomić dwie instancje usługi na różnych portach,
- przygotować pierwszy plik Dockerfile.

---

## 12. Powiązanie z kolejnymi laboratoriami

```text
LAB1 — podstawowa usługa i API
  ↓
LAB2 — baza danych i cache
  ↓
LAB3 — Eureka / service discovery
  ↓
LAB4 — API Gateway
  ↓
LAB5 — RabbitMQ i zdarzenia
  ↓
LAB6 — Docker i uruchomienie całego systemu
```

Każde kolejne laboratorium rozszerza tę samą domenę paczkomatów, zamiast tworzyć niezależny przykład od początku.

---

## 13. Kryteria gotowości planu do implementacji

Przed rozpoczęciem kodowania należy zaakceptować:

- nazwę usługi: `Locker Service`,
- model paczkomatu i skrytki,
- listę obowiązkowych endpointów,
- sposób przechowywania danych w pamięci,
- port aplikacji,
- zakres błędów,
- strukturę projektu,
- zakres tematów odłożonych do kolejnych laboratoriów.

## 14. Kryteria zaliczenia LAB1

| Element | Wymaganie |
|---|---|
| Działanie | Usługa uruchamia się na własnym porcie |
| API | Działa minimalny zestaw endpointów |
| Model | Dane są walidowane i spójne |
| Błędy | Obsłużone są przypadki `404`, błędnych danych i konfliktu |
| Testy | Student ma powtarzalne testy poprawnych i błędnych przypadków |
| Rozumienie | Student potrafi wyjaśnić własny kod i decyzje |
| Dokumentacja | README zawiera instrukcję, API, testy i ograniczenia |
| AI | Użycie AI jest jawne, a wygenerowany kod zweryfikowany |

Najważniejsza zasada oceny:

> Oceniany jest nie tylko efekt końcowy, ale także poprawność rozumowania, jakość weryfikacji i umiejętność samodzielnego wyjaśnienia rozwiązania.

