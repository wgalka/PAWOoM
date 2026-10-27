# LAB6 — Konteneryzacja systemu mikrousługowego (Docker / Docker Compose)

## Projektowanie aplikacji webowych opartych o mikrousługi

- **Czas:** 120 minut zajęć; silnik Docker Desktop oraz bazowe obrazy należy przygotować przed zajęciami
- **Technologia:** Docker, Docker Compose, obrazy wieloetapowe (`Dockerfile`), nazwane wolumeny oraz komplet komponentów z LAB1–LAB5 (FastAPI, SQLite, Redis, Eureka Server, Spring Cloud Gateway, RabbitMQ)
- **Forma:** praca indywidualna lub w parach, w dotychczasowym repozytorium projektu z LAB1–LAB5
- **Rezultat:** w pełni skonteneryzowany system mikrousługowy uruchamiany jednym poleceniem `docker compose up --build -d`, z izolacją sieciową usług za bramką API Gateway, trwałym wolumenem bazy danych, testami integracyjnymi oraz kompletną dokumentacją końcową projektu

---

## 1. Cel i zakres laboratorium

W tym ćwiczeniu należy zrealizować szósty, ostatni temat laboratoryjny z sylabusa: **„Konteneryzacja mikrousług przy użyciu silnika Docker”**, domykając architekturę systemu budowanego etapami w LAB1–LAB5. Dotychczas usługi Pythona oraz bramka API Gateway były uruchamiane ręcznie jako osobne procesy systemu gospodarza (*host OS*) w wielu oknach terminala. W ramach tego laboratorium należy przygotować pliki `Dockerfile` oraz plik `compose.yaml`, przenieść cały system do wspólnej sieci kontenerowej, skonfigurować trwały wolumen dla bazy danych oraz zweryfikować działanie wszystkich przepływów synchronicznych i asynchronicznych wyłącznie przez punkt wejścia bramki API Gateway.

Po wykonaniu laboratorium należy umieć:

- wyjaśnić różnicę pomiędzy maszyną fizyczną, maszyną wirtualną a kontenerem oraz wskazać rolę lokalnego `Docker Compose` i produkcyjnej orkiestracji w `Kubernetes`,
- przygotować powtarzalny plik `Dockerfile` oraz `.dockerignore` dla mikrousługi Python/FastAPI z wykorzystaniem warstw pamięci podręcznej i nieuprzywilejowanego użytkownika,
- zastosować budowanie wieloetapowe (*multi-stage build*) dla komponentów JVM (Spring Cloud Gateway i Eureka Server), oddzielając środowisko kompilacji Mavena od lekkiego obrazu uruchomieniowego JRE,
- skonfigurować komunikację wewnątrz sieci Docker Compose po nazwach DNS usług (`eureka`, `redis`, `rabbitmq`, nazwy kontenerowe usług w `INSTANCE_HOST`) zamiast adresów `127.0.0.1`,
- odizolować porty mikrousług, bazy cache i brokera wewnątrz sieci kontenerowej (`expose`), publikując na zewnątrz (`ports`) wyłącznie wejściowy port bramki API Gateway (oraz opcjonalnie panele diagnostyczne),
- zachować trwałość bazy danych SQLite z LAB2 poza cyklem życia kontenera przy użyciu nazwanego wolumenu (`volumes`),
- skonfigurować kontrole zdrowia (`healthcheck`) oraz kolejność startu kontenerów (`depends_on: condition: service_healthy`),
- zweryfikować kompletny system testami integracyjnymi i przygotować końcową dokumentację projektu zgodnie z wymaganiami zaliczeniowymi sylabusa (60% kod / 40% dokumentacja).

### Powiązanie z efektami kształcenia

| Efekt | Ćwiczone działanie na LAB6 | Dowód wykonania |
|---|---|---|
| EK_04 — projektowanie systemu z kilku mikrousług i skomunikowanie wszystkich komponentów podstawowych | Zintegrowanie wszystkich komponentów (brama, rejestr usług, dwie mikrousługi, baza danych, cache Redis, broker RabbitMQ) w jednym środowisku kontenerowym | Działające środowisko `compose.yaml`, przechodzące testy end-to-end i finalny diagram architektury |
| EK_03 — implementacja funkcjonalności z wykorzystaniem dokumentacji | Opracowanie plików `Dockerfile`, `.dockerignore` oraz definicji `compose.yaml` (sieci, wolumeny, `healthcheck`) na podstawie oficjalnej dokumentacji | Zbudowane obrazy, działające kontenery oraz opis dwóch źródeł dokumentacji w README |
| EK_01 — rozumienie pojęć architektury mikrousługowej | Porównanie maszyn wirtualnych i kontenerów, wzorców Monorepo i Multirepo, roli CI/CD oraz podstaw Kubernetes | Poprawne wyjaśnienie pojęć oraz architektury wdrożeniowej podczas odbioru |
| EK_02 — dobór i wykorzystanie narzędzi | Wykorzystanie silnika Docker, Docker Compose, obrazów wieloetapowych, sieci i wolumenów kontenerowych | Powtarzalne uruchomienie całego systemu jednym poleceniem i weryfikacja stanu kontenerów |
| EK_05 — analiza wyzwań, jakości i ograniczeń rozwiązania | Weryfikacja trwałości danych przy odtworzeniu kontenera, izolacji sieciowej portów oraz czasu gotowości zależności | Udokumentowane wyniki eksperymentów kontenerowych i ocena ograniczeń |

