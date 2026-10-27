# Plan realizacji LAB6 — konteneryzacja systemu mikrousługowego (Docker)

Aktualny zakres zadań, kryteria oceny oraz instrukcję krok po kroku dla studentów określa [instrukcja LAB6](README.md). Wzorcowe pliki `Dockerfile`, `.dockerignore`, konfiguracja `compose.yaml` oraz testy integracyjne znajdują się w [pakiecie pomocniczym](lab6-support.zip).

## 1. Zgodność z sylabusem i domknięcie projektu semestralnego

Laboratorium realizuje szósty temat ćwiczeń laboratoryjnych z sylabusa: **„Konteneryzacja mikrousług przy użyciu silnika Docker”** oraz wiąże praktyczną implementację z zagadnieniami wykładowymi:

- maszyny fizyczne, maszyny wirtualne i kontenery,
- budowanie warstwowe obrazów (`Dockerfile`), obrazy wieloetapowe (*multi-stage*) oraz `.dockerignore`,
- izolacja sieciowa, rozwiązywanie nazw DNS w sieci kontenerowej oraz trwałość danych na wolumenach,
- wzorce Monorepo i Multirepo, rola CI/CD oraz porównanie `Docker Compose` z orkiestracją w `Kubernetes`.

Ćwiczenie spina wszystkie wcześniejsze etapy projektu w jedno powtarzalne środowisko uruchomieniowe:

```text
LAB1 — pierwsza mikrousługa, kontrakt REST, walidacja (422) i reguła biznesowa (409)
  ↓
LAB2 — trwała baza danych SQLite (SQLAlchemy) oraz cache-aside w Redis (X-Cache, TTL, unieważnianie)
  ↓
LAB3 — druga mikrousługa, rejestracja w Eureka Server i wywołanie synchroniczne po nazwie logicznej
  ↓
LAB4 — wspólny punkt wejścia API Gateway kierujący ruch klienta przez nazwy z Eureki do obu usług
  ↓
LAB5 — asynchroniczna publikacja i idempotentna konsumpcja zdarzeń domenowych przez RabbitMQ
  ↓
LAB6 — konteneryzacja wszystkich komponentów, sieć wewnętrzna, trwały wolumen i orkiestracja w Docker Compose
```

## 2. Cele dydaktyczne i efekty kształcenia

Po wykonaniu laboratorium student potrafi:

- przygotować pliki `Dockerfile` i `.dockerignore` dla mikrousług Python/FastAPI oraz bramki Spring Cloud Gateway,
- uruchomić cały system za pomocą jednego pliku `compose.yaml` (`docker compose up --build -d`),
- skonfigurować komunikację między kontenerami po nazwach usług (`eureka`, `redis`, `rabbitmq`, `INSTANCE_HOST`) oraz nasłuchiwanie na `0.0.0.0`,
- odizolować porty wewnętrzne usług (`expose`), publikując na zewnątrz port wejściowy bramki (`127.0.0.1:8080:8080`),
- zachować trwałość bazy SQLite przy użyciu nazwanego wolumenu Docker po usunięciu i odtworzeniu kontenerów,
- zweryfikować kompletny system testami integracyjnymi i udokumentować końcową wersję projektu.

| Efekt | Realizacja na LAB6 | Dowód wykonania |
|---|---|---|
| EK_04 | Skomunikowanie wszystkich komponentów systemu (brama, rejestr, dwie mikrousługi, baza, cache, broker) w sieci Docker Compose | Działające środowisko `compose.yaml`, przechodzące testy integracyjne i diagram architektury |
| EK_03 | Opracowanie `Dockerfile` i `compose.yaml` na podstawie oficjalnej dokumentacji Docker | Zbudowane obrazy, działające kontenery oraz opis dwóch źródeł dokumentacji w README |
| EK_01 | Rozróżnienie maszyn wirtualnych i kontenerów, Monorepo i Multirepo oraz `Docker Compose` i `Kubernetes` | Poprawne wyjaśnienie pojęć oraz decyzji wdrożeniowych podczas odbioru |
| EK_02 | Użycie silnika Docker, Docker Compose, wolumenów, sieci i kontroli `healthcheck` | Odtwarzalna instrukcja zbudowania, uruchomienia i zatrzymania systemu |
| EK_05 | Weryfikacja trwałości danych po odtworzeniu kontenera, izolacji sieciowej portów oraz kolejności startu | Udokumentowane wyniki sześciu eksperymentów kontenerowych |

## 3. Przygotowanie przed zajęciami

Przed rozpoczęciem zajęć należy:

1. Upewnić się, że na komputerach działa Docker Desktop z obsługą `docker compose`.
2. Pobrać wcześniej obrazy bazowe (`python:3.12-slim`, `maven:3.9.9-eclipse-temurin-21`, `eclipse-temurin:21-jre-alpine`, `redis:7-alpine`, `rabbitmq:3.13-management-alpine`), aby nie obciążać sieci podczas zajęć.
3. Zweryfikować uruchomienie przykładu w `lab6-support` poleceniem `docker compose up --build -d` oraz wykonanie testów `pytest tests -q` (`5 passed`).

## 4. Organizacja 120 minut zajęć

| Czas | Etap | Działanie i oczekiwany rezultat |
|---:|---|---|
| 15 min | Pojęcia | VM vs kontenery, warstwy `Dockerfile`, różnica `127.0.0.1` vs DNS w sieci Docker, `ports` vs `expose`, wolumeny, `Docker Compose` vs `Kubernetes` |
| 20 min | Przykład wspólny | Uruchomienie `compose.yaml` z `lab6-support`, sprawdzenie wpisów kontenerowych w Eurece i weryfikacja izolacji portów |
| 15 min | Projekt konfiguracji | Zestawienie usług, adresów DNS, zmiennych środowiskowych (`INSTANCE_HOST`, `SERVER_ADDRESS`) i wolumenu dla własnego projektu |
| 35 min | Implementacja | Przygotowanie `Dockerfile`, `.dockerignore` i głównego `compose.yaml` we własnym repozytorium oraz zbudowanie obrazów |
| 20 min | Weryfikacja i eksperymenty | Sprawdzenie przepływów z LAB1–LAB5 przez bramkę, eksperyment trwałości wolumenu po `docker compose down`/`up` i testy integracyjne |
| 15 min | Odbiór końcowy | Prezentacja działającego środowiska kontenerowego, testów oraz kompletnej dokumentacji projektu |

## 5. Wymagania odbioru i kryteria zaliczenia

- Cały system uruchamia się z `compose.yaml` jednym poleceniem `docker compose up --build -d`.
- Obie mikrousługi własne rejestrują się w Eurece pod swoimi nazwami kontenerowymi i są odizolowane za bramką API Gateway (`expose` zamiast `ports`).
- Baza SQLite korzysta z nazwanego wolumenu i zachowuje dane po `docker compose down` i `docker compose up -d`.
- Przez port bramki (`127.0.0.1:8080`) działają wszystkie mechanizmy z LAB1–LAB5 (walidacja, reguła biznesowa, SQLite, Redis `X-Cache`, Eureka `do_service()`, RabbitMQ events) oraz przechodzą testy integracyjne.
- Dokumentacja README jest kompletna i zawiera wszystkie sekcje wymagane w LAB1–LAB6.
