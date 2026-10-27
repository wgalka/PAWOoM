# LAB4 — Konfiguracja wspólnego punktu wejścia (API Gateway)

## Projektowanie aplikacji webowych opartych o mikrousługi

- **Czas:** 120 minut zajęć; JDK, Maven i zależności należy przygotować przed zajęciami
- **Technologia:** Spring Cloud Gateway, Eureka oraz dwie usługi Python/FastAPI z LAB3
- **Forma:** praca indywidualna lub w parach
- **Rezultat:** jedno wejściowe API przekazujące żądania do dwóch usług odnajdywanych po nazwie

## 1. Cel i zakres laboratorium

Należy zrealizować temat sylabusa „Konfiguracja API Gateway”, rozwijając projekt z LAB1–LAB3. Do istniejących usług należy dodać bramkę HTTP, skonfigurować trasy oraz sprawdzić ich działanie i zachowanie podczas awarii. Nie należy przenosić logiki biznesowej do bramki.

Po laboratorium należy umieć:

- odróżnić API Gateway od rejestru Eureka i usługi domenowej,
- zaprojektować ścieżki dostępne dla klienta i przypisać je do usług,
- skonfigurować trasę, warunek jej dopasowania i filtr ścieżki,
- przekazać żądanie do usługi odnalezionej przez nazwę logiczną,
- rozróżnić brak trasy, brak zasobu i niedostępność procesu,
- sprawdzić przez gateway odczyt, zapis i błąd istniejącego API.

| Efekt | Ćwiczone działanie | Dowód wykonania |
|---|---|---|
| EK_03 | Konfiguracja rozwiązania z wykorzystaniem dokumentacji | Działające trasy, testy i opis wykorzystanych źródeł |
| EK_04 | Projektowanie komunikacji wielu komponentów | Diagram i kontrakt wejściowy dwóch usług |
| EK_01, EK_02 | Rozróżnienie ról komponentów i użycie narzędzi | Wyjaśnienie przepływu żądania i uruchomienie środowiska |
| EK_05 | Ocena skutków awarii i ograniczeń rozwiązania | Wyniki eksperymentów oraz wnioski |

## 2. Zachowanie ciągłości projektu

Należy kontynuować własny temat i repozytorium. Przed zmianami należy uruchomić dotychczasowe testy oraz zachować działający etap w Git. Nie należy zastępować projektu przykładem paczkomatów.

Należy zachować:

- granice odpowiedzialności, słownik domenowy i reguły biznesowe z LAB1,
- bazę danych, cache i ich testy z LAB2,
- dwie odrębne usługi, rejestrację w Eurece oraz wywołanie między usługami z LAB3,
- dotychczasowe endpointy usług i ich kody odpowiedzi.

Gateway należy dodać jako osobny komponent infrastruktury. Nie zastępuje on wymaganej mikrousługi domenowej. W projekcie semestralnym każda osoba nadal musi zaimplementować co najmniej dwie różne mikrousługi. W parze należy opisać wkład autorów i zamieniać role osoby konfigurującej oraz sprawdzającej.

Proponowany podział 120 minut: 15 minut pojęć, 20 minut wspólnego przykładu, 15 minut decyzji projektowych, 35 minut konfiguracji własnego projektu, 25 minut testów i 10 minut odbioru. Na koniec zajęć należy pokazać dwie działające trasy własnego projektu. Po zajęciach można dokończyć testy automatyczne i dokumentację; nadal należą one do wymagań oddawanego etapu.

## 3. Rozróżnienie bramki, rejestru i usług

W LAB3 klient musiał znać adres konkretnej usługi, np. `http://127.0.0.1:8101`. Po dodaniu gateway klient może wywoływać różne funkcje pod jednym adresem, np. `http://127.0.0.1:8080/api/...`. Bramka wybiera trasę i przekazuje żądanie HTTP do właściwej usługi; odpowiedź wraca przez bramkę do klienta.

| Komponent | Odpowiedzialność | Czego nie należy w nim umieszczać |
|---|---|---|
| Eureka | Informacje o instancjach: nazwy, adresy, porty | Danych paczek ani przekazywania żądań domenowych |
| API Gateway | Dopasowanie trasy, przekształcenie ścieżki, przekazanie HTTP | Reguł przyjmowania paczki ani bezpośredniego dostępu do bazy usług |
| Usługa domenowa | Własne API, dane i reguły biznesowe | Zapisu do bazy należącej do innej usługi |