---

## 2. Zachowanie ciągłości projektu i finalizacja architektury z LAB1–LAB6

Pracę należy kontynuować w tym samym repozytorium Git. Nie należy zmieniać logiki domenowej, reguł biznesowych ani kontraktów API wypracowanych w LAB1–LAB5 — celem jest opakowanie działającego systemu w przenośne kontenery i zastąpienie ręcznego uruchamiania wielu terminali deklaratywną orkiestracją `Docker Compose`.

### Zestawienie pełnego stosu projektu z LAB1–LAB6

| Etap | Element systemu | Sposób uruchomienia w LAB1–LAB5 | Sposób uruchomienia i konfiguracji w LAB6 |
|---|---|---|---|
| **LAB1** | Pierwsza mikrousługa (FastAPI, modele Pydantic, reguła biznesowa `409`, walidacja `422`) | Lokalny proces Uvicorna (`--port 8101`, domyślny host `127.0.0.1`) | Kontener budowany z własnego `Dockerfile`, nasłuchujący na `--host 0.0.0.0 --port 8101`, dostępny tylko w sieci Docker (`expose: 8101`) |
| **LAB2** | Baza SQLite (SQLAlchemy) i cache-aside w Redis (`X-Cache`, `TTL`, unieważnianie) | Plik `./app.db` na dysku hosta; pojedynczy kontener lub proces Redis na `localhost:6379` | Plik bazy zapisywany na **nazwanym wolumenie** (`/data/app.db`); kontener `redis` osiągalny pod adresem `redis://redis:6379/0` |
| **LAB3** | Druga mikrousługa i rejestr Eureka (`:8761`), wywołanie `do_service()` | Osobny terminal Uvicorna (`:8102`), zgłoszenie `INSTANCE_HOST=localhost` do `127.0.0.1:8761` | Kontenery obu usług zgłaszają swoje nazwy usług z `compose.yaml` (`INSTANCE_HOST=service-a`) do `http://eureka:8761` |
| **LAB4** | Wspólny punkt wejścia API Gateway (`:8080`, `lb://`, `StripPrefix=1`, `X-Gateway`) | Lokalny proces Maven (`mvn spring-boot:run`) na hoście | Kontener `api-gateway` budowany wieloetapowo, nasłuchujący na `0.0.0.0:8080` i publikujący port `127.0.0.1:8080:8080` dla klienta zewnętrznego |
| **LAB5** | Broker wiadomości RabbitMQ (`:5672` / `:15672`), publikacja i idempotentna konsumpcja | Osobny kontener RabbitMQ wywoływany z hosta przez `127.0.0.1:5672` | Kontener `rabbitmq` we wspólnej sieci `compose.yaml`, osiągalny dla usług pod adresem `amqp://guest:guest@rabbitmq:5672/%2F` |
| **LAB6** | Cały system mikrousługowy | 5–6 osobnych terminali uruchamianych ręcznie w odpowiedniej kolejności | Jedna definicja `compose.yaml` z kontrolami `healthcheck`, zależnościami `depends_on` i nazwanym wolumenem danych |

Zgodnie z sylabusem przedmiotu na ostatnich zajęciach kompletny kod źródłowy wraz z dokumentacją stanowi podstawę oceny projektu (60% jakość i kompletność kodu — w tym minimum dwie różne mikrousługi na osobę oraz wszystkie wymagane komponenty systemu; 40% jakość dokumentacji).

### Organizacja pracy na zajęciach

Proponowany podział 120 minut zajęć:

- **15 minut** — omówienie różnic między VM a kontenerami, budowy warstwowej `Dockerfile`, sieci/wolumenów Docker oraz roli `Docker Compose` i `Kubernetes`,
- **20 minut** — uruchomienie i analiza skonteneryzowanego przykładu (`lab6-support`),
- **15 minut** — zaprojektowanie adresacji sieciowej, zmiennych środowiskowych i wolumenów dla własnego projektu,
- **35 minut** — przygotowanie plików `Dockerfile`, `.dockerignore` oraz `compose.yaml` dla własnego repozytorium i zbudowanie obrazów,
- **20 minut** — weryfikacja pełnego przepływu (LAB1–LAB5) przez skonteneryzowaną bramkę oraz eksperyment trwałości wolumenu i izolacji portów,
- **15 minut** — odbiór końcowy etapu i weryfikacja kompletności dokumentacji.

---

## 3. Pojęcia konteneryzacji i orkiestracji mikrousług

### Maszyny fizyczne, maszyny wirtualne i kontenery

