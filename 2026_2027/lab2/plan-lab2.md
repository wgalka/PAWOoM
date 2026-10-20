# Plan realizacji LAB2 — persystencja danych i cache

> Plan roboczy poprzedzający instrukcję. Aktualny zakres, kryteria i sposób pracy określa [LAB2](README.md). Materiały pomocnicze są dostępne w [ZIP](lab2-support.zip); Redis jest wymaganym elementem ćwiczenia, a PostgreSQL i Alembic pozostają rozszerzeniami.

## Zakres tematyczny

**Od danych w pamięci do trwałej mikrousługi: baza danych i cache**

W LAB2 student rozwija tę samą usługę, którą przygotował w LAB1. Nie tworzy nowej aplikacji od początku. Najpierw zastępuje dane przechowywane w pamięci procesu trwałą bazą danych, a następnie dodaje cache dla wybranego odczytu.

Przykład wspólny nadal dotyczy `Locker Service`, ale zasadnicze zadanie student wykonuje w swoim własnym projekcie.

---

## 1. Zgodność zakresu z sylabusem

Laboratorium realizuje drugi punkt zajęć laboratoryjnych:

> Persystencja danych i cachowanie.

Podczas zajęć student:

- rozpozna, które dane należą do jego usługi,
- zaprojektuje prosty model relacyjny,
- podłączy aplikację FastAPI do bazy danych przez SQLAlchemy,
- zastąpi magazyn danych w pamięci trwałą persystencją,
- sprawdzi zachowanie usługi po restarcie,
- zastosuje cache-aside dla wybranego odczytu,
- zobaczy różnicę między źródłem prawdy a kopią danych w cache,
- obsłuży brak dostępności cache bez wyłączania podstawowej funkcji usługi,
- przygotuje testy oraz dokumentację decyzji.

W LAB2 nie wdrażamy jeszcze Eureki, API Gateway, RabbitMQ ani pełnego środowiska Docker Compose. Cache jest używany jako element funkcjonalny ćwiczenia, ale jego uruchomienie powinno być opisane tak, aby później można było przenieść je do kontenera.

---

## 2. Cele dydaktyczne

Po wykonaniu ćwiczenia student powinien rozumieć:

- dlaczego dane przechowywane wyłącznie w pamięci znikają po restarcie,
- czym różni się proces aplikacji od trwałej bazy danych,
- czym różni się model domenowy od tabeli bazy danych,
- dlaczego mikrousługa powinna być właścicielem swoich danych,
- jak aplikacja wykonuje odczyt i zapis przez warstwę dostępu do danych,
- czym różni się baza danych od cache,
- czym jest cache hit, cache miss i TTL,
- dlaczego cache może zawierać nieaktualną wartość,
- dlaczego zapis do bazy i unieważnienie cache muszą być przemyślane,
- co powinno się stać, gdy cache jest niedostępny,
- jak udowodnić testem, że dane przetrwały restart.

### Organizacja pracy podczas laboratorium

Nie chodzi o przepisanie konfiguracji SQLAlchemy ani Redis. Student powinien najpierw przewidzieć zmianę zachowania systemu, a dopiero potem ją zaimplementować.

Każdy większy etap ma cztery części:

1. **Obserwacja** — student sprawdza, jak działa wersja z LAB1.
2. **Decyzja** — student wybiera dane, tabelę, klucz cache i politykę unieważniania.
3. **Implementacja** — student wprowadza zmianę w swoim kodzie.
4. **Weryfikacja** — student wykonuje testy i interpretuje wynik.

---

## 3. Efekty kształcenia i dowody ich realizacji

