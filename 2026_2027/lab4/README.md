# LAB4 — Konfiguracja i uruchomienie wspólnego punktu wejścia (API Gateway)

## Projektowanie aplikacji webowych opartych o mikrousługi

- **Czas:** 120 minut zajęć; JDK 21, Maven 3.9.x oraz zależności z LAB3 należy przygotować przed zajęciami
- **Technologia:** Spring Cloud Gateway (Server WebFlux), Eureka Server oraz dwie mikrousługi Python + FastAPI (z SQLite i Redis z LAB2 oraz klientem Eureki z LAB3)
- **Forma:** praca indywidualna lub w parach, w dotychczasowym repozytorium projektu z LAB1–LAB3
- **Rezultat:** działająca bramka API Gateway udostępniająca wspólny punkt wejścia dla dwóch usług odnajdywanych w Eurece po nazwie logicznej, zestaw testów integracyjnych oraz zaktualizowana dokumentacja

---

## 1. Cel i zakres laboratorium

W tym ćwiczeniu należy zrealizować czwarty temat laboratoryjny z sylabusa: **„Konfiguracja i uruchomienie API Gateway”**, rozwijając system budowany w LAB1, LAB2 i LAB3. Do działających już komponentów — dwóch mikrousług domenowych, warstwy trwałości i cache oraz rejestru Eureka — należy dołączyć bramkę HTTP jako wspólny punkt wejścia klienta, skonfigurować jawne trasy routingu i zweryfikować zachowanie całego układu podczas poprawnej pracy oraz w sytuacjach awaryjnych.

Po wykonaniu laboratorium należy umieć:

- odróżnić odpowiedzialność API Gateway, wzorca BFF (Backend for Frontend), rejestru usług Eureka oraz mikrousług domenowych,
- zaprojektować publiczny kontrakt wejściowy (`/api/...`) i przypisać trasy do właściwych usług bez przenoszenia logiki biznesowej do bramki,
- skonfigurować trasy, warunki dopasowania (`predicates`), filtry przekształcające ścieżkę (`StripPrefix`) oraz nagłówki diagnostyczne (`AddResponseHeader`),
- przekazywać żądania z bramki do usług odnajdywanych dynamicznie w rejestrze Eureka za pomocą schematu `lb://NAZWA-USŁUGI`,
- wykazać współdziałanie wszystkich dotychczasowych warstw systemu: walidacji i reguł biznesowych (LAB1), bazy SQLite i cache Redis z nagłówkiem `X-Cache` (LAB2), wywołania usługa–usługa (LAB3) oraz routingu bramki z nagłówkiem `X-Gateway` (LAB4),
- odróżnić brak trasy w bramce (`404`), brak zasobu w usłudze (`404`), błąd walidacji lub konflikt biznesowy (`422` / `409`), błąd zależności między usługami (`502` / `503`) oraz błąd połączenia lub przekroczenia czasu w bramce (`503` / `504` / `500`),
- przygotować powtarzalne testy integracyjne weryfikujące przepływ żądań przez bramkę.

### Powiązanie z efektami kształcenia

| Efekt | Ćwiczone działanie na LAB4 | Dowód wykonania |
|---|---|---|
| EK_04 — projektowanie systemu z kilku mikrousług i skomunikowanie komponentów (brama, rejestr, mikrousługi) | Połączenie bramki API Gateway, rejestru Eureka i dwóch usług domenowych w jeden spójny przepływ komunikacyjny | Działający układ czterech procesów (plus Redis dla usługi z LAB2), diagram architektury i tabela tras |
| EK_03 — implementacja funkcjonalności z wykorzystaniem dokumentacji | Konfiguracja tras, filtrów, klienta rejestru i limitów czasu oraz implementacja testów integracyjnych | Plik `application.yml`, przechodzące testy i opis co najmniej dwóch wykorzystanych źródeł dokumentacji |
| EK_01 — rozumienie pojęć architektury mikrousługowej | Rozróżnienie routingu brzegowego, service discovery, komunikacji wewnętrznej i wzorca BFF | Poprawne wyjaśnienie przepływu żądania oraz granic odpowiedzialności komponentów |
| EK_02 — dobór i wykorzystanie narzędzi | Uruchomienie i integracja Spring Cloud Gateway, Eureka, FastAPI, SQLite, Redis oraz HTTPX | Powtarzalna instrukcja uruchomienia środowiska i weryfikacji przez HTTP |
| EK_05 — analiza wyzwań, jakości i ograniczeń rozwiązania | Badanie skutków zatrzymania usługi, zatrzymania bramki, opóźnień odświeżania rejestru i błędnej transformacji ścieżki | Udokumentowane wyniki eksperymentów awarii oraz wnioski techniczne |

---

## 2. Zachowanie ciągłości projektu z LAB1–LAB3

Pracę należy kontynuować we własnym temacie domenowym i w tym samym repozytorium Git, które było rozwijane na poprzednich zajęciach. Przed wprowadzeniem zmian należy uruchomić dotychczasowe testy z LAB1–LAB3 oraz upewnić się, że bieżący stan projektu jest zapisany w historii Git. Nie należy zastępować własnego projektu przykładem paczkomatów.

### Zestawienie ewolucji systemu w LAB1–LAB4

| Etap | Dotychczasowy rezultat w projekcie | Rola i zachowanie na etapie LAB4 |
|---|---|---|
| **LAB1** | Pierwsza mikrousługa (`create_app()`), model Pydantic, `/health`, odczyt listy i szczegółów, zapis, walidacja (`422`), reguła biznesowa (`409`) i obsługa braku zasobu (`404`) | Endpointy domenowe pierwszej usługi stają się dostępne przez trasę bramki; walidacja i reguła biznesowa nadal są egzekwowane w usłudze, a kody `404`, `409`, `422` przechodzą przez bramkę bez zmian |
| **LAB2** | Trwała baza SQLite (SQLAlchemy) oraz wzorzec cache-aside w Redis (`JsonCache`, `TTL`, unieważnianie po zapisie, nagłówek `X-Cache: MISS/HIT/BYPASS`) | Baza danych i Redis pozostają prywatnymi zasobami pierwszej usługi; przy odczycie przez bramkę odpowiedź zawiera zarówno nagłówek `X-Cache` z usługi, jak i `X-Gateway` z bramki, a zapis przez bramkę unieważnia klucz w cache |
| **LAB3** | Druga usługa domenowa, rejestracja obu usług w Eureka Server (`:8761`), wywołanie HTTP usługa–usługa po nazwie logicznej (`do_service()`) i mapowanie błędów zależności (`404`, `502`, `503`) | Obie usługi nadal rejestrują się w Eurece; bramka pobiera z Eureki listę instancji obu usług, natomiast wewnętrzne wywołanie usługa–usługa z LAB3 pozostaje bezpośrednie |
| **LAB4** | Brak wspólnego punktu wejścia — klient musiał znać porty poszczególnych usług (`8101`, `8102`) | Dodanie komponentu `gateway` (`:8080`), który przyjmuje żądania klienta pod wspólnym prefiksem `/api/...`, przekształca ścieżkę i kieruje ruch do właściwej usługi przez `lb://NAZWA-USŁUGI` |

API Gateway jest komponentem infrastruktury brzegowej i **nie zastępuje wymaganej mikrousługi domenowej**. Zgodnie z sylabusem każda osoba realizująca projekt musi zaimplementować co najmniej dwie różne mikrousługi oraz pozostałe wymagane komponenty systemu. Podczas pracy w parze należy dokumentować indywidualny wkład autorów oraz zmieniać role osoby konfigurującej i osoby weryfikującej działanie systemu.

### Organizacja pracy na zajęciach i po zajęciach

Proponowany podział 120 minut zajęć:

- **15 minut** — omówienie roli API Gateway, porównanie z Eureką i BFF oraz analiza przepływu żądania,
- **20 minut** — uruchomienie i zbadanie wspólnego przykładu (`lab3-support` + `lab4-support`),
- **15 minut** — zaprojektowanie tabeli tras i kontraktu wejściowego dla własnej domeny,
- **35 minut** — włączenie bramki do własnego repozytorium i konfiguracja tras do obu usług,
- **25 minut** — weryfikacja odczytu, zapisu, cache, reguły biznesowej oraz scenariuszy awarii,
- **10 minut** — prezentacja punktu kontrolnego i odbiór na zajęciach.

**Punkt kontrolny na koniec zajęć:** działająca bramka we własnym projekcie, przekazująca żądania przez nazwy z Eureki do co najmniej dwóch tras (po jednej dla każdej usługi). Dokończenie czterech testów integracyjnych oraz pełnej dokumentacji można wykonać po zajęciach przed terminem oddania etapu.

---

## 3. Rozróżnienie roli bramki, rejestru usług i mikrousług