Zgodnie z problematyką wykładową sylabusa należy rozróżnić trzy poziomy izolacji środowiska uruchomieniowego:

| Cecha | Maszyna fizyczna | Maszyna wirtualna (VM) | Kontener (Docker) |
|---|---|---|---|
| **Warstwa izolacji** | Brak (wspólny sprzęt i jeden system operacyjny) | Pełna wirtualizacja sprzętu przez *Hypervisor*; każda VM uruchamia własne jądro systemu (*Guest OS*) | Izolacja procesów na poziomie przestrzeni nazw (*namespaces*) i grup kontrolnych (*cgroups*) wspólnego jądra systemu |
| **Narzut zasobów i rozmiar** | Brak narzutu wirtualizacji, trudne dzielenie zależności | Duży (gigabajty obrazu, osobny RAM dla każdego systemu gościa) | Niski (dziesiątki lub setki megabajtów, współdzielone jądro systemu) |
| **Czas uruchomienia** | Minuty | Od kilkunastu sekund do kilku minut | Ułamki sekund do kilku sekund |
| **Powtarzalność środowiska** | Niska („u mnie działa” przez różnice bibliotek w systemie) | Wysoka, lecz kosztowna w budowaniu i dystrybucji | Bardzo wysoka — obraz zawiera dokładne wersje języka, bibliotek i zależności aplikacji |

### Budowa obrazu, warstwy i budowanie wieloetapowe (`Dockerfile`)

**Obraz kontenerowy (*Image*)** jest niemodyfikowalnym szablonem składającym się z warstw tylko do odczytu. **Kontener (*Container*)** jest uruchomioną instancją obrazu z dołączoną cienką, ulotną warstwą zapisu.

Podczas tworzenia plików `Dockerfile` należy stosować trzy zasady inżynierskie:

1. **Wykorzystanie pamięci podręcznej warstw (*Layer Caching*):** w usłudze Python należy najpierw skopiować sam plik `requirements.txt` i wykonać `RUN pip install ...`, a dopiero w kolejnym kroku skopiować kod aplikacji (`COPY . .`). Dzięki temu zmiana w kodzie `main.py` nie wymusza ponownego pobierania bibliotek podczas kolejnego `docker compose build`.
2. **Budowanie wieloetapowe (*Multi-stage build*):** dla bramki Spring Cloud Gateway (oraz serwera Eureka) w pierwszym etapie (`FROM maven:3.9.9-eclipse-temurin-21 AS build`) kompilowany jest plik `.jar`, natomiast do docelowego obrazu uruchomieniowego (`FROM eclipse-temurin:21-jre-alpine`) kopiowany jest wyłącznie gotowy artefakt `app.jar` bez narzędzi kompilatora i lokalnego cache Mavena.
3. **Plik `.dockerignore`:** wyklucza z kontekstu budowania lokalne katalogi `.venv/`, `target/`, `.git/`, `__pycache__/` oraz lokalne pliki baz `*.db`, przyspieszając budowanie i zapobiegając przypadkowemu skopiowaniu lokalnych artefaktów z systemu Windows do kontenera Linuksa.

### Sieć kontenerowa, adresacja `0.0.0.0` i rejestracja w Eurece

Przeniesienie mikrousług z procesów hosta do kontenerów zmienia znaczenie adresu `127.0.0.1` (`localhost`):

- na hoście w LAB1–LAB5 wszystkie procesy dzieliły interfejs pętli zwrotnej `127.0.0.1`, więc `PARCEL-SERVICE` mogła wywołać `LOCKER-SERVICE` pod adresem `http://localhost:8101`,
- w Dockerze **każdy kontener posiada własny, odizolowany interfejs `127.0.0.1`**; wywołanie `http://127.0.0.1:8101` wewnątrz kontenera `parcel-service` oznacza próbę połączenia z samym sobą, która kończy się błędem `Connection refused`!

Aby komunikacja w `Docker Compose` działała poprawnie, należy skonfigurować trzy elementy:

1. **Nasłuchiwanie na `0.0.0.0` wewnątrz kontenera:** serwer Uvicorn w kontenerze musi być uruchamiany z parametrem `--host 0.0.0.0`, a Spring Cloud Gateway ze zmienną `SERVER_ADDRESS=0.0.0.0`, aby przyjmować połączenia przychodzące z wirtualnej sieci Dockera.
2. **Komunikacja po nazwach usług z `compose.yaml`:** wbudowany serwer DNS Dockera rozwiązuje nazwy usług zdefiniowanych w `compose.yaml` (np. `http://eureka:8761`, `redis://redis:6379/0`, `amqp://guest:guest@rabbitmq:5672/%2F`).
3. **Zgłoszenie nazwy kontenerowej do Eureki (`INSTANCE_HOST` / `INSTANCE_IP`):** usługa rejestrująca się w Eurece nie może zgłaszać `INSTANCE_HOST=localhost`, ponieważ inny kontener (np. `api-gateway` lub druga usługa) po pobraniu takiego wpisu z Eureki próbowałby łączyć się z własnym `localhost`. W `compose.yaml` dla każdej usługi należy ustawić `INSTANCE_HOST` oraz `INSTANCE_IP` na jej nazwę usługi w sieci Docker Compose (np. `INSTANCE_HOST: locker-service`, `INSTANCE_IP: locker-service`).