### Prześledzenie połączeń między procesami

<pre class="mermaid">
flowchart LR
    K["Klient HTTP"] --> G["API Gateway :8080"]
    G -->|"/lockers/..."| L["Locker Service :8101"]
    G -->|"/delivery-check/..."| P["Parcel Service :8102"]
    P -->|"Wywołanie z LAB3"| L
    G -.->|"Pobieranie rejestru"| E["Eureka :8761"]
    P -.->|"Rejestracja i pobieranie rejestru"| E
    L -.->|"Rejestracja i heartbeat"| E
</pre>

Linie ciągłe oznaczają żądania domenowe; przerywane — komunikację z rejestrem. Gateway, podobnie jak klient z LAB3, korzysta z okresowo odświeżanej lokalnej kopii rejestru. Nie należy oczekiwać zapytania do Eureki przy każdym żądaniu użytkownika. Własna baza i Redis pozostają przy usłudze z LAB2; nie są potrzebne bramce.

Nie należy kierować istniejącego wywołania usługa–usługa przez gateway tylko dlatego, że dodano bramkę. W tym ćwiczeniu gateway obsługuje wejście klienta, a komunikacja wewnętrzna z LAB3 pozostaje bezpośrednia.

### Odczytanie definicji trasy

**Trasa (route)** łączy identyfikator, adres docelowy, warunki dopasowania i filtry. **Predicate** jest warunkiem wyboru trasy, np. zgodnością ścieżki z `Path`. **Filtr** wykonuje operację na żądaniu lub odpowiedzi, np. usuwa początkowy segment ścieżki albo dodaje nagłówek.

| Element | Przykład | Znaczenie |
|---|---|---|
| `id` | `lockers` | Nazwa trasy w konfiguracji bramki, nie nazwa usługi |
| `uri` | `lb://LOCKER-SERVICE` | Wybór instancji usługi po nazwie z Eureki |
| `Path` | `/api/lockers/**` | Dopasowanie żądań do tej trasy |
| `StripPrefix=1` | `/api/lockers/KRK-1024` → `/lockers/KRK-1024` | Usunięcie jednego segmentu, czyli `api` |
| `AddResponseHeader` | `X-Gateway: lab4` | Dodatkowy nagłówek w odpowiedzi przekazywanej trasą |

`lb` oznacza wykorzystanie mechanizmu wyboru instancji (load balancing). Przy jednej instancji nadal można stosować `lb://...`; nie powstaje przez to druga instancja ani odporność na awarię jedynego procesu. Nazwy `LOCKER-SERVICE` i `PARCEL-SERVICE` należy sprawdzić w panelu Eureki.

### Ocena korzyści i ograniczeń

Wspólny adres ułatwia klientowi korzystanie z kilku usług, a jawne trasy pozwalają wybrać udostępniane ścieżki. Należy jednak uwzględnić dodatkowy proces, połączenie sieciowe i punkt awarii. Zatrzymanie jedynej bramki odcina dostęp przez jej adres, nawet jeśli usługi nadal działają.

Nie należy utożsamiać błędu HTTP `500` z zakończeniem procesu: zarówno monolit, jak i mikrousługa mogą zwrócić błąd dla jednego żądania i nadal obsługiwać inne. Izolację procesów należy sprawdzić przez rzeczywiste zatrzymanie jednego z nich.

Sama konfiguracja gateway nie blokuje bezpośrednich portów usług, nie uwierzytelnia użytkownika i nie zastępuje autoryzacji. „API wejściowe” oznacza tu kontrakt dla klienta lokalnego, nie publikację aplikacji w Internecie. Nie należy otwierać portów w zaporze ani udostępniać środowiska poza komputerem.

## 4. Przygotowanie i uruchomienie przykładu

### Krok 1. Pobranie pakietu i sprawdzenie środowiska

Należy pobrać [pakiet pomocniczy LAB4 — ZIP]({{ '/2026_2027/lab4/lab4-support.zip' | relative_url }}) i rozpakować go obok własnego projektu. Do przykładu należy wykorzystać usługi z [LAB3]({{ '/2026_2027/lab3/' | relative_url }}) oraz [pakiet LAB3]({{ '/2026_2027/lab3/lab3-support.zip' | relative_url }}).