| Efekt | Co student ćwiczy | Dowód wykonania |
|---|---|---|
| EK_03 — implementacja funkcjonalności | Integracja API z bazą danych i cache | Działająca usługa, testy odczytu i zapisu |
| EK_04 — projektowanie kilku usług | Określenie własności danych pierwszej usługi | Tabela danych należących do usługi i wskazanie danych, których nie powinna przechowywać |
| EK_01 — rozumienie pojęć | Rozróżnienie bazy, pamięci procesu i cache | Odpowiedzi na pytania kontrolne i eksperyment po restarcie |
| EK_02 — korzystanie z narzędzi | SQLAlchemy, sterownik bazy i klient Redis | README z konfiguracją, uruchomieniem i wykorzystaną dokumentacją |
| EK_05 — analiza jakości rozwiązania | Rozpoznanie ryzyka nieaktualnego cache i awarii zależności | Opis scenariusza cache miss, unieważniania i niedostępności Redis |

---

## 4. Stos technologiczny

### Zakres obowiązkowy

- Python 3.12 lub nowszy,
- FastAPI,
- Uvicorn,
- Pydantic,
- SQLAlchemy 2.x,
- SQLite jako lokalna baza danych,
- `pytest` i `httpx` do testów API,
- klient Redis dla Pythona (`redis`).

### Wariant docelowy i zadania rozszerzające

- PostgreSQL zamiast SQLite,
- Alembic do zarządzania migracjami schematu,
- Redis uruchomiony jako osobny proces lub kontener,
- konfiguracja przez zmienne środowiskowe,
- osobny moduł repozytorium i osobny moduł cache.

SQLite jest wariantem startowym, ponieważ pozwala przeprowadzić pierwszą część laboratorium bez konfigurowania serwera bazy. SQLAlchemy powinno jednak zostać użyte tak, aby późniejsza zmiana dialektu na PostgreSQL nie wymagała przepisywania endpointów.

---

## 5. Weryfikacja stanu usługi z LAB1

Student pracuje na własnej usłudze z LAB1. Przed rozpoczęciem powinien mieć:

- działający endpoint zdrowia usługi,
- co najmniej jeden odczyt danych,
- co najmniej jeden zapis lub modyfikację danych,
- model danych i walidację,
- testy podstawowego API,
- README z instrukcją uruchomienia.

Jeśli własna usługa nie działa, student może wykorzystać wspólny przykład `Locker Service`, ale powinien później przenieść rozwiązanie do własnego tematu.

### Weryfikacja trwałości danych przed zmianami

Student wykonuje następujące czynności:

1. uruchamia usługę,
2. dodaje lub modyfikuje rekord,
3. odczytuje go ponownie,
4. zatrzymuje proces,
5. uruchamia usługę jeszcze raz,
6. sprawdza, czy rekord nadal istnieje.

Należy zapisać wynik eksperymentu w README. To jest punkt odniesienia dla późniejszej wersji z bazą danych.

---

## 6. Decyzje projektowe przed implementacją

Przed rozpoczęciem implementacji student odpowiada na pytania dotyczące własnej usługi:

1. Jaki jest główny rekord, który musi przetrwać restart?
2. Które pola są wymagane, a które mogą być puste?
3. Jakie wartości powinny być unikalne?
4. Która usługa jest właścicielem tych danych?
5. Jakie dane należą do innej planowanej usługi i nie powinny trafić do tej tabeli?
6. Który odczyt będzie dobrym kandydatem do cache?
7. Jak rozpoznamy cache hit i cache miss?
8. Co powinno się stać z cache po utworzeniu, zmianie lub usunięciu rekordu?
9. Czy usługa nadal powinna obsługiwać podstawowy odczyt, gdy Redis nie działa?

Decyzje należy zapisać w krótkiej tabeli:

| Decyzja | Wybrana opcja | Uzasadnienie |
|---|---|---|
| Źródło prawdy | np. SQLite | Baza przechowuje trwały stan |
| Tabela główna | np. `rooms` | Odpowiada głównemu pojęciu domenowemu |
| Odczyt cache'owany | np. `GET /rooms/{id}` | Odczyt jest częsty i jednoznaczny |
| Klucz cache | np. `room:{id}` | Klucz wskazuje konkretny rekord |
| TTL | np. 60 sekund | Ogranicza czas życia nieaktualnej wartości |
| Unieważnianie | po zapisie i usunięciu | Cache nie powinien zwracać starego rekordu |
| Awaria Redis | odczyt z bazy | Cache nie jest źródłem prawdy |