<pre class="mermaid">
flowchart LR
    Client["Klient na hoście<br/>(curl / pytest)"] -->|"127.0.0.1:8080"| GW

    subgraph DockerNet["Sieć wewnętrzna Docker Compose"]
        GW["api-gateway :8080"]
        EU["eureka :8761"]
        S1["locker-service :8101<br/>(expose only)"]
        S2["parcel-service :8102<br/>(expose only)"]
        RD[("redis :6379<br/>(expose only)")]
        RMQ[["rabbitmq :5672 / :15672"]]

        GW -->|"lb://LOCKER-SERVICE<br/>(http://locker-service:8101)"| S1
        GW -->|"lb://PARCEL-SERVICE<br/>(http://parcel-service:8102)"| S2
        S2 -->|"HTTP przez Eurekę<br/>http://locker-service:8101"| S1
        S2 -->|"AMQP: rabbitmq:5672"| RMQ
        RMQ -->|"Konsumpcja + ACK"| S1
        S1 <-->|"redis:6379"| RD
        S1 -.->|"http://eureka:8761"| EU
        S2 -.->|"http://eureka:8761"| EU
        GW -.->|"http://eureka:8761/eureka/"| EU
    end

    VOL[("Nazwany wolumen Docker<br/>locker_data (/data/locker.db)")]
    S1 --> VOL
</pre>

### Monorepo a Multirepo, CI/CD oraz Docker Compose a Kubernetes

W kontekście wdrażania systemów mikrousługowych należy uporządkować pojęcia z sylabusa:

- **Monorepo vs Multirepo:** rozwijany na laboratoriach projekt wykorzystuje wzorzec **Monorepo** — wszystkie mikrousługi (`service-a`, `service-b`), komponent `gateway` oraz wspólny plik `compose.yaml` znajdują się w jednym repozytorium Git, co ułatwia spójne wersjonowanie (tagi `lab1`–`lab6`) i atomowe testy integracyjne. W dużych organizacjach stosuje się również **Multirepo** (osobne repozytorium i osobny potok CI/CD dla każdej mikrousługi), co zwiększa autonomię zespołów, ale wymaga osobnej koordynacji wersji kontraktów API.
- **Rola CI/CD (*Continuous Integration / Continuous Delivery*):** w zautomatyzowanym potoku CI każda zmiana kodu uruchamia najpierw szybkie testy jednostkowe z atrapami (`MemoryRedis`, `FakeEurekaClient`, `InMemoryEventBroker`), następnie buduje obrazy kontenerowe (`docker build`) i wykonuje testy integracyjne na uruchomionym środowisku kontenerowym.
- **Docker Compose vs Kubernetes:** `Docker Compose` służy do deklaratywnego uruchamiania wielu kontenerów na **jednej maszynie** (lokalnej lub testowej). W środowiskach produkcyjnych do zarządzania kontenerami na klastrze wielu serwerów stosuje się orkiestratory takie jak **Kubernetes**, gdzie podstawową jednostką wdrożenia jest **Pod**, liczbą replik i aktualizacjami zarządza **Deployment**, a stabilną adresację sieciową i równoważenie obciążenia zapewnia obiekt **Service** oraz **Ingress / Gateway API**.

---

## 4. Część A — uruchomienie i analiza skonteneryzowanego przykładu

### Krok 1. Pobranie pakietu pomocniczego i analiza plików `Dockerfile` oraz `compose.yaml`

Należy pobrać [pakiet pomocniczy LAB6 — ZIP]({{ '/2026_2027/lab6/lab6-support.zip' | relative_url }}) i rozpakować go w strukturze materiałów obok katalogów z poprzednich laboratoriów (lub przejść do katalogu `2026_2027/lab6/lab6-support`).

Struktura pakietu `lab6-support`:

```text
lab6-support/
├── compose.yaml
├── docker/
│   ├── .dockerignore
│   ├── Dockerfile.gateway
│   └── Dockerfile.python
├── tests/
│   └── test_containerized_system.py
├── requirements.txt
├── README-LAB6-template.md
├── README.md
└── .gitignore
```