```text
lab4-support/
├── gateway/
│   ├── pom.xml
│   └── src/main/
│       ├── java/pl/ur/pawoom/lab4/GatewayApplication.java
│       └── resources/application.yml
├── tests/test_gateway_demo.py
├── requirements.txt
├── README-LAB4-template.md
└── README.md
```

Wymagane są Python 3.12 lub nowszy, JDK 21 oraz Maven 3.9.x. Java uruchamia bramkę, Maven pobiera zależności i buduje aplikację. Nie należy przepisywać usług Python na Javę. Dostarczona klasa uruchamia gateway i udostępnia `/health`; zadaniem jest konfiguracja oraz weryfikacja tras.

W PowerShellu należy sprawdzić:

```powershell
python --version
java -version
mvn -version
```

Jeżeli `mvn` nie jest rozpoznawany, należy przygotować Maven przed zajęciami zgodnie z [instrukcją instalacji Apache Maven](https://maven.apache.org/install.html). Można użyć archiwum JDK i Maven rozpakowanego do katalogu użytkownika; nie jest potrzebna instalacja usługi systemowej. Zmienna `JAVA_HOME` powinna wskazywać katalog JDK, a `PATH` jego `bin` i katalog `bin` Mavena. Należy sprawdzić, czy `mvn -version` wskazuje właściwą Javę. Pierwsze uruchomienie wymaga dostępu do repozytorium zależności.

Bramkę i usługi Python należy uruchamiać lokalnie w tym samym systemie. Docker ani maszyna wirtualna nie są wymagane dla gateway. Eurekę należy uruchomić metodą wybraną na LAB3 — przez Maven lub dotychczasowy kontener. Nie należy uruchamiać drugiego rejestru na tym samym porcie.

### Krok 2. Uruchomienie dwóch usług z LAB3

Należy uruchomić Eurekę oraz demo `LOCKER-SERVICE` i `PARCEL-SERVICE`, korzystając z poleceń pakietu LAB3. Na czas przykładu należy zatrzymać własne usługi zajmujące te porty lub rejestrujące się pod tymi samymi nazwami. Każdy proces powinien mieć osobny terminal.

Przed uruchomieniem bramki należy wykonać:

```powershell
curl.exe -i http://127.0.0.1:8101/lockers/KRK-1024
curl.exe -i http://127.0.0.1:8102/delivery-check/KRK-1024
```

Należy oczekiwać `200` i danych znanego paczkomatu w obu przypadkach. Jeśli drugi odczyt nie działa, należy najpierw usunąć problem z LAB3. Gateway nie naprawia błędnej rejestracji ani komunikacji między usługami.

### Krok 3. Odczytanie konfiguracji bramki

Należy otworzyć `gateway/src/main/resources/application.yml`. Poniżej przedstawiono fragment istniejącej konfiguracji pierwszej trasy; nie należy dopisywać go jako drugiego bloku `spring`:

```yaml
spring:
  cloud:
    gateway:
      server:
        webflux:
          routes:
            - id: lockers
              uri: lb://LOCKER-SERVICE
              predicates:
                - Path=/api/lockers,/api/lockers/**
              filters:
                - StripPrefix=1
```

Należy odnaleźć drugą trasę, prowadzącą do `PARCEL-SERVICE`, oraz porównać jej ścieżkę. W `Path` podano ścieżkę kolekcji i ścieżki podrzędne. Samo dopasowanie nie tworzy endpointów w usłudze: demo nie ma `GET /lockers`, chociaż trasa dopuszcza taki adres. Nie należy dodawać warunku `Method=GET`, jeśli tą samą trasą mają przechodzić także operacje zapisu.

W pakiecie należy zwrócić uwagę na:

- `register-with-eureka: false` i `fetch-registry: true` — bramka pobiera rejestr, lecz sama nie zgłasza instancji; brak wpisu `API-GATEWAY` w panelu jest prawidłowy,
- `defaultZone` — adres API Eureki **z końcówką `/eureka/`**; w kliencie Python z LAB3 `EUREKA_SERVER_URL` nie zawiera tej końcówki, ponieważ dodaje ją osobny parametr,
- `discovery.locator.enabled: false` — brak automatycznego publikowania tras do wszystkich zarejestrowanych usług; trasy należy deklarować jawnie,
- `connect-timeout: 1000` — limit nawiązywania połączenia wynoszący 1000 ms,
- `response-timeout: 5s` — limit oczekiwania na odpowiedź usługi; nie należy traktować go jako gwarantowanego limitu czasu wszystkich operacji w całym systemie,
- `default-filters` — filtr dodający `X-Gateway: lab4` do odpowiedzi przekazywanych trasami.

Starter `spring-cloud-starter-loadbalancer` w `pom.xml` umożliwia obsługę `lb://`. Należy zachować wersje zależności pakietu oraz strukturę `spring.cloud.gateway.server.webflux`. Nie należy mieszać jej z przykładami przeznaczonymi dla innej wersji lub wariantu Server Web MVC.

### Krok 4. Uruchomienie gateway i sprawdzenie tras

W nowym terminalu, z katalogu `lab4-support`, należy wykonać:

```powershell
Set-Location .\gateway
mvn spring-boot:run
```

Po uruchomieniu aplikacji w innym terminalu należy wykonać:

```powershell
curl.exe -i http://127.0.0.1:8080/health
curl.exe -i http://127.0.0.1:8080/api/lockers/KRK-1024
curl.exe -i http://127.0.0.1:8080/api/delivery-check/KRK-1024
```

`curl.exe` pozwala w PowerShellu uniknąć pomylenia programu curl z aliasem; opcja `-i` pokazuje kod i nagłówki odpowiedzi. Należy oczekiwać `200` dla trzech żądań. `/health` bramki zwraca `service: API-GATEWAY`, a odpowiedzi domenowe zawierają dane z LAB3 i nagłówek `X-Gateway: lab4`. `/health` nie sprawdza dostępności Eureki ani usług i nie korzysta z filtrów tras.

Po rejestracji usług może być potrzebne odczekanie na odświeżenie rejestru klienta. Przy błędzie należy porównać panel Eureki, log bramki i odpowiedź bezpośrednią usługi. Nie należy uznawać samego `UP` za dowód działania całego przepływu.

| Żądanie klienta do portu 8080 | Cel po wyborze instancji | Ścieżka otrzymana przez usługę |
|---|---|---|
| `GET /api/lockers/KRK-1024` | `LOCKER-SERVICE` | `/lockers/KRK-1024` |
| `GET /api/delivery-check/KRK-1024` | `PARCEL-SERVICE` | `/delivery-check/KRK-1024` |

<pre class="mermaid">
sequenceDiagram
    participant K as Klient
    participant G as Gateway
    participant P as Parcel Service
    participant L as Locker Service
    K->>G: GET /api/delivery-check/KRK-1024
    Note over G: Dopasowanie trasy, StripPrefix=1, wybór instancji
    G->>P: GET /delivery-check/KRK-1024
    P->>L: GET /lockers/KRK-1024 (wywołanie z LAB3)
    L-->>P: 200 + dane paczkomatu
    P-->>G: 200 + destination i locker
    G-->>K: 200 + JSON + X-Gateway
</pre>

Przed dalszą pracą należy wskazać, który komponent usuwa `api`, który składa odpowiedź `destination` i `locker`, a który przechowuje dane o adresach instancji.

### Krok 5. Sprawdzenie dwóch różnych błędów 404

Należy wykonać:

```powershell
curl.exe -i http://127.0.0.1:8080/api/lockers/UNKNOWN
curl.exe -i http://127.0.0.1:8080/not-a-route
```

Pierwsze żądanie trafia do usługi i powinno zwrócić `404` z `{"detail":"Locker not found"}`. Drugie nie pasuje do trasy; odpowiedź `404` powstaje w bramce. Należy porównać treść, nagłówek `X-Gateway` oraz log dostępu Uvicorna. Sam kod `404` nie wskazuje miejsca powstania błędu. Nagłówek jest pomocą diagnostyczną, a nie zabezpieczeniem ani gwarancją oznaczenia wszystkich błędów.

Następnie należy przewidzieć wynik zmiany `StripPrefix=1` na `StripPrefix=2` w pierwszej trasie. Dopiero po zapisaniu przewidywania należy zmienić filtr, ponownie uruchomić gateway i wykonać odczyt znanego paczkomatu. Należy wskazać otrzymaną przez usługę ścieżkę i przyczynę `404`. Po eksperymencie należy przywrócić `StripPrefix=1` i ponownie uruchomić bramkę.

### Krok 6. Uruchomienie testów przykładu

Przy działającej Eurece, obu usługach demo i bramce, w nowym terminalu w katalogu `lab4-support` należy wykonać:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

Należy oczekiwać `5 passed`. Są to **testy integracyjne** wykonujące rzeczywiste HTTP; nie uruchamiają procesów i nie korzystają z atrap Eureki. Sprawdzają proces bramki, dwie trasy, nagłówek, przekazanie domenowego `404` i brak trasy. Nie sprawdzają zapisu, ponieważ demo LAB3 udostępnia tylko odczyt. Zapis należy sprawdzić we własnym projekcie.

## 5. Zaprojektowanie tras własnego projektu

Przed edycją konfiguracji należy zatrzymać demo i uruchomić własne usługi z LAB3. Należy uzupełnić tabelę dla własnej domeny, nie kopiując nazw paczkomatów:

| Metoda i ścieżka klienta | Nazwa usługi w Eurece | Ścieżka w usłudze | Uzasadnienie |
|---|---|---|---|
| Przykład: `GET /api/rooms/R1` | `ROOM-SERVICE` | `/rooms/R1` | Odczyt sali przed rezerwacją |
| Własna operacja pierwszej usługi | | | |
| Własna operacja drugiej usługi | | | |
| Własna operacja zapisu | | | |

Przykład sali pokazuje sposób zapisu kontraktu, nie narzuca nowego tematu. Należy odpowiedzieć:

1. Które endpointy obu usług są potrzebne klientowi i dlaczego?
2. Które ścieżki, np. diagnostyczne, pozostaną bez trasy w gateway?
3. Jak po usunięciu prefiksu będzie wyglądać ścieżka otrzymana przez usługę?
4. Która usługa nadal sprawdza regułę biznesową i jest właścicielem zapisywanych danych?
5. Czy awaria jednej usługi wpływa na drugą trasę bezpośrednio, czy przez zależność z LAB3?

W ramach DDD należy zachować nazwy ze słownika domenowego i granice odpowiedzialności. Wspólny prefiks `/api` nie oznacza wspólnej bazy ani połączenia modeli usług. Nie należy implementować w gateway reguł domenowych, np. decyzji o dostępności skrytki.

## 6. Dodanie gateway do własnego projektu

### Krok 1. Włączenie komponentu i konfiguracja tras

Należy skopiować katalog `gateway` do własnego repozytorium, bez `target`. Do własnego `.gitignore` należy dodać `gateway/target/`. Należy zachować osobne katalogi i środowiska usług Python.

W `application.yml` należy zastąpić obie przykładowe trasy własnymi. Należy skonfigurować co najmniej dwie jawne trasy domenowe, po jednej do każdej usługi, z `lb://NAZWA-USŁUGI`. Nie należy wpisywać portów instancji w `uri`, używać jednej trasy przechwytującej wszystko ani włączać automatycznego publikowania wszystkich usług.

Należy zachować filtr ścieżki odpowiedni do istniejącego API, nagłówek diagnostyczny oraz skończone limity czasu. W dokumentacji należy uzasadnić limity względem wywołania usługa–usługa z LAB3: zbyt krótki limit bramki może przerwać oczekiwanie przed odpowiedzią usługi. Nie należy dodawać automatycznych ponowień zapisu, które mogłyby powtórzyć operację biznesową.

Przy zajętym porcie `8080` można ustawić w terminalu gateway `$env:GATEWAY_PORT = '8088'` przed uruchomieniem Maven. Należy wtedy zmienić adres w poleceniach i testach. Nie należy kończyć nieznanych procesów zajmujących port.

### Krok 2. Sprawdzenie odczytu i zapisu przez bramkę

Należy wykonać przez gateway odczyt domenowy z każdej usługi i porównać odpowiedź z wywołaniem bezpośrednim. Następnie należy wykonać istniejącą operację zapisu pierwszej usługi, a po niej odczyt zmienionych danych. Należy sprawdzić zachowanie metody HTTP, JSON, kodu odpowiedzi oraz wpływ zmiany na cache z LAB2.

Przykładowa konstrukcja klienta Python, do dostosowania do rzeczywistego kontraktu:

```python
import httpx

# Ścieżkę i pola należy zastąpić kontraktem własnej usługi.
with httpx.Client(base_url="http://127.0.0.1:8080", timeout=10) as client:
    response = client.post("/api/rooms", json={"id": "R1", "capacity": 20})
    print(response.status_code, response.text)
```

Nie należy przyjmować, że każda operacja zapisu zwraca `200`: należy użyć kodu własnego API, np. `201` dla utworzenia albo `204` bez treści dla usunięcia. Dane testowe powinny mieć unikatowe identyfikatory. Nie należy ponawiać tworzenia tego samego zasobu, a następnie traktować oczekiwanego `409` jako błędu bramki.

Należy także wysłać dane naruszające walidację lub regułę biznesową i wykazać zachowanie dotychczasowego `422` albo `409`. Jeśli API ma parametry zapytania, należy sprawdzić istniejące filtrowanie, np. `?status=...`; nie należy dodawać sztucznego filtra tylko na potrzeby gateway. Bramka nie zastępuje walidacji w FastAPI.

### Krok 3. Sprawdzenie awarii i przywrócenia działania

Należy wykonać scenariusze pojedynczo, zapisując kod, treść odpowiedzi, stan procesów i wniosek:

| Scenariusz | Co należy sprawdzić |
|---|---|
| Brak zasobu w działającej usłudze | Czy `404` i treść usługi przechodzą przez gateway |
| Nieistniejąca trasa gateway | Czy bramka zwraca `404` bez wywołania usługi |
| Zatrzymana jedna usługa (`Ctrl+C`) | Błąd jej trasy, stan drugiej trasy i bezpośredni `/health` drugiej usługi |
| Ponownie uruchomiona usługa | Powrót poprawnej odpowiedzi po rejestracji i odświeżeniu kopii rejestru |
| Zatrzymany gateway | Brak połączenia na porcie bramki przy nadal działającym bezpośrednim API usług |

Do sprawdzenia niezależnej trasy należy najpierw zatrzymać usługę wywołującą, a nie jej zależność. W demo zatrzymanie `PARCEL-SERVICE` pozostawia odczyt paczkomatu przez gateway. Zatrzymanie `LOCKER-SERVICE` wpływa również na `delivery-check`, ponieważ ta operacja potrzebuje paczkomatu. Należy wyciągnąć wniosek o zależnościach, a nie zakładać, że wszystkie pozostałe funkcje zawsze będą dostępne.

Gdy mechanizm wyboru instancji nie znajduje żadnego kandydata, gateway domyślnie zwraca `503`. Gdy lokalny rejestr nadal zawiera zatrzymany proces, błąd może powstać dopiero podczas połączenia; nie należy oczekiwać identycznej odpowiedzi na każdym etapie aktualizacji rejestru. Nieobsłużony błąd połączenia może dać `500`, a przekroczenie limitu oczekiwania na odpowiedź — `504`. Należy odróżnić te błędy bramki od przekazanego `503` wygenerowanego przez usługę wywołującą zależność z LAB3.

Wpisy Eureki i kopie rejestru nie zmieniają się natychmiast. Należy zapisać obserwowane opóźnienie, zamiast dodawać test zależny od arbitralnego krótkiego `sleep`. Nie należy wyłączać mechanizmów bezpieczeństwa Eureki tylko po to, aby wynik pojawił się szybciej. Odmowa połączenia przy zatrzymanej bramce nie jest odpowiedzią HTTP `500` ani `503`.

### Krok 4. Napisanie własnych testów integracyjnych

Należy zachować wcześniejsze testy jednostkowe i dodać co najmniej cztery **własne** testy integracyjne, odwołujące się do uruchomionego gateway:

1. Odczyt domenowy pierwszej usługi, poprawna treść i nagłówek diagnostyczny.
2. Odczyt domenowy drugiej usługi, z kontrolą treści, nie tylko kodu `200`.
3. Zapis i następujący po nim odczyt potwierdzający skutek operacji.
4. Błąd walidacji lub reguły biznesowej, z kontrolą kodu i treści.

Przykładowy schemat testu należy dostosować do własnej domeny:

```python
def test_read_resource_through_gateway(client):
    response = client.get("/api/rooms/R1")
    assert response.status_code == 200
    assert response.json()["id"] == "R1"
    assert response.headers["x-gateway"] == "lab4"
```

Fixture `client` można zaadaptować z pakietu. Należy przygotować rekord `R1` lub zastąpić go własnym identyfikatorem; fragment nie tworzy danych. Test zapisu powinien używać nowego identyfikatora i sprzątać wyłącznie dane utworzone na potrzeby testu, jeśli API umożliwia usuwanie. Nie należy kasować całej bazy projektu. Należy opisać sposób ponownego uruchomienia testów bez konfliktów danych.

Testy integracyjne należy trzymać oddzielnie od jednostkowych, np. w `tests/integration`, i podać osobne polecenia ich uruchomienia. Sprawdzenie samego `create_app()` z atrapą klienta nie potwierdza działania gateway ani Eureki. Scenariusze awarii z kroku 3 należy udokumentować ręcznie; nie są zastępowane czterema testami powyżej.

### Krok 5. Uzupełnienie dokumentacji projektu

Należy wykorzystać `README-LAB4-template.md` z pakietu jako listę pól do uzupełnienia. W dokumentacji należy podać diagram, tabelę tras, granice odpowiedzialności, komendy z katalogami roboczymi, porty, zmienne, przygotowanie danych, uruchomienie testów, wyniki awarii i sposób zatrzymania procesów. Należy również wskazać, które ścieżki nie zostały udostępnione przez bramkę.

Można korzystać z AI do konfiguracji i testów. Należy jednak samodzielnie uzasadnić wybór tras, przewidzieć ścieżkę po filtrze i zweryfikować kod. W dokumentacji należy opisać zakres wsparcia AI oraz co najmniej dwa wykorzystane źródła: konkretny problem, zastosowane rozwiązanie i dowód jego sprawdzenia.

## 7. Rozpoznawanie problemów konfiguracji

| Objaw | Co należy sprawdzić |
|---|---|
| `mvn` nie jest rozpoznawany lub błędna Java | `PATH`, `JAVA_HOME`, `mvn -version`; nie należy instalować pakietu Python o podobnej nazwie |
| Błąd pobierania zależności | Dostęp do sieci, konfigurację proxy Maven i pełny komunikat; nie należy usuwać losowo wersji z `pom.xml` |
| `/health` działa, a każda trasa daje `404` | Wcięcia YAML, położenie `routes` pod `server.webflux`, zapis pliku i restart gateway |
| Tylko konkretna ścieżka daje `404` | `Path`, liczbę usuwanych segmentów, ścieżkę w logu Uvicorna oraz istnienie zasobu |
| `503` mimo działającej usługi | Nazwę w `lb://`, adres Eureki z `/eureka/`, pobranie rejestru i czas odświeżenia |
| Błąd połączenia do wpisu `UP` | Faktyczny proces, zgodność portów i osiągalność adresu instancji z procesu gateway |
| `405 Method Not Allowed` | Czy endpoint usługi obsługuje tę metodę HTTP |
| `422` lub `409` przy zapisie | JSON, wymagane pola i regułę biznesową; nie należy zamieniać błędu na `200` w bramce |
| `/api/docs` nie działa | Brak takiej trasy; Swagger każdej usługi należy otwierać bezpośrednio na jej porcie |
| Po zmianie YAML nadal stare zachowanie | Restart procesu Maven; bramka nie działa z Pythonowym `--reload` |

Nie należy rozszerzać tego etapu o logowanie użytkowników, agregację Swaggera, RabbitMQ, klaster bramek, frontend ani pełną konteneryzację. Należy skoncentrować się na poprawnym routingu istniejących API i jego weryfikacji.

## 8. Punkty kontrolne i kryteria zaliczenia etapu

| Punkt | Oczekiwany rezultat |
|---|---|
| A — ciągłość | Działające usługi, baza, cache, Eureka i wcześniejsze testy |
| B — kontrakt | Własna tabela tras i uzasadnienie granic API |
| C — konfiguracja | Dwie trasy do różnych usług przez `lb://` oraz poprawne ścieżki |
| D — zachowanie API | Odczyt, zapis i błędy przechodzą przez gateway bez zmiany reguł domenowych |
| E — awarie | Udokumentowane zatrzymanie usługi, jej przywrócenie i zatrzymanie bramki |
| F — weryfikacja | Cztery własne testy integracyjne oraz powtarzalna instrukcja uruchomienia |

Podczas odbioru każda osoba powinna umieć wyjaśnić:

1. Dlaczego Eureka i gateway są dwoma różnymi komponentami?
2. Co zmienia `StripPrefix`, a czego nie zmienia?
3. Jak gateway wybiera instancję i dlaczego nie ma portu usługi w definicji trasy?
4. Jak odróżnić brak trasy od braku zasobu?
5. Co przestaje działać po zatrzymaniu bramki, a co po zatrzymaniu jednej usługi?
6. Dlaczego gateway nie jest dodatkową mikrousługą domenową ani automatycznym zabezpieczeniem API?

Należy również umieć wykonać małą zmianę, np. zmienić prefiks wejściowy, przewidzieć ścieżkę docelową i poprawić odpowiedni test.

| Obszar | Element | Punkty |
|---|---|---:|
| Kod | Zachowanie działania usług i mechanizmów LAB1–LAB3 | 10 |
| Kod | Dwie trasy przez Eurekę, poprawne ścieżki i filtr diagnostyczny | 20 |
| Kod | Poprawne przekazywanie odczytu, zapisu i błędów API; limity czasu | 15 |
| Kod | Cztery własne testy integracyjne i wcześniejsze testy | 15 |
| Dokumentacja | Kontrakt, diagram i granice odpowiedzialności | 10 |
| Dokumentacja | Powtarzalne uruchomienie, dane testowe i zatrzymanie | 10 |
| Dokumentacja | Wyniki awarii, ograniczenia i wykorzystane źródła | 10 |
| Dokumentacja | Wkład autorów i zakres wykorzystania AI | 10 |
| **Razem** | **Kod 60 + dokumentacja 40** | **100** |

**Zaliczenie etapu:** minimum 50 punktów i spełnienie wszystkich warunków minimum:

- własny projekt zachowuje dwie usługi i funkcjonalność wcześniejszych etapów,
- gateway udostępnia co najmniej dwie jawne trasy do różnych usług przez nazwy z Eureki,
- wykazano poprawny odczyt z obu usług, zapis oraz przekazanie błędu biznesowego lub walidacji,
- bramka nie zawiera logiki domenowej ani dostępu do baz usług,
- przechodzą wcześniejsze testy i co najmniej cztery własne testy integracyjne,
- udokumentowano scenariusze awarii i przywrócenia działania,
- każda osoba potrafi wyjaśnić konfigurację i przepływ żądania.

## 9. Oznaczenie i przekazanie wersji projektu LAB4

Należy oddać to samo repozytorium co wcześniej. Przed dodaniem zmian do Git należy wykluczyć `.venv`, `target`, lokalne bazy, cache, `.env` i sekrety. Następnie należy sprawdzić zakres zmian:

```powershell
git status
git add .
git diff --cached --stat
git commit -m "feat(lab4): konfiguracja API Gateway"
git tag lab4
git push origin HEAD
git push origin refs/tags/lab4
```

Jeżeli tag `lab4` już istnieje, nie należy nadpisywać go siłą; należy uzgodnić oznaczenie poprawionej wersji. Dokumentacja musi umożliwiać odtworzenie konfiguracji bez kopiowania lokalnych środowisk i baz.

## 10. Dokumentacja techniczna

- [Spring Cloud Gateway — starter WebFlux](https://docs.spring.io/spring-cloud-gateway/reference/spring-cloud-gateway-server-webflux/starter.html) — wybór wariantu i zależności.
- [Spring Cloud Gateway — właściwości konfiguracji](https://docs.spring.io/spring-cloud-gateway/reference/appendix.html) — prefiks `server.webflux`, trasy i limity połączenia.
- [StripPrefix](https://docs.spring.io/spring-cloud-gateway/reference/spring-cloud-gateway-server-webflux/gatewayfilter-factories/stripprefix-factory.html) — usuwanie segmentów ścieżki.
- [ReactiveLoadBalancerClientFilter](https://docs.spring.io/spring-cloud-gateway/reference/spring-cloud-gateway-server-webflux/global-filters.html) — wybór instancji dla `lb://` i zachowanie przy braku instancji.
- [Spring Cloud Netflix](https://docs.spring.io/spring-cloud-netflix/reference/spring-cloud-netflix.html) — konfiguracja klienta Eureka.
- [HTTPX — QuickStart](https://www.python-httpx.org/quickstart/) — żądania, JSON, kody i nagłówki odpowiedzi.

Przed zastosowaniem fragmentu dokumentacji należy sprawdzić jego wersję i wariant gateway. Należy wskazać w dokumentacji projektu nie tylko linki, lecz także sposób wykorzystania i sprawdzenia rozwiązania.