---

## 7. Projekt modelu i określenie własności danych

### Model danych usługi `Locker Service`

Wspólny przykład może mieć następujący model:

```text
locker
-------
id
name
address
city
status

compartment
-----------
id
locker_id
code
status
```

`Locker Service` jest właścicielem paczkomatów i skrytek. Nie powinien przechowywać w swoich tabelach historii przesyłek, danych użytkowników ani informacji o wysyłce powiadomień.

### Projekt modelu dla własnej usługi

Student tworzy prosty model dla własnej usługi:

- minimum jedna tabela główna,
- minimum jeden identyfikator,
- minimum dwa pola domenowe,
- co najmniej jedno ograniczenie lub reguła, np. unikalność,
- opcjonalnie druga tabela, jeśli relacja jest potrzebna do wyjaśnienia domeny.

Nie należy tworzyć tabeli „na wszystko”. Model ma pokazywać granicę odpowiedzialności mikrousługi.

---

## 8. Przepływ odczytu i zapisu po dodaniu cache

### Odczyt danych bez użycia cache

```text
Klient
  |
  v
FastAPI
  |
  v
SQLAlchemy
  |
  v
Baza danych
```

### Odczyt danych z użyciem cache-aside

```text
Klient
  |
  v
FastAPI
  |
  +--> Redis: czy istnieje klucz?
  |       |
  |       +--> HIT  — zwróć wartość z cache
  |       |
  |       +--> MISS — pobierz z bazy i zapisz w Redis
  |
  +--> Baza danych
```

W wariancie cache-aside aplikacja sama decyduje, kiedy odczytać bazę i kiedy uzupełnić cache.

### Zapis danych i unieważnienie cache

Minimalny schemat zapisu:

```text
1. Walidacja danych
2. Zapis do bazy danych
3. Zatwierdzenie transakcji
4. Usunięcie starego klucza z cache
5. Kolejny odczyt pobierze aktualną wartość z bazy
```

Student powinien umieć wyjaśnić, dlaczego nie należy zapisywać nowej wartości tylko do Redis i pomijać bazy danych.

---

## 9. Sekwencja realizacji ćwiczenia

### Krok 0 — przygotowanie projektu i wersji z LAB1

Student:

- tworzy gałąź lub kopię roboczą `lab2-persistence-cache`,
- uruchamia testy z LAB1,
- sprawdza, że API działa przed zmianą,
- zapisuje wynik eksperymentu z restartem.

Punkt kontrolny: student potrafi pokazać, że dane z pamięci znikają po restarcie.

### Krok 1 — konfiguracja połączenia z bazą danych

Student:

- dodaje SQLAlchemy i sterownik SQLite,
- definiuje adres bazy przez konfigurację,
- tworzy moduł silnika i sesji,
- oddziela konfigurację od kodu endpointów.

Nie należy umieszczać połączenia z bazą w każdym endpointcie osobno.

### Krok 2 — implementacja modelu tabeli w SQLAlchemy

Student:

- wybiera rekord główny własnej usługi,
- tworzy model tabeli,
- definiuje typy pól,
- dodaje klucz główny,
- dodaje wymagane ograniczenia,
- określa, jak wygląda reprezentacja rekordu w odpowiedzi API.

Należy odróżnić:

- model domenowy,
- model tabeli,
- model wejściowy i wyjściowy API.

W prostym ćwiczeniu te modele mogą być podobne, ale nie powinny być utożsamiane bez wyjaśnienia.

### Krok 3 — inicjalizacja schematu i przygotowanie danych testowych

Student:

- tworzy tabele przy uruchomieniu w wersji ćwiczeniowej albo przygotowuje prostą migrację,
- dodaje dane początkowe tylko wtedy, gdy baza jest pusta,
- sprawdza, czy ponowne uruchomienie nie dubluje rekordów,
- opisuje położenie pliku SQLite w README.

`create_all` jest akceptowalne jako rozwiązanie startowe do laboratorium. Alembic jest zadaniem rozszerzającym; w projekcie końcowym należy opisać sposób zmiany schematu.

### Krok 4 — implementacja odczytu danych z bazy

Student przepisuje istniejący odczyt tak, aby:

- dane pochodziły z bazy,
- brak rekordu kończył się właściwym `404`,
- odpowiedź API nie ujawniała szczegółów implementacji bazy,
- sesja była poprawnie zamykana.

Punkt kontrolny: po restarcie usługi rekord utworzony wcześniej nadal jest dostępny.

### Krok 5 — implementacja zapisu i modyfikacji danych w bazie

Student przenosi do bazy co najmniej jedną operację zapisu oraz jedną operację modyfikacji lub usunięcia.

Należy sprawdzić:

- walidację danych wejściowych,
- konflikt unikalności,
- brak rekordu,
- zatwierdzenie transakcji,
- brak częściowo zapisanych danych po błędzie.

### Krok 6 — wydzielenie warstwy dostępu do danych

Student porządkuje kod tak, aby endpoint nie zawierał całej logiki zapytań SQLAlchemy.

Minimalny układ może wyglądać tak:

```text
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── repository.py
└── cache.py
```

Nazwy plików mogą być inne. Ważne jest, aby student potrafił wskazać, gdzie znajduje się:

- konfiguracja połączenia,
- model tabeli,
- walidacja API,
- dostęp do danych,
- obsługa cache.

### Krok 7 — obserwacja odczytu danych bez cache

Przed dodaniem Redis student wybiera jeden endpoint odczytu i opisuje jego ścieżkę:

```text
żądanie HTTP → endpoint → repozytorium → baza → odpowiedź HTTP
```

Opcjonalnie student mierzy czas odczytu lub dodaje log informujący o wykonaniu zapytania do bazy. Nie chodzi o wyścig na milisekundy, tylko o obserwację, skąd pochodzi odpowiedź.

### Krok 8 — zastosowanie cache-aside dla wybranego odczytu

Student:

- uruchamia Redis lub przygotowane środowisko testowe,
- wybiera jeden konkretny odczyt,
- definiuje klucz cache,
- serializuje odpowiedź do JSON,
- ustawia TTL,
- rozróżnia cache hit i cache miss,
- dodaje czytelny log albo nagłówek, np. `X-Cache: HIT` / `X-Cache: MISS`.

Na tym etapie nie należy cache'ować wszystkich endpointów automatycznie. Student ma rozumieć, co i dlaczego jest cache'owane.

### Krok 9 — unieważnianie cache po zmianie danych

Student sprawdza scenariusz:

1. pobierz rekord — powstaje cache miss,
2. pobierz rekord ponownie — występuje cache hit,
3. zmień rekord przez API,
4. pobierz rekord ponownie,
5. upewnij się, że odpowiedź nie zawiera starej wartości.

Jeżeli student świadomie wybiera inną strategię, np. aktualizację wartości w cache, musi opisać jej konsekwencje.

### Krok 10 — weryfikacja zachowania podczas awarii cache

Student zatrzymuje Redis albo konfiguruje nieprawidłowy adres i sprawdza:

- czy podstawowy zapis do bazy nadal działa,
- czy odczyt może przejść bez cache,
- jaki błąd jest logowany,
- czy użytkownik otrzymuje kontrolowaną odpowiedź.

Minimalna zasada odporności:

> Niedostępny cache może pogorszyć wydajność, ale nie powinien niszczyć podstawowej funkcji usługi, jeśli baza danych działa.