Należy przeanalizować wzorcowy plik `docker/Dockerfile.python`:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8101

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8101"]
```

Następnie należy otworzyć plik `compose.yaml` i zwrócić uwagę na:

- różnicę pomiędzy `ports` (np. `"127.0.0.1:8080:8080"` w `api-gateway`) a `expose` (np. `"8101"` w `locker-service`, `"8102"` w `parcel-service`, `"6379"` w `redis`),
- sekcję `healthcheck` w kontenerach `eureka`, `redis` i `rabbitmq` oraz warunek `depends_on` z `condition: service_healthy`,
- konfigurację zmiennych `INSTANCE_HOST: locker-service` oraz `INSTANCE_IP: locker-service`,
- sekcję `volumes: locker_data:/data`, która montuje trwały wolumen w katalogu `/data` wewnątrz kontenera.

### Krok 2. Zbudowanie i uruchomienie całego systemu jednym poleceniem (Docker Compose)

Przed uruchomieniem kontenerów należy upewnić się, że działa Docker Desktop (`docker version`) oraz że wcześniejsze lokalne procesy z LAB3–LAB5 nie zajmują portów `8080`, `8761` i `15672`.

W terminalu PowerShell, w katalogu `2026_2027/lab6/lab6-support`, należy wykonać:

```powershell
docker compose up --build -d
docker compose ps
```

Pierwsze budowanie obrazów może potrwać kilka minut. Po uruchomieniu należy obserwować status kontenerów (`docker compose ps`), aż kontenery `eureka`, `redis` i `rabbitmq` osiągną stan `(healthy)`, a następnie otworzyć panel Eureki pod adresem `http://127.0.0.1:8761/`.

W panelu Eureki należy sprawdzić wpisy zarejestrowanych instancji:

- `LOCKER-SERVICE` jest zarejestrowany pod adresem kontenerowym `locker-service:8101`,
- `PARCEL-SERVICE` jest zarejestrowany pod adresem kontenerowym `parcel-service:8102`.

Następnie z terminala na hoście należy wykonać zapytania przez opublikowany port bramki (`8080`):

```powershell
curl.exe -i http://127.0.0.1:8080/health
curl.exe -i http://127.0.0.1:8080/api/lockers/KRK-1024
curl.exe -i http://127.0.0.1:8080/api/delivery-check/KRK-1024
```

Oraz sprawdzić izolację sieciową — próba bezpośredniego wywołania portu `8101` lub `8102` z hosta:

```powershell
curl.exe -i http://127.0.0.1:8101/lockers/KRK-1024
```

powinna zakończyć się odmową połączenia, ponieważ mikrousługi nie publikują swoich portów na hoście (`expose` zamiast `ports`) i są dostępne wyłącznie wewnątrz sieci Docker Compose za pośrednictwem bramki API Gateway!

### Krok 3. Uruchomienie testów integracyjnych przeciwko kontenerom (pytest / HTTPX)

W katalogu `lab6-support` należy utworzyć środowisko dla klienta testowego i uruchomić testy:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

Oczekiwany wynik to `5 passed`. Po zakończeniu części demonstracyjnej należy zatrzymać środowisko przykładowe poleceniem `docker compose down -v`.

---

## 5. Część B — konteneryzacja własnego projektu z LAB1–LAB5

Głównym zadaniem laboratorium jest przygotowanie kompletnej konteneryzacji własnego projektu rozwijanego w LAB1–LAB5.

### Krok 1. Zaprojektowanie konfiguracji kontenerowej własnego systemu

Dla własnego repozytorium należy uzupełnić tabelę konfiguracji kontenerów:

| Usługa w `compose.yaml` | Kontekst budowania / obraz | Port wewnętrzny | Port na hoście (`ports`) | Kluczowe zmienne środowiskowe i wolumeny |
|---|---|---|---|---|
| `eureka` | `./eureka-server` (lub obraz z LAB3) | `8761` | `127.0.0.1:8761:8761` | — |
| `redis` | `redis:7-alpine` | `6379` | Brak (`expose`) | — |
| `rabbitmq` | `rabbitmq:3.13-management-alpine` | `5672` | `127.0.0.1:15672:15672` | `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS` |
| Pierwsza usługa (z LAB1–LAB5) | np. `./service-a` | `8101` | Brak (`expose`) | `INSTANCE_HOST=service-a`, `DATABASE_URL=sqlite:////data/app.db`, `REDIS_URL=redis://redis:6379/0`, `EUREKA_SERVER_URL=http://eureka:8761`, `RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/%2F`, wolumen `service_a_data:/data` |
| Druga usługa (z LAB3–LAB5) | np. `./service-b` | `8102` | Brak (`expose`) | `INSTANCE_HOST=service-b`, `EUREKA_SERVER_URL=http://eureka:8761`, `RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/%2F` |
| `api-gateway` (z LAB4) | `./gateway` | `8080` | `127.0.0.1:8080:8080` | `SERVER_ADDRESS=0.0.0.0`, `GATEWAY_EUREKA_URL=http://eureka:8761/eureka/` |

### Krok 2. Przygotowanie plików `Dockerfile` oraz `.dockerignore` dla własnych usług

W katalogach własnych mikrousług Pythona oraz w katalogu `gateway/` (i `eureka-server/`, jeśli znajduje się w repozytorium) należy umieścić pliki `Dockerfile` oraz `.dockerignore`, wzorując się na plikach z pakietu `lab6-support/docker/`.

Należy upewnić się, że:

- w każdej usłudze Python tworzony jest katalog `/data` z uprawnieniami zapisu dla użytkownika uruchamiającego proces w kontenerze (lub wolumen montowany jest z odpowiednimi uprawnieniami), aby SQLite mógł utworzyć plik `/data/app.db` oraz pliki dziennika transakcji,
- polecenie `CMD` w `Dockerfile` każdej usługi uruchamia Uvicorna z parametrem `--host 0.0.0.0` oraz portem zgodnym z `SERVICE_PORT`,
- w pliku `gateway/src/main/resources/application.yml` właściwość `server.address` pozwala na nadpisanie adresem `0.0.0.0` (np. `address: ${SERVER_ADDRESS:127.0.0.1}`).

### Krok 3. Utworzenie głównego pliku `compose.yaml` w repozytorium projektu

W głównym katalogu własnego repozytorium należy utworzyć plik `compose.yaml` łączący wszystkie komponenty systemu:

1. Zdefiniować usługi infrastrukturalne (`eureka`, `redis`, `rabbitmq`) wraz z sekcjami `healthcheck`.
2. Zdefiniować obie własne mikrousługi z warunkami `depends_on` (`condition: service_healthy`), przekazać im adresy kontenerowe przez zmienne środowiskowe i zamontować nazwany wolumen dla bazy danych SQLite.
3. Zdefiniować usługę `api-gateway` publikującą port `127.0.0.1:8080:8080`.
4. Ukryć bezpośrednie porty obu mikrousług, Redisa oraz portu AMQP (`5672`) przed dostępem z hosta, stosując dla nich `expose` zamiast `ports`.

### Krok 4. Uruchomienie i weryfikacja pełnego przepływu LAB1–LAB6 oraz eksperymenty kontenerowe

Z głównego katalogu własnego repozytorium należy uruchomić całe środowisko:

```powershell
docker compose up --build -d
docker compose ps
```

Następnie należy wykonać i udokumentować sześć scenariuszy weryfikacyjnych:

| Scenariusz | Działanie | Co należy sprawdzić i udokumentować |
|---|---|---|
| **1. Start i rejestracja kontenerów** | `docker compose ps` oraz sprawdzenie panelu `http://127.0.0.1:8761/` | Wszystkie kontenery mają status `Up` / `(healthy)`, a obie usługi własne widnieją w Eurece ze statusem `UP` i nazwami hostów z sieci Docker Compose |
| **2. Izolacja sieciowa usług za bramką** | Wywołanie `curl.exe -i http://127.0.0.1:8080/api/...` oraz próba wywołania `http://127.0.0.1:8101/...` z hosta | Żądanie przez bramkę (`:8080`) zwraca `200 OK` z `X-Gateway: lab4`, natomiast bezpośredni port usługi (`:8101`) jest niedostępny z hosta |
| **3. Przepływ synchroniczny, walidacja i cache (LAB1–LAB4)** | Wykonanie przez bramkę odczytu (MISS → HIT), zapisu, błędnego zapisu (`409`/`422`) oraz wywołania usługa–usługa z LAB3 | Zachowanie wszystkich kodów HTTP, nagłówków `X-Gateway` i `X-Cache` oraz komunikacji między kontenerami usług |
| **4. Przepływ asynchroniczny przez RabbitMQ (LAB5)** | Wywołanie przez bramkę operacji publikującej zdarzenie, sprawdzenie panelu `15672` i uruchomienie konsumpcji | Wiadomość przechodzi przez kontener `rabbitmq`, zostaje przetworzona idempotentnie przez konsumenta i unieważnia cache w kontenerze `redis` |
| **5. Trwałość danych na wolumenie po odtworzeniu kontenerów** | Utworzenie/zmiana rekordu przez bramkę, wykonanie `docker compose down`, a następnie `docker compose up -d` i ponowny odczyt rekordu przez bramkę | Rekord zapisany w SQLite na nazwanym wolumenie przetrwał usunięcie i ponowne utworzenie kontenerów (mimo że cache w Redis uległ wyczyszczeniu i pierwszy odczyt zwraca `X-Cache: MISS`) |
| **6. Restart pojedynczego kontenera usługi** | Wykonanie `docker compose restart <nazwa-uslugi>`, sprawdzenie `docker compose logs --tail=30 <nazwa-uslugi>` i ponowny odczyt przez bramkę | Kontener uruchamia się ponownie, odnawia rejestrację w Eurece i wznawia obsługę żądań bez restartu pozostałych kontenerów |

### Krok 5. Uruchomienie testów automatycznych i finalizacja dokumentacji projektu

Należy uruchomić:

1. **Testy jednostkowe usług (z LAB1–LAB5)** — potwierdzając, że nadal przechodzą w izolacji,
2. **Testy integracyjne przez bramkę (`pytest tests/integration -q`)** — wykonywane z hosta przeciwko skonteneryzowanemu środowisku uruchomionemu przez `docker compose up -d`.