### Punkt wejścia klienta a komunikacja wewnętrzna

W LAB3 zewnętrzny klient HTTP musiał znać dokładny adres i port każdej mikrousługi (np. `http://127.0.0.1:8101` dla pierwszej usługi oraz `http://127.0.0.1:8102` dla drugiej). Wprowadzenie **API Gateway** zapewnia klientowi jeden spójny adres wejściowy, np. `http://127.0.0.1:8080/api/...`. Bramka analizuje przychodzące żądanie, dopasowuje trasę, opcjonalnie modyfikuje ścieżkę lub nagłówki i przekazuje żądanie do odpowiedniej usługi domenowej, a następnie zwraca odpowiedź klientowi.

| Komponent | Główna odpowiedzialność w systemie | Czego nie należy w nim umieszczać |
|---|---|---|
| **Eureka Server** | Przechowywanie rejestru instancji usług (nazwa logiczna, adres IP, port, status dzierżawy) | Danych domenowych, logiki biznesowej ani pośredniczenia w przesyłaniu żądań HTTP klienta |
| **API Gateway** | Jeden punkt wejścia dla klienta, dopasowanie trasy (`Predicate`), przekształcenie ścieżki (`Filter`), wybór instancji z rejestru (`lb://`) i przekazanie żądania HTTP | Reguł biznesowych domeny (np. sprawdzania wolnych skrytek lub nakładania się rezerwacji), tabel bazodanowych usług ani bezpośrednich połączeń z SQLite/Redis usług |
| **BFF (Backend for Frontend)** | Odmiana warstwy pośredniej dostosowana do potrzeb konkretnego typu interfejsu (np. osobne API dla aplikacji mobilnej i osobne dla panelu webowego) | Logiki właściciela danych domenowych; w tym laboratorium należy skonfigurować jedną wspólną bramkę API Gateway, a nie osobne usługi BFF |
| **Mikrousługa domenowa** | Realizacja logiki biznesowej w granicach własnego kontekstu (DDD), walidacja danych, trwały zapis we własnej bazie i obsługa własnego cache | Bezpośredniego dostępu do bazy danych innej usługi ani przejmowania odpowiedzialności innych kontekstów domenowych |

### Przepływ żądań i komunikacji w architekturze z LAB1–LAB4

Poniższy diagram przedstawia pełny układ procesów łączący elementy z LAB2 (baza danych i cache), LAB3 (Eureka i dwie usługi) oraz LAB4 (API Gateway):

<pre class="mermaid">
flowchart LR
    K["Klient HTTP"] -->|"GET /api/lockers/KRK-1024<br/>GET /api/delivery-check/KRK-1024"| G["API Gateway :8080"]
    G -->|"/lockers/..."| L["Usługa 1 (Locker Service) :8101"]
    G -->|"/delivery-check/..."| P["Usługa 2 (Parcel Service) :8102"]
    P -->|"Bezpośrednie HTTP z LAB3<br/>GET /lockers/KRK-1024"| L
    L --> DB[("SQLite (LAB2)<br/>źródło prawdy")]
    L <--> R[("Redis (LAB2)<br/>cache-aside")]
    G -.->|"Pobieranie rejestru (fetch-registry)"| E["Eureka Server :8761"]
    P -.->|"Rejestracja, heartbeat,<br/>pobieranie rejestru"| E
    L -.->|"Rejestracja i heartbeat"| E
</pre>

Linie ciągłe oznaczają wywołania przesyłające dane domenowe i operacje biznesowe, natomiast linie przerywane oznaczają ruch administracyjny związany z rejestrem usług. Należy zwrócić uwagę na trzy zasady architektoniczne:

1. **Lokalna kopia rejestru:** Bramka, podobnie jak klient `py-eureka-client` z LAB3, pobiera i okresowo odświeża lokalną kopię rejestru z Eureki. Nie wysyła osobnego zapytania do Eureki przed każdym żądaniem HTTP klienta.
2. **Bezpośrednia komunikacja wewnętrzna:** Istniejącego wywołania usługa–usługa z LAB3 (`Usługa 2 -> Usługa 1`) nie należy kierować z powrotem przez API Gateway. Bramka obsługuje ruch wejściowy od klienta zewnętrznego, a usługi komunikują się wewnątrz systemu bezpośrednio po adresach pobranych z Eureki. Skierowanie ruchu wewnętrznego przez bramkę dodałoby zbędny przeskok sieciowy i uzależniło komunikację wewnętrzną od dostępności procesu bramki.
3. **Niezależność warstwy danych:** Baza SQLite oraz serwer Redis skonfigurowane w LAB2 należą wyłącznie do usługi domenowej. Bramka nie łączy się z bazą danych ani z Redisem.

### Konfiguracja trasy, warunków dopasowania i filtrów (Spring Cloud Gateway)

W Spring Cloud Gateway pojedyncza **trasa (`route`)** składa się z unikatowego identyfikatora (`id`), docelowego adresu (`uri`), listy warunków dopasowania (`predicates`) oraz listy filtrów (`filters`):

| Element konfiguracji | Przykład w `application.yml` | Znaczenie techniczne |
|---|---|---|
| `id` | `lockers` | Wewnętrzny identyfikator trasy w konfiguracji bramki (nie musi być identyczny z nazwą usługi w Eurece) |
| `uri` | `lb://LOCKER-SERVICE` | Wskazanie usługi docelowej przez nazwę logiczną zarejestrowaną w Eurece z użyciem klienta LoadBalancer (`lb`) |
| `predicates` (`Path`) | `Path=/api/lockers,/api/lockers/**` | Warunek wyboru trasy: żądanie zostanie dopasowane, gdy ścieżka jest równa `/api/lockers` lub zaczyna się od `/api/lockers/` |
| `filters` (`StripPrefix`) | `StripPrefix=1` | Usunięcie pierwszego segmentu ścieżki (`/api`) przed wysłaniem żądania do usługi docelowej (`/api/lockers/KRK-1024` → `/lockers/KRK-1024`) |
| `default-filters` | `AddResponseHeader=X-Gateway, lab4` | Filtr domyślny dołączający nagłówek `X-Gateway: lab4` do odpowiedzi przechodzących przez zdefiniowane trasy |

Schemat `lb://` uruchamia mechanizm `ReactiveLoadBalancerClientFilter`, który tłumaczy nazwę usługi (np. `LOCKER-SERVICE`) na konkretny adres IP i port aktywnej instancji pobranej z Eureki. Użycie `lb://` działa poprawnie również wtedy, gdy w systemie uruchomiona jest tylko jedna instancja danej usługi — należy jednak pamiętać, że pojedyncza instancja nie zapewnia redundancji w razie zatrzymania procesu.

### Ocena korzyści, kosztów i ograniczeń bramki

Wprowadzenie API Gateway porządkuje kontrakt zewnętrzny systemu: klient korzysta z jednego adresu i spójnej przestrzeni ścieżek `/api/...`, a wewnętrzny podział na usługi oraz ich porty pozostają ukryte za bramką. Pozwala to również jawnie zdecydować, które endpointy są udostępniane na zewnątrz, a które (np. techniczne endpointy `/health` poszczególnych usług) pozostają wyłącznie wewnętrzne.

Rozwiązanie to wiąże się jednak z kosztami inżynierskimi:

- dochodzi kolejny proces wymagający konfiguracji, uruchomienia i monitorowania,
- każde żądanie klienta pokonuje dodatkowy przeskok sieciowy (`Klient -> Gateway -> Usługa`),
- pojedyncza instancja bramki stanowi pojedynczy punkt awarii (*Single Point of Failure*) dla ruchu przychodzącego przez port `8080`,
- sama obecność bramki nie blokuje dostępu do lokalnych portów usług (`8101`, `8102`), nie uwierzytelnia użytkowników i nie szyfruje ruchu.

W ramach laboratorium wszystkie komponenty należy uruchamiać wyłącznie lokalnie na adresie `127.0.0.1` (`localhost`). Nie należy wystawiać portów na zewnętrzne interfejsy sieciowe ani otwierać ruchu w zaporze systemowej.

---

## 4. Część A — uruchomienie i analiza przykładu wspólnego

W pierwszej części należy uruchomić wspólny przykład łączący rejestr Eureka oraz dwie usługi demonstracyjne z LAB3 z bramką zawartą w pakiecie pomocniczym LAB4.

### Krok 1. Pobranie pakietu pomocniczego i weryfikacja narzędzi (JDK / Maven)

Należy pobrać [pakiet pomocniczy LAB4 — ZIP]({{ '/2026_2027/lab4/lab4-support.zip' | relative_url }}) i rozpakować go obok własnego projektu oraz obok katalogu `lab3-support` z [poprzedniego laboratorium]({{ '/2026_2027/lab3/' | relative_url }}).