### Krok 11 — implementacja testów

Student dodaje lub aktualizuje testy dla:

- zapisu i odczytu po restarcie,
- braku rekordu,
- naruszenia reguły unikalności lub innej reguły domenowej,
- cache miss,
- cache hit,
- unieważnienia po zmianie,
- działania bez dostępnego cache, jeśli środowisko na to pozwala.

Testy nie powinny zależeć od przypadkowej kolejności uruchomienia ani od danych pozostawionych przez poprzedni test.

### Krok 12 — dokumentacja zmian we własnym projekcie

Student aktualizuje README o:

- sposób instalacji zależności,
- konfigurację bazy,
- sposób uruchomienia Redis,
- strukturę danych,
- listę używanych endpointów,
- opis przepływu cache hit/miss,
- politykę TTL i unieważniania,
- zachowanie podczas awarii Redis,
- instrukcję uruchomienia testów,
- ograniczenia rozwiązania,
- informację o użyciu AI i sposobie weryfikacji.

---

## 10. Decyzje projektowe pozostawione studentom

Instrukcja LAB2 nie powinna podawać całego rozwiązania. Student sam musi zdecydować:

- który rekord będzie tabelą główną,
- czy potrzebna jest druga tabela,
- jaki endpoint cache'ować,
- jak nazwać klucz Redis,
- jaki ustawić TTL,
- czy po zapisie usunąć klucz, czy zaktualizować cache,
- jak zachować się przy błędzie Redis,
- jak przetestować niezależność od kolejności testów.

Przykładowe zadanie:

> Wybierz jeden odczyt ze swojej usługi. Zaprojektuj dla niego strategię cache-aside. Zapisz przewidywany przebieg pierwszego, drugiego i trzeciego żądania, a następnie sprawdź, czy implementacja daje taki wynik.

---

## 11. Punkty kontrolne realizacji ćwiczenia

### Checkpoint A — weryfikacja stanu przed zmianami

Student pokazuje:

- działające API z LAB1,
- eksperyment utraty danych po restarcie,
- wybrany rekord i właściciela danych.

### Checkpoint B — weryfikacja integracji z bazą danych

Student pokazuje:

- model tabeli,
- konfigurację sesji,
- rekord zapisany w bazie,
- odczyt tego rekordu po restarcie procesu.

### Checkpoint C — weryfikacja reguł biznesowych i błędów

Student pokazuje:

- poprawny zapis,
- odrzucony błędny zapis,
- kontrolowany błąd braku rekordu,
- brak duplikatów po ponownym uruchomieniu.

### Checkpoint D — weryfikacja cache

Student pokazuje:

- pierwszy odczyt jako miss,
- kolejny odczyt jako hit,
- zmianę rekordu i brak starej wartości po unieważnieniu.

### Checkpoint E — wyjaśnienie decyzji technicznych

Student odpowiada własnymi słowami:

1. Co jest źródłem prawdy w twojej usłudze?
2. Dlaczego cache nie może zastąpić bazy danych?
3. Co stanie się po wygaśnięciu TTL?
4. Dlaczego po zmianie danych trzeba unieważnić lub zaktualizować cache?
5. Jak zachowa się usługa, gdy Redis przestanie działać?
6. Czy wszystkie dane systemu powinny znaleźć się w jednej bazie?
7. Co zmieniłoby się przy przejściu z SQLite na PostgreSQL?

---

## 12. Porównanie pamięci procesu, bazy danych i cache

| Cecha | Pamięć procesu | Baza danych | Cache |
|---|---|---|---|
| Przetrwanie restartu aplikacji | Nie | Tak | Zwykle nie należy tego zakładać |
| Rola | Tymczasowy stan | Źródło prawdy | Szybka kopia danych |
| Trwałość | Brak | Wysoka | Ograniczona przez TTL i awarie |
| Aktualność | Aktualna w procesie | Zgodna z zatwierdzonym zapisem | Może być nieaktualna |
| Główne ryzyko | Utrata danych | Błąd połączenia lub transakcji | Stara wartość i niespójność |
| Czy może zastąpić bazę? | Nie | — | Nie |