Następnie należy uzupełnić główny plik `README.md` projektu o sekcję LAB6 na podstawie szablonu `README-LAB6-template.md` oraz upewnić się, że cała dokumentacja projektu z LAB1–LAB6 tworzy spójną całość gotową do oceny końcowej.

---

## 6. Diagnostyka typowych problemów w środowisku Docker Compose

| Objaw problemu | Przyczyna i sposób rozwiązania |
|---|---|
| Kontener usługi Python kończy pracę natychmiast po starcie (`Exited (1)`) | Należy sprawdzić logi: `docker compose logs <nazwa-uslugi>`. Częstą przyczyną jest brak uprawnień zapisu do katalogu `/data` dla SQLite albo błędna ścieżka modułu w `CMD` |
| Bramka działa na hoście pod `:8080/health` w LAB4, a w kontenerze połączenie do `127.0.0.1:8080` jest odrzucane | W `application.yml` bramki ustawiono na sztywno `server.address: 127.0.0.1` zamiast `0.0.0.0` wewnątrz kontenera. Należy użyć `address: ${SERVER_ADDRESS:127.0.0.1}` i przekazać `SERVER_ADDRESS: 0.0.0.0` w `compose.yaml` |
| Usługa jest `UP` w Eurece, ale bramka lub druga usługa zwraca `500` / `503` przy wywołaniu | Usługa zarejestrowała w Eurece `INSTANCE_HOST=localhost` albo Uvicorn w kontenerze został uruchomiony bez `--host 0.0.0.0`. Należy ustawić `INSTANCE_HOST` i `INSTANCE_IP` na nazwę usługi z `compose.yaml` |
| Usługa przy starcie zgłasza błąd połączenia z RabbitMQ lub Eureką | Kontener usługi wystartował zanim serwer Eureka lub RabbitMQ zakończył inicjalizację. Należy skonfigurować `healthcheck` oraz `depends_on` z `condition: service_healthy` |
| Dane w bazie SQLite znikają po `docker compose down` i `docker compose up -d` | Ścieżka `DATABASE_URL` wskazuje plik wewnątrz ulotnego systemu plików kontenera (np. `sqlite:///./app.db`) zamiast katalogu zamontowanego z nazwanego wolumenu (np. `sqlite:////data/app.db`) |

---

## 7. Punkty kontrolne, odbiór końcowy i kryteria oceny

### Punkty kontrolne weryfikowane przy odbiorze

| Punkt kontrolny | Oczekiwany dowód wykonania |
|---|---|
| **Punkt A — budowanie i start (`compose.yaml`)** | Całe środowisko projektu uruchamia się poleceniem `docker compose up --build -d`, a wszystkie kontenery osiągają stan `Up` / `(healthy)` |
| **Punkt B — izolacja sieciowa i adresacja** | Dostęp klienta zewnętrznego odbywa się przez port bramki (`127.0.0.1:8080`), porty mikrousług są nieopublikowane na hoście (`expose`), a usługi komunikują się po nazwach z sieci Docker Compose |
| **Punkt C — pełny przepływ LAB1–LAB5 w kontenerach** | Przez skonteneryzowaną bramkę działają: walidacja i reguła biznesowa (LAB1), zapis do SQLite i cache Redis z `X-Cache` (LAB2), wywołanie przez Eurekę (LAB3), routing z `X-Gateway` (LAB4) oraz zdarzenia w RabbitMQ (LAB5) |
| **Punkt D — trwałość wolumenu** | Dane zapisane w bazie SQLite przetrwają wykonanie `docker compose down` oraz ponowne `docker compose up -d` |
| **Punkt E — testy i dokumentacja końcowa** | Przechodzą testy jednostkowe i integracyjne przeciwko kontenerom, a dokumentacja README kompletnie opisuje cały system |

### Pytania do rozmowy technicznej podczas odbioru

Każda osoba powinna umieć samodzielnie odpowiedzieć na pytania:

1. Czym różni się kontener od maszyny wirtualnej i dlaczego obraz budowany wieloetapowo (*multi-stage*) dla bramki jest mniejszy niż obraz z pełnym środowiskiem Maven?
2. Dlaczego wewnątrz kontenera Uvicorn i bramka muszą nasłuchiwać na `0.0.0.0`, podczas gdy na hoście port bramki publikuje się jako `127.0.0.1:8080:8080`?
3. Dlaczego adres `http://127.0.0.1:8761` nie działa z wnętrza kontenera mikrousługi i jaką wartość należy nadać zmiennym `EUREKA_SERVER_URL` oraz `INSTANCE_HOST`?
4. Czym różni się dyrektywa `ports` od `expose` w pliku `compose.yaml` i jak wpływa na bezpieczeństwo architektury z bramką API Gateway?
5. Dlaczego bez nazwanego wolumenu dane w SQLite znikają po `docker compose down`, mimo że nie znikają po samym `docker compose restart`?
6. Jaka jest różnica pomiędzy lokalnym `Docker Compose` a orkiestracją kontenerów w `Kubernetes`?