Struktura pakietu `lab4-support`:

```text
lab4-support/
├── gateway/
│   ├── pom.xml
│   └── src/main/
│       ├── java/pl/ur/pawoom/lab4/GatewayApplication.java
│       └── resources/application.yml
├── tests/
│   └── test_gateway_demo.py
├── requirements.txt
├── README-LAB4-template.md
├── README.md
└── .gitignore
```

Do wykonania ćwiczenia wymagane są:

- **Python 3.12 lub nowszy** (do uruchomienia usług FastAPI oraz testów integracyjnych w `pytest`),
- **JDK 21** oraz **Apache Maven 3.9.x** (do zbudowania i uruchomienia bramki Spring Cloud Gateway),
- działający **Eureka Server** z pakietu `lab3-support` (uruchamiany przez Docker Compose albo przez Maven).

W terminalu PowerShell należy zweryfikować dostępność i wersje narzędzi:

```powershell
python --version
java -version
mvn -version
```

Polecenie `mvn -version` powinno wskazywać Javę w wersji 21. Jeżeli polecenie `mvn` lub `java` nie jest rozpoznawane, należy skonfigurować zmienne środowiskowe `JAVA_HOME` (wskazującą katalog główny JDK 21) oraz `PATH` (zawierającą wpisy `%JAVA_HOME%\bin` oraz katalog `bin` rozpakowanego Apache Maven). Nie należy przepisywać usług Python z LAB1–LAB3 na język Java — w architekturze mikrousługowej komponenty infrastruktury i poszczególne usługi mogą korzystać z różnych technologii, komunikując się przez HTTP i wspólny rejestr.

### Krok 2. Uruchomienie rejestru Eureka i dwóch usług demonstracyjnych z LAB3 (FastAPI / Eureka)

Przed uruchomieniem bramki należy uruchomić środowisko demonstracyjne z pakietu `lab3-support`. Na czas części demonstracyjnej należy zatrzymać własne usługi, jeśli nasłuchują na portach `8101` lub `8102`. Każdy proces należy uruchomić w osobnym oknie terminala.

1. **Terminal 1 — uruchomienie Eureka Server (w katalogu `lab3-support`):**
   Należy wybrać wariant używany w LAB3 — Docker Compose:
   ```powershell
   Set-Location .\lab3-support
   docker compose up -d eureka
   ```
   albo uruchomienie bezpośrednie przez Maven (bez Dockera):
   ```powershell
   Set-Location .\lab3-support\eureka-server
   mvn spring-boot:run
   ```
   Następnie należy upewnić się, że panel pod adresem `http://127.0.0.1:8761/` odpowiada.

2. **Terminal 2 — uruchomienie `LOCKER-SERVICE` na porcie `8101` (w katalogu `lab3-support`):**
   ```powershell
   $env:EUREKA_SERVER_URL = 'http://127.0.0.1:8761'
   $env:SERVICE_NAME = 'LOCKER-SERVICE'
   $env:SERVICE_PORT = '8101'
   .\.venv\Scripts\python.exe -m uvicorn demo.locker_service.app.main:app --port 8101
   ```

3. **Terminal 3 — uruchomienie `PARCEL-SERVICE` na porcie `8102` (w katalogu `lab3-support`):**
   ```powershell
   $env:EUREKA_SERVER_URL = 'http://127.0.0.1:8761'
   $env:SERVICE_NAME = 'PARCEL-SERVICE'
   $env:SERVICE_PORT = '8102'
   .\.venv\Scripts\python.exe -m uvicorn demo.parcel_service.app.main:app --port 8102
   ```

4. **Weryfikacja stanu z LAB3 przed włączeniem bramki:**
   Po pojawieniu się obu usług (`LOCKER-SERVICE` oraz `PARCEL-SERVICE`) ze statusem `UP` w panelu Eureki, w kolejnym terminalu należy sprawdzić bezpośrednie wywołania:
   ```powershell
   curl.exe -i http://127.0.0.1:8101/lockers/KRK-1024
   curl.exe -i http://127.0.0.1:8102/delivery-check/KRK-1024
   ```
   Oba żądania muszą zwrócić kod `200 OK` oraz dane paczkomatu `KRK-1024`. Jeżeli komunikacja z LAB3 nie działa, należy naprawić ją przed przejściem do konfiguracji bramki — API Gateway nie zastępuje rejestracji w Eurece ani wywołania między usługami.

### Krok 3. Analiza kodu i konfiguracji bramki (Spring Cloud Gateway)

Należy otworzyć i przeanalizować trzy pliki znajdujące się w katalogu `lab4-support/gateway`:

1. **Klasa startowa `src/main/java/pl/ur/pawoom/lab4/GatewayApplication.java`:**
   ```java
   @SpringBootApplication
   @RestController
   public class GatewayApplication {
       public static void main(String[] args) {
           SpringApplication.run(GatewayApplication.class, args);
       }

       @GetMapping("/health")
       public Map<String, String> health() {
           return Map.of("status", "ok", "service", "API-GATEWAY");
       }
   }
   ```
   Klasa uruchamia serwer reaktywny Spring Boot i wystawia lokalny endpoint kontrolny `GET /health` samego procesu bramki. Nie zawiera żadnego kodu domenowego.

2. **Zależności w `pom.xml`:**
   Projekt wykorzystuje trzy główne startery:
   - `spring-cloud-starter-gateway-server-webflux` — reaktywny serwer bramki API,
   - `spring-cloud-starter-netflix-eureka-client` — klient pobierający rejestr instancji z serwera Eureka,
   - `spring-cloud-starter-loadbalancer` — komponent tłumaczący adresy `lb://NAZWA-USŁUGI` na konkretne instancje z rejestru.

3. **Konfiguracja w `src/main/resources/application.yml`:**
   ```yaml
   server:
     address: 127.0.0.1
     port: ${GATEWAY_PORT:8080}

   spring:
     application:
       name: api-gateway
     cloud:
       gateway:
         server:
           webflux:
             discovery:
               locator:
                 enabled: false
             httpclient:
               connect-timeout: 1000
               response-timeout: 5s
             default-filters:
               - AddResponseHeader=X-Gateway, lab4
             routes:
               - id: lockers
                 uri: lb://LOCKER-SERVICE
                 predicates:
                   - Path=/api/lockers,/api/lockers/**
                 filters:
                   - StripPrefix=1
               - id: delivery-check
                 uri: lb://PARCEL-SERVICE
                 predicates:
                   - Path=/api/delivery-check,/api/delivery-check/**
                 filters:
                   - StripPrefix=1

   eureka:
     client:
       register-with-eureka: false
       fetch-registry: true
       service-url:
         defaultZone: ${GATEWAY_EUREKA_URL:http://127.0.0.1:8761/eureka/}
   ```

Podczas analizy pliku `application.yml` należy zwrócić uwagę na następujące ustawienia:

- `register-with-eureka: false` oraz `fetch-registry: true` — bramka jest wyłącznie odbiorcą rejestru (pobiera listę instancji usług docelowych), natomiast sama nie rejestruje się jako usługa w Eurece; dlatego brak wpisu `API-GATEWAY` w tabeli instancji panelu `8761` jest zachowaniem prawidłowym,
- `defaultZone` — w kliencie Spring Cloud adres serwera Eureka wymaga jawnego sufiksu `/eureka/` (`http://127.0.0.1:8761/eureka/`), w przeciwieństwie do zmiennej `EUREKA_SERVER_URL` z LAB3, gdzie sufiks `/eureka` był dodawany przez parametr `eureka_context`,
- `discovery.locator.enabled: false` — wyłącza automatyczne generowanie tras dla wszystkich usług widocznych w rejestrze; na zewnętrznym interfejsie bramki udostępniane są wyłącznie jawnie zadeklarowane trasy z sekcji `routes`,
- `connect-timeout: 1000` oraz `response-timeout: 5s` — ograniczają czas nawiązania połączenia TCP (1000 ms) oraz czas oczekiwania na odpowiedź HTTP od wybranej instancji (5 sekund); warto zauważyć, że dla trasy `delivery-check` limit `5s` w bramce jest dłuższy niż limit `timeout=3` w wywołaniu `PARCEL-SERVICE -> LOCKER-SERVICE` z LAB3, dzięki czemu `PARCEL-SERVICE` zdąży zwrócić kontrolowany kod `503` przed przerwaniem połączenia przez bramkę,
- `default-filters` (`AddResponseHeader=X-Gateway, lab4`) — dołącza nagłówek `X-Gateway: lab4` do każdej odpowiedzi przechodzącej przez zdefiniowaną trasę, co pozwala odróżnić odpowiedź obsłużoną przez trasę bramki od wywołania bezpośredniego lub błędu braku trasy.