Student powinien umieć wyjaśnić, dlaczego dodanie Redis nie oznacza usunięcia bazy danych.

---

## 13. Zakres poza LAB2

W LAB2 nie realizujemy jeszcze:

- rejestracji usług w Eurece,
- odnajdywania usług po nazwie,
- API Gateway,
- komunikacji przez RabbitMQ,
- zdarzeń domenowych i Sagi,
- pełnego uruchomienia wszystkich usług w Docker Compose,
- rozdzielania usług na osobne komputery.

Na końcu LAB2 student ma jedną trwalszą mikrousługę z cache. Dopiero później do systemu zostaną dołączone service discovery, gateway i komunikacja asynchroniczna.

---

## 14. Zadania rozszerzające

Po wykonaniu minimum student może:

- przełączyć bazę z SQLite na PostgreSQL,
- przygotować migrację Alembic,
- dodać indeks dla często używanego wyszukiwania,
- porównać odczyt z cache i bez cache,
- zastosować różny TTL dla różnych typów danych,
- dodać endpoint czyszczenia cache tylko na potrzeby testów,
- przygotować test integracyjny z rzeczywistym Redis,
- zaprojektować cache dla listy z filtrem,
- opisać problem stampede, gdy wiele żądań jednocześnie odświeża ten sam klucz,
- dodać mechanizm wersjonowania kluczy cache.

---

## 15. Warunki rozpoczęcia implementacji instrukcji LAB2

Przed rozpoczęciem pisania pełnej instrukcji `lab2.md` należy zaakceptować:

- czy SQLite jest obowiązkowym wariantem startowym,
- czy Redis będzie uruchamiany lokalnie, przez Docker, czy przez przygotowane środowisko,
- który endpoint wspólny zostanie użyty jako przykład cache,
- czy nagłówek `X-Cache` będzie wymagany, czy tylko log,
- czy Alembic pozostaje zadaniem rozszerzającym,
- jakie minimum testów musi wykonać każdy student,
- jakie elementy muszą znaleźć się w README,
- jak oceniane będzie zachowanie przy niedostępności cache.

---

## 16. Kryteria zaliczenia etapu LAB2

| Element | Wymaganie |
|---|---|
| Persystencja | Dane są zapisywane w bazie i przetrwają restart procesu |
| Model | Tabela odpowiada odpowiedzialności usługi i ma podstawowe ograniczenia |
| API | Istniejący kontrakt z LAB1 nadal działa albo zmiany są udokumentowane |
| Operacje | Działa co najmniej jeden odczyt i jeden zapis przez bazę |
| Cache | Jeden odczyt korzysta z cache-aside i ma opisaną politykę TTL |
| Spójność | Zmiana lub usunięcie rekordu nie zwraca starej wartości z cache |
| Odporność | Awaria cache nie powoduje niekontrolowanego błędu podstawowego odczytu, jeśli baza działa |
| Testy | Sprawdzone są zapis, restart, błędne dane, cache hit, cache miss i unieważnienie |
| Dokumentacja | README zawiera konfigurację, uruchomienie, decyzje i ograniczenia |
| Rozumienie | Student potrafi wyjaśnić różnicę między bazą, pamięcią procesu i cache |
| AI | Użycie AI jest jawne, a wygenerowany kod został uruchomiony i zweryfikowany |

---

## 17. Miejsce LAB2 w projekcie semestralnym

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

LAB2 kończy etap budowania pojedynczej usługi jako samodzielnego komponentu. W LAB3 usługa przestanie być odnajdywana wyłącznie przez ręcznie wpisany adres, a w kolejnych laboratoriach zacznie współpracować z innymi usługami.