### Kryteria oceny etapu LAB6

Punktacja zachowuje proporcję z sylabusa przedmiotu: **60 punktów za kod** oraz **40 punktów za dokumentację**.

| Obszar | Oceniany element | Maksimum |
|---|---|---:|
| **Kod** | Poprawne pliki `Dockerfile` i `.dockerignore` dla mikrousług oraz bramki (warstwy cache, multi-stage build, `--host 0.0.0.0`) | 15 |
| **Kod** | Kompletny plik `compose.yaml` z siecią wewnętrzną (`expose` vs `ports`), kontrolami `healthcheck`, `depends_on` i nazwanym wolumenem bazy danych | 20 |
| **Kod** | Działanie wszystkich mechanizmów z LAB1–LAB5 w środowisku kontenerowym (SQLite na wolumenie, Redis, Eureka, API Gateway, RabbitMQ) | 15 |
| **Kod** | Przechodzące testy integracyjne uruchamiane przeciwko skonteneryzowanemu systemowi oraz zachowane testy jednostkowe | 10 |
| **Dokumentacja** | Pełny diagram architektury kontenerowej, tabela usług, portów, zmiennych środowiskowych i wolumenów | 10 |
| **Dokumentacja** | Powtarzalna instrukcja zbudowania, uruchomienia, przetestowania i zatrzymania całego systemu (`up`, `ps`, `logs`, `down`, `down -v`) | 10 |
| **Dokumentacja** | Udokumentowane wyniki sześciu scenariuszy weryfikacyjnych (w tym izolacji portów oraz trwałości wolumenu po `down`/`up`) | 10 |
| **Dokumentacja** | Opis co najmniej dwóch wykorzystanych źródeł dokumentacji (EK_03), podsumowanie wkładu autorów i weryfikacji AI | 10 |
| **Razem** | **Kod 60 pkt + Dokumentacja 40 pkt** | **100** |

**Warunki zaliczenia etapu:** uzyskanie co najmniej **50 punktów** oraz spełnienie wszystkich poniższych warunków minimum:

- cały system własnego projektu (Eureka, Redis, RabbitMQ, dwie mikrousługi domenowe oraz API Gateway) uruchamia się z pliku `compose.yaml` poleceniem `docker compose up --build -d`,
- mikrousługi komunikują się wewnątrz sieci Docker Compose po nazwach usług i nie wymagają ręcznego uruchamiania procesów Uvicorna lub Mavena na hoście,
- baza danych SQLite korzysta z nazwanego wolumenu i zachowuje zapisane dane po wykonaniu `docker compose down` i ponownym `docker compose up -d`,
- przez opublikowany port bramki (`127.0.0.1:8080`) działają przepływy synchroniczne i asynchroniczne z LAB1–LAB5 oraz przechodzą testy integracyjne,
- każda osoba potrafi samodzielnie wyjaśnić konfigurację `Dockerfile` i `compose.yaml` oraz wykonać drobną modyfikację podczas odbioru.

---

## 8. Oznaczenie i przekazanie końcowej wersji projektu (LAB6)

Przed zatwierdzeniem końcowej wersji repozytorium należy zatrzymać kontenery i upewnić się, że w drzewie roboczym nie ma lokalnych baz danych, katalogów `.venv/` ani `target/`:

```powershell
git status
git add .
git diff --cached --stat
git commit -m "feat(lab6): konteneryzacja calego systemu w Docker i Docker Compose"
git tag lab6
git push origin HEAD
git push origin refs/tags/lab6
```

---

## 9. Dokumentacja techniczna

Podczas realizacji zadania należy wykorzystać co najmniej dwa źródła z oficjalnej dokumentacji technicznej (wymaganie **EK_03**) i opisać w README rozwiązany problem, zastosowaną dyrektywę oraz sposób weryfikacji:

- [Dockerfile reference — Docker Docs](https://docs.docker.com/reference/dockerfile/) — instrukcje `FROM`, `WORKDIR`, `COPY`, `RUN`, `USER`, `EXPOSE`, `CMD` oraz `ENTRYPOINT`.
- [Multi-stage builds — Docker Docs](https://docs.docker.com/build/building/multi-stage/) — oddzielenie etapu budowania aplikacji od docelowego obrazu uruchomieniowego.
- [Compose file reference — Services, Networks, Volumes](https://docs.docker.com/reference/compose-file/) — specyfikacja usług, zmiennych środowiskowych, `ports`, `expose`, `volumes` oraz `healthcheck`.
- [Control startup and shutdown order in Compose](https://docs.docker.com/compose/how-tos/startup-order/) — sterowanie kolejnością uruchamiania kontenerów za pomocą `depends_on` i `condition: service_healthy`.
- [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/) — rozwiązywanie nazw DNS usług w domyślnej sieci `Docker Compose`.
- [Persist the DB — Docker Volumes](https://docs.docker.com/get-started/docker-concepts/running-containers/persisting-container-data/) — zachowywanie trwałych danych poza cyklem życia kontenera.