### Krok 4. Uruchomienie bramki i weryfikacja tras (Maven / curl.exe)

W nowym terminalu należy przejść do katalogu `lab4-support/gateway` i uruchomić bramkę:

```powershell
Set-Location .\lab4-support\gateway
mvn spring-boot:run
```

Po wyświetleniu w logu informacji o uruchomieniu serwera na porcie `8080`, w osobnym terminalu należy wykonać trzy zapytania weryfikujące:

```powershell
curl.exe -i http://127.0.0.1:8080/health
curl.exe -i http://127.0.0.1:8080/api/lockers/KRK-1024
curl.exe -i http://127.0.0.1:8080/api/delivery-check/KRK-1024
```

Należy zaobserwować i porównać odpowiedzi:

| Żądanie klienta do bramki (`:8080`) | Dopasowana trasa (`id`) | Usługa docelowa z Eureki | Ścieżka otrzymana przez usługę po `StripPrefix=1` | Nagłówek `X-Gateway` |
|---|---|---|---|---|
| `GET /health` | Brak (endpoint własny bramki) | Brak (`GatewayApplication`) | `/health` | Brak |
| `GET /api/lockers/KRK-1024` | `lockers` | `LOCKER-SERVICE` (`:8101`) | `/lockers/KRK-1024` | `lab4` |
| `GET /api/delivery-check/KRK-1024` | `delivery-check` | `PARCEL-SERVICE` (`:8102`) | `/delivery-check/KRK-1024` | `lab4` |

Przebieg trzeciego żądania (łączącego routing w bramce z wywołaniem usługa–usługa z LAB3) ilustruje poniższy diagram sekwencji:

<pre class="mermaid">
sequenceDiagram
    participant K as Klient HTTP
    participant G as API Gateway (:8080)
    participant P as Parcel Service (:8102)
    participant L as Locker Service (:8101)
    K->>G: GET /api/delivery-check/KRK-1024
    Note over G: 1. Predicate Path=/api/delivery-check/**<br/>2. Filtr StripPrefix=1<br/>3. Wybór instancji lb://PARCEL-SERVICE
    G->>P: GET /delivery-check/KRK-1024
    Note over P: Odnalezienie LOCKER-SERVICE<br/>w lokalnej kopii rejestru (LAB3)
    P->>L: GET /lockers/KRK-1024
    L-->>P: 200 OK + JSON paczkomatu
    P-->>G: 200 OK + {"destination": "KRK-1024", "locker": {...}}
    Note over G: Dołączenie nagłówka X-Gateway: lab4
    G-->>K: 200 OK + JSON + X-Gateway: lab4
</pre>

### Krok 5. Rozróżnienie źródeł błędu 404 i eksperyment z filtrem ścieżki

W terminalu należy wykonać dwa zapytania kończące się kodem `404 Not Found`:

```powershell
curl.exe -i http://127.0.0.1:8080/api/lockers/UNKNOWN
curl.exe -i http://127.0.0.1:8080/not-a-route
```

Następnie należy wykonać eksperyment z filtrem `StripPrefix`:

1. Przed edycją pliku należy zapisać przewidywanie: jaka ścieżka trafi do `LOCKER-SERVICE` dla żądania `GET /api/lockers/KRK-1024`, gdy w trasie `lockers` filtr zostanie zmieniony ze `StripPrefix=1` na `StripPrefix=2`?
2. W pliku `gateway/src/main/resources/application.yml` należy zmienić w trasie `lockers` wartość na `StripPrefix=2`, zrestartować proces bramki (`Ctrl+C` i ponownie `mvn spring-boot:run`) oraz wywołać `curl.exe -i http://127.0.0.1:8080/api/lockers/KRK-1024`.
3. Należy sprawdzić log terminala `LOCKER-SERVICE` (Uvicorn), aby odczytać dokładną ścieżkę HTTP, która dotarła do usługi.
4. Po zakończeniu obserwacji należy przywrócić `StripPrefix=1` i ponownie uruchomić bramkę.

Porównanie trzech przypadków kodu `404`:

| Wywołanie i konfiguracja | Gdzie powstaje `404`? | Ścieżka w logu Uvicorna | Treść odpowiedzi (`body`) | Obecność `X-Gateway: lab4` |
|---|---|---|---|---|
| `GET /api/lockers/UNKNOWN` (`StripPrefix=1`) | W kodzie endpointu `LOCKER-SERVICE` (brak rekordu w danych domenowych) | `GET /lockers/UNKNOWN` | `{"detail":"Locker not found"}` | Tak (odpowiedź przeszła przez trasę) |
| `GET /not-a-route` (`StripPrefix=1`) | W bramce `API Gateway` (żadna trasa nie pasuje do `Path`) | Brak wpisu (żądanie nie opuściło bramki) | Domyślny JSON błędu Spring WebFlux | Nie (żadna trasa nie została uruchomiona) |
| `GET /api/lockers/KRK-1024` (`StripPrefix=2`) | W routerze FastAPI `LOCKER-SERVICE` (błędna ścieżka po ucięciu dwóch segmentów `/api` i `/lockers`) | `GET /KRK-1024` | `{"detail":"Not Found"}` | Tak (żądanie przeszło przez trasę zepsutą filtrem) |

Sam kod statusu HTTP `404` nie rozstrzyga więc, który komponent wygenerował odpowiedź i z jakiej przyczyny — należy zawsze zestawiać status z treścią odpowiedzi, nagłówkami oraz logami dostępowymi usług.

### Krok 6. Uruchomienie testów integracyjnych przykładu (pytest / HTTPX)

Przy działających czterech procesach (Eureka Server, `LOCKER-SERVICE`, `PARCEL-SERVICE`, `API Gateway`), w nowym terminalu otwartym w katalogu `lab4-support` należy utworzyć środowisko wirtualne i uruchomić zestaw testów:

```powershell
Set-Location .\lab4-support
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

Oczekiwany wynik to `5 passed`. Testy w pliku `tests/test_gateway_demo.py` są **testami integracyjnymi**: nie używają `TestClient` ani atrap `FakeEurekaClient`, lecz wysyłają prawdziwe żądania HTTP przez bibliotekę `httpx` na port `8080` bramki.

---

## 5. Część B — zaprojektowanie kontraktu wejściowego dla własnego projektu

Po przeanalizowaniu przykładu należy zatrzymać procesy demonstracyjne (`LOCKER-SERVICE`, `PARCEL-SERVICE` oraz bramkę z `lab4-support`), pozostawiając uruchomiony serwer Eureka oraz serwer Redis (wymagany przez pierwszą usługę z LAB2). Następnie należy przejść do własnego projektu rozwijanego w LAB1–LAB3.

### Krok 1. Wyznaczenie tras i granic API wejściowego

Dla dwóch własnych usług z LAB3 należy zaprojektować przestrzeń ścieżek wspólnego punktu wejścia i uzupełnić poniższą tabelę w dokumentacji projektu (poniższy wiersz z `ROOM-SERVICE` jest wyłącznie przykładem formatu zapisu):

| Metoda i ścieżka zewnętrzna (w bramce `:8080`) | Identyfikator trasy (`id`) | Usługa docelowa w Eurece (`uri`) | Ścieżka wewnętrzna po `StripPrefix=1` | Rola operacji i właściciel danych |
|---|---|---|---|---|
| *Przykład:* `GET /api/rooms/{id}` | `rooms` | `lb://ROOM-SERVICE` | `/rooms/{id}` | Odczyt sali z bazy SQLite / cache Redis (właściciel: pierwsza usługa z LAB1–LAB2) |
| Własny odczyt z pierwszej usługi | | | | |
| Własny zapis/modyfikacja w pierwszej usłudze | | | | |
| Własny odczyt z drugiej usługi (w tym przepływ z LAB3) | | | | |

Projektując trasy, należy pisemnie odpowiedzieć na pięć pytań projektowych:

1. Które endpointy pierwszej i drugiej usługi powinny być dostępne dla zewnętrznego klienta przez prefiks `/api/...`, a które pełnią wyłącznie funkcję techniczną (np. `/health`, `/ready` z LAB2, `/docs`) i pozostaną nieudostępnione w bramce?
2. Jaka dokładnie ścieżka dotrze do każdego endpointu w FastAPI po zastosowaniu filtra `StripPrefix=1`?
3. Która usługa pozostaje jedynym właścicielem zapisu do bazy danych SQLite i unieważniania kluczy w Redis (z LAB2), oraz w którym komponencie sprawdzana jest reguła biznesowa (z LAB1)?
4. Dlaczego wywołanie między drugą a pierwszą usługą (zrealizowane w LAB3 przez `do_service()`) nadal powinno odbywać się bezpośrednio pomiędzy usługami, a nie przez port `8080` bramki?
5. Które trasy bramki przestaną działać po zatrzymaniu pierwszej usługi, a które po zatrzymaniu drugiej usługi (z uwzględnieniem zależności z LAB3)?

W ramach DDD (*Domain-Driven Design*) wspólny prefiks `/api` w bramce stanowi wyłącznie warstwę routingu technicznego — nie łączy modeli domenowych obu usług we wspólny model ani nie uprawnia do współdzielenia bazy danych.

---

## 6. Integracja API Gateway z własnym projektem z LAB1–LAB3

### Krok 1. Dodanie komponentu bramki do repozytorium i konfiguracja tras (Spring Cloud Gateway)

Katalog `gateway` z pakietu pomocniczego (bez katalogu roboczego `target/`) należy skopiować do głównego katalogu własnego repozytorium projektu. Do głównego pliku `.gitignore` repozytorium należy dopisać `gateway/target/`.

Przykładowa organizacja repozytorium rozwijanego od LAB1 do LAB4:

```text
my-microservices-project/
├── service-a/                  # Pierwsza usługa (LAB1 + baza SQLite i Redis z LAB2 + Eureka z LAB3)
│   ├── app/
│   │   ├── main.py             # create_app(database_url, redis_client, eureka_client)
│   │   ├── models.py           # Modele Pydantic i walidacja (LAB1)
│   │   ├── db_models.py        # Tabele SQLAlchemy (LAB2)
│   │   ├── database.py         # Silnik i sesje SQLite (LAB2)
│   │   ├── repository.py       # Operacje w transakcji i reguła biznesowa (LAB1–LAB2)
│   │   └── cache.py            # Obsługa Redis cache-aside i X-Cache (LAB2)
│   ├── tests/                  # Testy jednostkowe i komponentowe z LAB1–LAB3
│   └── requirements.txt
├── service-b/                  # Druga usługa (LAB3: własny endpoint + wywołanie service-a przez Eurekę)
│   ├── app/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── gateway/                    # Komponent dodawany w LAB4 (Spring Cloud Gateway)
│   ├── pom.xml
│   └── src/main/
│       ├── java/pl/ur/pawoom/lab4/GatewayApplication.java
│       └── resources/application.yml
├── tests/
│   └── integration/            # Testy integracyjne przechodzące przez API Gateway (LAB4)
│       └── test_gateway_integration.py
├── .gitignore
└── README.md                   # Dokumentacja rozwijana od LAB1 do LAB4
```

Jeżeli w repozytorium z LAB3 przyjęto nieco inny układ katalogów dla pierwszej i drugiej usługi, należy go zachować i dołączyć na najwyższym poziomie katalog `gateway/` oraz katalog testów integracyjnych.

W pliku `gateway/src/main/resources/application.yml` należy zastąpić trasy demonstracyjne (`lockers`, `delivery-check`) własnymi trasami, zachowując poniższe wymagania:

- należy zdefiniować **co najmniej dwie jawne trasy domenowe** — minimum po jednej prowadzącej do każdej z dwóch własnych usług,
- w polu `uri` każdej trasy należy użyć schematu `lb://NAZWA-USŁUGI` zgodnego z nazwą zgłaszaną przez daną usługę do Eureki (np. `lb://ROOM-SERVICE` oraz `lb://RESERVATION-SERVICE`),
- nie wolno wpisywać w `uri` sztywnych adresów ani portów instancji (np. `http://127.0.0.1:8101`),
- należy utrzymać `discovery.locator.enabled: false` (brak automatycznego wystawiania wszystkich usług),
- należy zachować filtr `StripPrefix=1` (lub odpowiednią liczbę segmentów dopasowaną do zaprojektowanego prefiksu), domyślny filtr `AddResponseHeader=X-Gateway, lab4` oraz jawne limity czasu `connect-timeout` i `response-timeout`.

Przykład konfiguracji sekcji `routes` dla przykładowej domeny rezerwacji sal:

```yaml
          routes:
            - id: rooms
              uri: lb://ROOM-SERVICE
              predicates:
                - Path=/api/rooms,/api/rooms/**
              filters:
                - StripPrefix=1
            - id: reservations
              uri: lb://RESERVATION-SERVICE
              predicates:
                - Path=/api/reservations,/api/reservations/**
              filters:
                - StripPrefix=1
```

W przypadku zajętości portu `8080` na komputerze laboratoryjnym można przed uruchomieniem bramki ustawić zmienną środowiskową `$env:GATEWAY_PORT = '8088'` oraz odpowiednio uwzględnić ten port w zapytaniach `curl.exe` i zmiennej `GATEWAY_URL` dla testów.

### Krok 2. Weryfikacja spójności z LAB1, LAB2 i LAB3 przez bramkę (curl.exe / HTTPX)

Należy uruchomić pełne środowisko własnego projektu:

1. Serwer **Redis** (zgodnie z wariantem wybranym w LAB2: Docker, WSL2 lub usługa lokalna),
2. Serwer **Eureka** (`:8761`),
3. **Pierwszą usługę** z LAB1–LAB3 (np. na porcie `8101`, z podłączoną bazą SQLite, Redisem i rejestracją w Eurece),
4. **Drugą usługę** z LAB3 (np. na porcie `8102`, zarejestrowaną w Eurece i wywołującą pierwszą usługę po nazwie logicznej),
5. **API Gateway** (`:8080`, uruchomiony przez `mvn spring-boot:run` w katalogu `gateway`).

Po potwierdzeniu w panelu `http://127.0.0.1:8761/`, że obie usługi własne mają status `UP`, należy wykonać przez port bramki (`8080`) cztery powiązane ze sobą sprawdzenia weryfikujące integrację wszystkich dotychczasowych laboratoriów:

1. **Odczyt z pierwszej usługi i weryfikacja cache z LAB2 przez bramkę:**
   Należy dwukrotnie wywołać przez bramkę endpoint szczegółów zasobu pierwszej usługi, który w LAB2 został objęty wzorcem cache-aside:
   ```powershell
   curl.exe -i http://127.0.0.1:8080/api/<zasob-uslugi-1>/<id>
   curl.exe -i http://127.0.0.1:8080/api/<zasob-uslugi-1>/<id>
   ```
   W odpowiedzi na oba wywołania należy potwierdzić obecność **dwóch nagłówków diagnostycznych jednocześnie**:
   - `X-Gateway: lab4` — dodanego przez filtr bramki API Gateway (LAB4),
   - `X-Cache: MISS` (przy pierwszym odczycie) oraz `X-Cache: HIT` (przy drugim odczycie) — zwróconego przez warstwę cache-aside pierwszej usługi (LAB2) i przekazanego przez bramkę do klienta.

2. **Operacja zapisu/modyfikacji (LAB1) oraz unieważnienie cache i trwałość w bazie (LAB2) przez bramkę:**
   Należy wykonać przez bramkę operację zapisu (`POST` lub `PATCH` na `/api/<zasob-uslugi-1>...`), a bezpośrednio po niej ponowny odczyt `GET` przez bramkę. Przykładowe wywołanie z użyciem `httpx` (ścieżkę i pola JSON należy dopasować do własnego kontraktu):
   ```python
   import httpx

   with httpx.Client(base_url="http://127.0.0.1:8080", timeout=10.0, trust_env=False) as client:
       write_resp = client.patch("/api/rooms/R-101", json={"name": "Sala Laboratoryjna 101"})
       read_resp = client.get("/api/rooms/R-101")
       print(write_resp.status_code, write_resp.headers.get("x-gateway"))
       print(read_resp.status_code, read_resp.headers.get("x-cache"), read_resp.json())
   ```
   Należy potwierdzić, że:
   - operacja zapisu zwraca właściwy kod sukcesu z LAB1 (`201 Created` lub `200 OK`) oraz nagłówek `X-Gateway: lab4`,
   - zmiana została trwale zapisana w bazie SQLite pierwszej usługi, a klucz w Redis został unieważniony (kolejny `GET` przez bramkę zwraca zaktualizowane dane oraz `X-Cache: MISS`, a następny po nim — `X-Cache: HIT`).

3. **Weryfikacja walidacji (`422`) i reguły biznesowej (`409`) z LAB1 przez bramkę:**
   Należy wysłać przez bramkę żądanie naruszające walidację modelu Pydantic (oczekiwane `422 Unprocessable Entity`) oraz żądanie naruszające regułę biznesową z LAB1 (oczekiwane `409 Conflict`). Należy potwierdzić, że bramka przekazuje dokładny kod i ciało błędu z FastAPI (wraz z `X-Gateway: lab4`), a odrzucona operacja nie zmienia stanu w bazie SQLite ani w cache Redis.

4. **Weryfikacja odczytu z drugiej usługi i komunikacji usługa–usługa z LAB3 przez bramkę:**
   Należy wywołać przez bramkę endpoint drugiej usługi, który pod spodem odnajduje pierwszą usługę w Eurece i pobiera z niej dane:
   ```powershell
   curl.exe -i http://127.0.0.1:8080/api/<zasob-uslugi-2>/<id>
   ```
   Należy potwierdzić otrzymanie kodu `200 OK`, nagłówka `X-Gateway: lab4` oraz zagregowanych/powiązanych danych pochodzących z obu usług.

### Krok 3. Przeprowadzenie eksperymentów awarii i analiza kodów błędów

Należy przeprowadzić pojedynczo poniższe scenariusze awarii na własnym projekcie, zapisując w dokumentacji stan procesów, wykonane żądanie, otrzymany wynik oraz wniosek techniczny:

| Scenariusz eksperymentalny | Działanie do wykonania | Co należy sprawdzić i udokumentować |
|---|---|---|
| **1. Brak zasobu domenowego** | Wywołanie przez bramkę nieistniejącego identyfikatora zasobu przy działających wszystkich procesach | Kod `404`, treść `{"detail": "..."}` z usługi, obecność nagłówka `X-Gateway: lab4` |
| **2. Nieistniejąca trasa** | Wywołanie ścieżki niepasującej do żadnej trasy w `application.yml` (np. `GET /internal-only` lub `GET /health` usługi przez `/api/health`, jeśli nie ma takiej trasy) | Kod `404` wygenerowany w bramce, brak `X-Gateway: lab4` i brak śladu żądania w logach Uvicorna |
| **3. Zatrzymanie usługi wywołującej (Usługa 2)** | Zatrzymanie procesu drugiej usługi (`Ctrl+C`) przy działającej pierwszej usłudze, Eurece i bramce | Trasa drugiej usługi zwraca błąd w bramce (`503 Service Unavailable` lub błąd połączenia przed odświeżeniem rejestru), natomiast trasa pierwszej usługi (`/api/<zasob-1>/...`) oraz jej `/health` nadal działają poprawnie |
| **4. Zatrzymanie usługi bazowej (Usługa 1 — zależność z LAB3)** | Przywrócenie drugiej usługi, a następnie zatrzymanie pierwszej usługi (`Ctrl+C`) | Trasa pierwszej usługi przestaje działać w bramce, a endpoint drugiej usługi zależny od pierwszej zwraca kontrolowany kod `503` zaimplementowany w LAB3 (z nagłówkiem `X-Gateway: lab4`); sam `/health` drugiej usługi na jej porcie bezpośrednim nadal zwraca `200` |
| **5. Ponowne uruchomienie usługi** | Uruchomienie zatrzymanej usługi i odczekanie na rejestrację w Eurece oraz odświeżenie kopii rejestru w bramce | Powrót odpowiedzi `200 OK` na obu trasach bramki bez konieczności restartowania procesu `API Gateway`; należy zanotować przybliżony czas potrzebny na odświeżenie rejestru |
| **6. Zatrzymanie bramki (`API Gateway`)** | Zatrzymanie procesu Maven bramki (`Ctrl+C`) przy pozostawieniu obu usług i Eureki | Brak możliwości nawiązania połączenia TCP na porcie `8080` (to odmowa połączenia, a nie kod HTTP `500` lub `503`), przy jednoczesnym poprawnym działaniu bezpośrednich portów usług (`8101`, `8102`) |

#### Zestawienie kodów błędów i miejsc ich powstawania w systemie z LAB1–LAB4

| Obserwowany wynik u klienta | Miejsce powstania | Przyczyna techniczna | Obecność `X-Gateway: lab4` |
|---|---|---|---|
| `404` + `{"detail": "..."}` z domeny | Usługa FastAPI (LAB1–LAB3) | Trasa w bramce zadziałała, ale zasób o podanym ID nie istnieje w bazie usługi | Tak |
| `404` (domyślny format WebFlux) | API Gateway (LAB4) | Ścieżka żądania nie pasuje do żadnego warunku `Path` w sekcji `routes` | Nie |
| `422 Unprocessable Entity` | Usługa FastAPI (LAB1) | Niepoprawne typy lub brakujące pola w JSON przesłanym przez bramkę | Tak |
| `409 Conflict` | Usługa FastAPI (LAB1–LAB2) | Naruszenie reguły biznesowej lub unikalności klucza w usłudze | Tak |
| `502 Bad Gateway` | Druga usługa FastAPI (LAB3) | Druga usługa wywołała pierwszą przez `do_service()`, a pierwsza zwróciła nieoczekiwany błąd HTTP (np. `500`) | Tak |
| `503` + `{"detail": "..."}` z LAB3 | Druga usługa FastAPI (LAB3) | Bramka dotarła do drugiej usługi, ale druga usługa nie mogła połączyć się z pierwszą usługą | Tak |
| `503 Service Unavailable` (z WebFlux) | API Gateway — `LoadBalancer` (LAB4) | W lokalnej kopii rejestru bramki nie ma żadnej aktywnej instancji dla `lb://NAZWA-USŁUGI` | Zależnie od momentu przerwania potoku filtrów |
| `500` (Connection refused) / `504 Gateway Timeout` | API Gateway — klient HTTP (LAB4) | Wpis instancji jeszcze widnieje w kopii rejestru bramki, ale proces usługi został już zatrzymany (`500`) albo nie odpowiedział w czasie `response-timeout` (`504`) | Zależnie od momentu przerwania potoku filtrów |
| Odmowa połączenia TCP (*Connection refused*) | Warstwa sieciowa systemu operacyjnego | Proces `API Gateway` na porcie `8080` jest wyłączony (klient nie otrzymuje żadnej odpowiedzi HTTP) | Brak odpowiedzi HTTP |

### Krok 4. Implementacja testów integracyjnych wspólnego wejścia (pytest / HTTPX)

Należy zachować wszystkie dotychczasowe testy jednostkowe i komponentowe z LAB1, LAB2 i LAB3 (uruchamiane z atrapami w izolacji od sieci) oraz utworzyć w osobnym katalogu (np. `tests/integration/test_gateway_integration.py`) zestaw **co najmniej czterech własnych testów integracyjnych** wykonywanych przeciwko uruchomionemu środowisku przez port bramki (`8080`):

1. **Test 1 — odczyt domenowy z pierwszej usługi przez bramkę:** sprawdzenie kodu `200`, oczekiwanych pól JSON zasobu, nagłówka `X-Gateway: lab4` oraz obecności nagłówka `X-Cache` z LAB2 (`MISS` lub `HIT`).
2. **Test 2 — odczyt domenowy z drugiej usługi przez bramkę:** sprawdzenie kodu `200`, nagłówka `X-Gateway: lab4` oraz treści odpowiedzi potwierdzającej działanie przepływu z LAB3.
3. **Test 3 — zapis lub modyfikacja przez bramkę i następujący po nim odczyt:** wykonanie operacji `POST` lub `PATCH` przez `/api/...`, sprawdzenie kodu sukcesu (`201` lub `200`), a następnie wykonanie `GET` przez `/api/...` potwierdzającego trwałe zapisanie zmiany i odświeżenie odczytu.
4. **Test 4 — przekazanie błędu walidacji (`422`) lub reguły biznesowej (`409`) przez bramkę:** wysłanie niepoprawnych lub konfliktowych danych przez `/api/...`, sprawdzenie oczekiwanego kodu błędu (`422` albo `409`), treści `detail` oraz nagłówka `X-Gateway: lab4`.

Przykładowy szkielet pliku `tests/integration/test_gateway_integration.py` (ścieżki, nazwy pól i regułę należy dostosować do własnej domeny):

```python
import os
import uuid
import httpx
import pytest


@pytest.fixture
def client():
    base_url = os.getenv("GATEWAY_URL", "http://127.0.0.1:8080")
    with httpx.Client(base_url=base_url, timeout=10.0, trust_env=False) as http:
        yield http


def test_service_a_read_through_gateway_includes_gateway_and_cache_headers(client):
    # Zasób początkowy lub przygotowany wcześniej w usłudze pierwszej
    response = client.get("/api/rooms/R-101")
    assert response.status_code == 200
    assert response.json()["id"] == "R-101"
    assert response.headers.get("x-gateway") == "lab4"
    assert response.headers.get("x-cache") in {"MISS", "HIT", "BYPASS"}


def test_service_b_read_through_gateway_executes_lab3_flow(client):
    # Endpoint drugiej usługi korzystający z odnajdywania z LAB3
    response = client.get("/api/reservations/check-room/R-101")
    assert response.status_code == 200
    assert response.headers.get("x-gateway") == "lab4"
    body = response.json()
    assert body["room"]["id"] == "R-101"


def test_write_and_subsequent_read_through_gateway(client):
    # Unikatowy identyfikator lub aktualizacja pozwalająca na powtarzalne uruchomienie testu
    unique_id = f"R-{uuid.uuid4().hex[:6].upper()}"
    create_resp = client.post(
        "/api/rooms",
        json={"id": unique_id, "name": "Sala Testowa", "capacity": 24},
    )
    assert create_resp.status_code == 201
    assert create_resp.headers.get("x-gateway") == "lab4"

    read_resp = client.get(f"/api/rooms/{unique_id}")
    assert read_resp.status_code == 200
    assert read_resp.json()["name"] == "Sala Testowa"


def test_business_rule_or_validation_error_is_forwarded_by_gateway(client):
    # Przykład naruszenia reguły biznesowej (409) lub walidacji (422) z LAB1
    invalid_resp = client.post(
        "/api/rooms",
        json={"id": "R-ERR", "name": "Sala", "capacity": -5},
    )
    assert invalid_resp.status_code in {409, 422}
    assert "detail" in invalid_resp.json()
    assert invalid_resp.headers.get("x-gateway") == "lab4"
```

Wskazówki dotyczące utrzymania powtarzalności testów:

- jeśli operacją zapisu w teście 3 jest `POST` tworzący nowy zasób, należy generować unikatowy identyfikator (np. przez `uuid4`) albo usuwać rekord po teście, aby kolejne uruchomienie `pytest` nie kończyło się błędem duplikatu `409`,
- jeśli operacją zapisu jest `PATCH` modyfikujący istniejący rekord, należy zmieniać wartość pola (np. z użyciem znacznika lub licznika) i weryfikować tę nową wartość w kolejnym `GET`,
- nie należy kasować całego pliku bazy danych projektu na potrzeby testów integracyjnych,
- w README należy podać osobne polecenie do uruchomienia szybkich testów jednostkowych z LAB1–LAB3 (np. `pytest service-a/tests service-b/tests -q`) oraz osobne polecenie do uruchomienia testów integracyjnych wymagających działających procesów (np. `pytest tests/integration -q`).

### Krok 5. Uzupełnienie dokumentacji projektu

Dokumentację w głównym pliku `README.md` projektu należy rozbudować o sekcję etapu LAB4 na podstawie szablonu `README-LAB4-template.md` z pakietu pomocniczego. Nie należy usuwać dokumentacji wcześniejszych etapów (LAB1–LAB3).

W sekcji LAB4 należy zawrzeć:

- zaktualizowany diagram architektury obejmujący klienta, API Gateway (`:8080`), Eureka Server (`:8761`), obie mikrousługi (`:8101`, `:8102`) oraz bazę SQLite i cache Redis pierwszej usługi,
- tabelę tras wejściowych bramki (`Metoda i ścieżka klienta`, `id trasy`, `uri lb://...`, `ścieżka po StripPrefix`, `właściciel danych i uzasadnienie`),
- wykaz endpointów pozostawionych wyłącznie wewnątrz usług (nieudostępnionych przez bramkę) wraz z uzasadnieniem,
- wyjaśnienie konfiguracji limitów czasu (`connect-timeout`, `response-timeout`) w relacji do limitu czasu wywołania usługa–usługa z LAB3,
- pełną instrukcję uruchomienia i zatrzymania wszystkich komponentów (katalogi robocze, zmienne środowiskowe, porty, kolejność uruchamiania) oraz osobne komendy uruchomienia testów jednostkowych i integracyjnych,
- wypełnioną tabelę z rzeczywistymi wynikami sześciu eksperymentów awarii z Kroku 3 (w tym zaobserwowany czas odświeżenia rejestru i zachowanie nagłówków `X-Gateway` oraz `X-Cache`),
- opis co najmniej dwóch wykorzystanych źródeł oficjalnej dokumentacji (zgodnie z wymogiem **EK_03**: źródło i wersja, rozwiązywany problem, zastosowana konfiguracja oraz sposób weryfikacji),
- informację o wkładzie każdego autora w parze oraz o zakresie użycia i sposobie weryfikacji narzędzi AI (albo informację „nie korzystano”).

---

## 7. Diagnostyka typowych problemów konfiguracji

| Objaw problemu | Przyczyna i sposób weryfikacji |
|---|---|
| Polecenie `mvn` nie działa lub używa niewłaściwej wersji Javy | Należy sprawdzić `java -version` i `mvn -version` w tym samym oknie PowerShella oraz ustawić `JAVA_HOME` na katalog JDK 21 i dodać katalogi `bin` JDK oraz Mavena do `PATH`. Nie należy instalować pakietów Pythona o nazwie `maven` |
| `GET /health` na `:8080` zwraca `200`, ale wszystkie ścieżki `/api/...` zwracają `404` bez `X-Gateway` | Błąd wcięć w pliku `application.yml`, umieszczenie `routes` poza ścieżką `spring.cloud.gateway.server.webflux.routes` albo brak restartu procesu Maven po zapisaniu pliku YAML |
| Ścieżka `/api/...` zwraca `404`, ale w odpowiedzi jest obecny nagłówek `X-Gateway: lab4` | Żądanie przeszło przez trasę bramki i dotarło do usługi FastAPI, lecz w usłudze nie ma takiej ścieżki (błędna wartość `StripPrefix`) albo w bazie usługi nie istnieje rekord o podanym identyfikatorze. Należy sprawdzić log Uvicorna |
| Bramka zwraca `503 Service Unavailable` mimo uruchomionej usługi Python | Niezgodność nazwy usługi w `lb://NAZWA-USŁUGI` z nazwą widoczną w panelu Eureki, brak końcowego `/eureka/` w `defaultZone` bramki albo zbyt krótki czas od momentu uruchomienia usługi (przed odświeżeniem lokalnej kopii rejestru) |
| Bramka zwraca `500` lub `504` przy wywołaniu trasy | Wpis `UP` w kopii rejestru wskazuje na nieaktualny port/adres, proces usługi został zatrzymany bez wyrejestrowania albo wywołanie przekroczyło `response-timeout` |
| Bramka zwraca `405 Method Not Allowed` przy próbie zapisu | Trasa przekazała żądanie do usługi, ale dany endpoint w FastAPI nie obsługuje użytej metody HTTP (np. wysłano `POST` na ścieżkę obsługującą wyłącznie `GET` lub `PATCH`) |
| `GET /api/docs` zwraca `404` | Dokumentacja Swagger UI (`/docs`) i schemat `/openapi.json` nie mają zdefiniowanej trasy w bramce; interaktywną dokumentację każdej usługi należy otwierać bezpośrednio na jej porcie lokalnym (`8101`, `8102`) |
| Zmiana w `application.yml` nie przynosi efektu | Proces Spring Boot uruchomiony przez `mvn spring-boot:run` nie przeładowuje automatycznie zmian konfiguracji jak `uvicorn --reload`; po każdej zmianie YAML należy zatrzymać bramkę (`Ctrl+C`) i uruchomić ją ponownie |

### Granice zakresu zadania na LAB4

W ramach LAB4 nie należy implementować uwierzytelniania i autoryzacji użytkowników (OAuth2 / JWT), agregacji dokumentacji OpenAPI w bramce, komunikacji asynchronicznej przez brokera wiadomości, konteneryzacji bramki i usług w jednym pliku Docker Compose ani dodatkowych warstw frontendowych. Należy skupić się na poprawnym skonfigurowaniu routingu wspólnego wejścia, integracji z Eureką oraz rygorystycznej weryfikacji współdziałania z mechanizmami z LAB1–LAB3.

---

## 8. Punkty kontrolne, odbiór i kryteria oceny etapu

### Punkty kontrolne weryfikowane przy odbiorze

| Punkt kontrolny | Oczekiwany dowód wykonania |
|---|---|
| **Punkt A — ciągłość LAB1–LAB3** | Działają obie usługi własnego projektu, baza SQLite i cache Redis pierwszej usługi, rejestracja w Eurece oraz dotychczasowe testy jednostkowe |
| **Punkt B — projekt kontraktu wejściowego** | Uzupełniona tabela tras dla własnej domeny, uzasadnienie wyboru udostępnionych ścieżek oraz rozdzielenie odpowiedzialności komponentów |
| **Punkt C — konfiguracja bramki** | Co najmniej dwie jawne trasy w `application.yml` kierujące ruch przez `lb://NAZWA-USŁUGI` do dwóch różnych usług, z poprawnym `StripPrefix` i nagłówkiem diagnostycznym |
| **Punkt D — spójność operacji API** | Przez port bramki (`8080`) działają: odczyt z pierwszej usługi (z widocznymi nagłówkami `X-Gateway` i `X-Cache`), zapis/modyfikacja unieważniająca cache, odczyt z drugiej usługi (wykonujący pod spodem wywołanie z LAB3) oraz kody błędów `404`, `409`, `422` |
| **Punkt E — analiza awarii** | Przeprowadzone i udokumentowane scenariusze zatrzymania każdej z usług, ponownego uruchomienia usługi oraz zatrzymania bramki |
| **Punkt F — testy integracyjne** | Przechodzą co najmniej cztery własne testy integracyjne wywołujące API przez bramkę oraz wszystkie wcześniejsze testy projektu |

### Pytania do rozmowy technicznej podczas odbioru

Każda osoba (również przy pracy w parze) powinna umieć samodzielnie odpowiedzieć na pytania:

1. Czym różni się rola API Gateway od roli serwera Eureka oraz od wzorca BFF?
2. Dlaczego bramka ma ustawione `fetch-registry: true` oraz `register-with-eureka: false` i dlaczego nie widać jej na liście instancji w panelu Eureki?
3. W jaki sposób zapis `uri: lb://NAZWA-USŁUGI` pozwala bramce przekazać żądanie bez wpisywania numeru portu usługi w pliku `application.yml`?
4. Co dokładnie zmienia filtr `StripPrefix=1`, a jakich elementów żądania i odpowiedzi (np. metody HTTP, ciała JSON, nagłówka `X-Cache` z LAB2) nie modyfikuje?
5. Po jakich cechach odpowiedzi HTTP i logów można odróżnić `404` wynikające z braku trasy w bramce od `404` wynikającego z braku rekordu w bazie usługi?
6. Dlaczego zatrzymanie pierwszej usługi wpływa nie tylko na jej własną trasę w bramce, ale również na endpoint drugiej usługi korzystający z wywołania z LAB3?

Podczas odbioru każda osoba powinna również wykonać drobną modyfikację na żywo (np. zmianę prefiksu zewnętrznego wybranej trasy na `/api/v2/...`, dopasowanie wartości `StripPrefix`, wskazanie wynikowej ścieżki w usłudze i aktualizację odpowiedniego testu integracyjnego).

### Kryteria oceny etapu LAB4

Punktacja etapu zachowuje proporcję z sylabusa przedmiotu: **60 punktów za kod** oraz **40 punktów za dokumentację**.

| Obszar | Oceniany element | Maksimum |
|---|---|---:|
| **Kod** | Zachowanie pełnej funkcjonalności usług i mechanizmów z LAB1–LAB3 (baza SQLite, cache Redis, rejestracja i wywołanie przez Eurekę) | 10 |
| **Kod** | Poprawna konfiguracja co najmniej dwóch jawnych tras w Spring Cloud Gateway przez `lb://`, warunki `Path`, `StripPrefix`, nagłówek `X-Gateway` i limity czasu | 20 |
| **Kod** | Poprawne przekazywanie przez bramkę odczytu z obu usług, operacji zapisu (z unieważnieniem cache z LAB2) oraz błędów domenowych i walidacji (`404`, `409`, `422`) | 15 |
| **Kod** | Co najmniej cztery własne, powtarzalne testy integracyjne przechodzące przez bramkę oraz utrzymanie wcześniejszych testów jednostkowych | 15 |
| **Dokumentacja** | Projekt kontraktu wejściowego, tabela tras, diagram architektury z uwzględnieniem zasobów LAB2–LAB4 oraz granice odpowiedzialności | 10 |
| **Dokumentacja** | Powtarzalna instrukcja uruchomienia i zatrzymania wszystkich procesów, opis zmiennych środowiskowych, portów i przygotowania danych testowych | 10 |
| **Dokumentacja** | Udokumentowane wyniki sześciu scenariuszy awarii, porównanie źródeł błędów HTTP oraz opis ograniczeń rozwiązania | 10 |
| **Dokumentacja** | Opis co najmniej dwóch wykorzystanych źródeł dokumentacji technicznej (EK_03), wkład autorów i informacja o weryfikacji AI | 10 |
| **Razem** | **Kod 60 pkt + Dokumentacja 40 pkt** | **100** |

**Warunki zaliczenia etapu:** uzyskanie co najmniej **50 punktów** oraz spełnienie wszystkich poniższych warunków minimum:

- projekt zachowuje dwie odrębne usługi domenowe oraz działające mechanizmy z LAB1, LAB2 i LAB3,
- bramka udostępnia co najmniej dwie jawne trasy prowadzące do dwóch różnych usług za pomocą nazw logicznych z Eureki (`lb://`),
- przez bramkę wykazano poprawny odczyt z obu usług, operację zapisu z aktualizacją stanu/cache oraz poprawne przekazanie błędu walidacji (`422`) lub reguły biznesowej (`409`),
- w kodzie i konfiguracji bramki nie umieszczono logiki biznesowej ani bezpośrednich połączeń z bazą danych usług,
- przechodzą wcześniejsze testy projektu oraz co najmniej cztery własne testy integracyjne wywołujące bramkę,
- w README udokumentowano przebieg i wnioski ze scenariuszy awarii oraz wykorzystane źródła dokumentacji,
- każda osoba potrafi samodzielnie wyjaśnić konfigurację, przepływ żądania i wykonać drobną zmianę podczas odbioru.

---

## 9. Oznaczenie i przekazanie wersji projektu LAB4

Rozwiązanie należy przekazać w tym samym repozytorium Git co poprzednie etapy. Przed utworzeniem commita należy upewnić się, że plik `.gitignore` wyklucza katalogi środowisk wirtualnych (`.venv/`), artefakty budowania Mavena (`gateway/target/`), lokalne pliki baz danych (`*.db`), pamięć podręczną Pythona (`__pycache__/`, `.pytest_cache/`) oraz pliki lokalnej konfiguracji (`.env`).

Przykładowa sekwencja poleceń w terminalu PowerShell:

```powershell
git status
git add .
git diff --cached --stat
git commit -m "feat(lab4): konfiguracja wspólnego punktu wejścia API Gateway i testy integracyjne"
git tag lab4
git push origin HEAD
git push origin refs/tags/lab4
```

Jeżeli znacznik `lab4` został już wcześniej utworzony, nie należy nadpisywać go opcją `--force` — ewentualną poprawkę należy oznaczyć kolejnym tagiem uzgodnionym z prowadzącym (np. `lab4-v2`).

---

## 10. Dokumentacja techniczna

Podczas realizacji zadania należy wykorzystać co najmniej dwa źródła z oficjalnej dokumentacji technicznej (wymaganie **EK_03**) i opisać w README: rozwiązany problem, zastosowaną opcję konfiguracyjną lub fragment kodu oraz sposób weryfikacji działania.

- [Spring Cloud Gateway — Server WebFlux Starter](https://docs.spring.io/spring-cloud-gateway/reference/spring-cloud-gateway-server-webflux/starter.html) — dobór reaktywnego startera bramki i wymaganych zależności Maven.
- [Spring Cloud Gateway — Configuration Properties](https://docs.spring.io/spring-cloud-gateway/reference/appendix.html) — struktura właściwości pod kluczem `spring.cloud.gateway.server.webflux`, definicja tras oraz parametry `httpclient.connect-timeout` i `httpclient.response-timeout`.
- [Path Route Predicate Factory](https://docs.spring.io/spring-cloud-gateway/reference/spring-cloud-gateway-server-webflux/request-predicates-factories/path-route-predicate-factory.html) — dopasowywanie ścieżek wejściowych, w tym wzorców kolekcji i ścieżek podrzędnych (`/api/zasob`, `/api/zasob/**`).
- [StripPrefix GatewayFilter Factory](https://docs.spring.io/spring-cloud-gateway/reference/spring-cloud-gateway-server-webflux/gatewayfilter-factories/stripprefix-factory.html) — usuwanie wskazanej liczby początkowych segmentów ścieżki przed przekazaniem żądania do usługi.
- [ReactiveLoadBalancerClientFilter](https://docs.spring.io/spring-cloud-gateway/reference/spring-cloud-gateway-server-webflux/global-filters.html) — działanie schematu `lb://NAZWA-USŁUGI` oraz zachowanie bramki przy braku dostępnych instancji w rejestrze (`503`).
- [Spring Cloud Netflix — Eureka Client](https://docs.spring.io/spring-cloud-netflix/reference/spring-cloud-netflix.html) — konfiguracja pobierania rejestru (`fetch-registry`), wyłączenia własnej rejestracji (`register-with-eureka`) oraz adresu `defaultZone`.
- [HTTPX — QuickStart & Client](https://www.python-httpx.org/quickstart/) — wykonywanie żądań HTTP, przekazywanie ładunków JSON oraz weryfikacja kodów statusu i nagłówków w testach integracyjnych.
