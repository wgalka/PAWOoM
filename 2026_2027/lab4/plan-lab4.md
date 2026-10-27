# Plan realizacji LAB4 — konfiguracja wspólnego punktu wejścia (API Gateway)

Aktualny zakres zadań, kryteria oceny oraz instrukcję krok po kroku dla studentów określa [instrukcja LAB4](README.md). Konfiguracja startowa bramki, testy integracyjne przykładu oraz szablon dokumentacji znajdują się w [pakiecie pomocniczym](lab4-support.zip).

## 1. Zgodność z sylabusem i ciągłość projektu

Laboratorium realizuje czwarty temat ćwiczeń laboratoryjnych z sylabusa: **„Konfiguracja i uruchomienie API Gateway”** oraz rozwija zagadnienia wykładowe dotyczące wzorców **API Gateway i BFF**, kontraktów API oraz separacji odpowiedzialności.

Ćwiczenie stanowi bezpośrednią kontynuację projektu rozwijanego w LAB1–LAB3:

```text
LAB1 — pierwsza mikrousługa, kontrakt REST, walidacja (422) i reguła biznesowa (409)
  ↓
LAB2 — trwała baza danych SQLite (SQLAlchemy) oraz cache-aside w Redis (X-Cache, TTL, unieważnianie)
  ↓
LAB3 — druga mikrousługa, rejestracja w Eureka Server i wywołanie usługa–usługa po nazwie logicznej
  ↓
LAB4 — wspólny punkt wejścia API Gateway kierujący ruch klienta przez nazwy z Eureki do obu usług
```

Docelowy przepływ weryfikowany na laboratorium:

```text
Klient HTTP ── /api/... ──> API Gateway (:8080)
                                ├── lb://USŁUGA-1 ──> Usługa 1 (:8101) ──> SQLite + Redis (LAB2)
                                └── lb://USŁUGA-2 ──> Usługa 2 (:8102) ── HTTP (LAB3) ──> Usługa 1 (:8101)
```

Bramka pobiera rejestr z Eureki, lecz nie przejmuje logiki biznesowej usług, nie łączy się z ich bazami danych i nie pośredniczy w wewnętrznym wywołaniu usługa–usługa z LAB3.

## 2. Cele dydaktyczne i efekty kształcenia

Po wykonaniu laboratorium student potrafi:

- odróżnić rolę API Gateway od rejestru Eureka, wzorca BFF i mikrousług domenowych,
- zaprojektować publiczny kontrakt wejściowy (`/api/...`) i odseparować go od technicznych endpointów wewnętrznych,
- skonfigurować trasy (`routes`), warunki dopasowania (`Path`), filtry (`StripPrefix`, `AddResponseHeader`) oraz integrację z Eureką (`lb://`),
- zweryfikować przez bramkę wszystkie dotychczasowe mechanizmy projektu (odczyt z cache `X-Cache`, zapis do SQLite z unieważnieniem cache, walidację `422`, regułę biznesową `409` oraz przepływ między usługami z LAB3),
- rozróżnić przyczyny błędów HTTP (`404` brak trasy vs `404` brak zasobu, `502`/`503` z usługi wywołującej vs `503`/`504`/`500` z bramki oraz odmowę połączenia TCP),
- przygotować powtarzalne testy integracyjne wykonywane przez port bramki.

| Efekt | Realizacja na LAB4 | Dowód wykonania |
|---|---|---|
| EK_04 | Skomunikowanie podstawowych komponentów systemu (brama, rejestr mikrousług, dwie mikrousługi) | Działający układ procesów, tabela tras i diagram architektury |
| EK_03 | Konfiguracja Spring Cloud Gateway i testów HTTPX na podstawie oficjalnej dokumentacji | Plik `application.yml`, cztery własne testy integracyjne i opis dwóch źródeł dokumentacji |
| EK_01 | Rozróżnienie routingu brzegowego, service discovery, BFF i logiki domenowej | Poprawne odpowiedzi podczas odbioru i opis granic odpowiedzialności |
| EK_02 | Użycie Spring Cloud Gateway, Eureka, FastAPI, SQLite, Redis i pytest/HTTPX | Odtwarzalna instrukcja uruchomienia i weryfikacji |
| EK_05 | Analiza skutków awarii usług i bramki oraz opóźnień odświeżania rejestru | Udokumentowane wyniki sześciu eksperymentów awarii |

## 3. Przygotowanie przed zajęciami

Przed rozpoczęciem zajęć należy:

1. Zweryfikować dostępność JDK 21 (`java -version`) oraz Apache Maven 3.9.x (`mvn -version`).
2. Uruchomić Eureka Server i dwie usługi demonstracyjne z `lab3-support` na portach `8761`, `8101` i `8102`.
3. Uruchomić raz bramkę w katalogu `lab4-support/gateway` poleceniem `mvn spring-boot:run`, aby Maven pobrał zależności do lokalnego repozytorium przed zajęciami.
4. Sprawdzić wywołania `http://127.0.0.1:8080/health`, `/api/lockers/KRK-1024`, `/api/delivery-check/KRK-1024` oraz uruchomienie `pytest tests -q` (`5 passed`).

## 4. Organizacja 120 minut zajęć

| Czas | Etap | Działanie i oczekiwany rezultat |
|---:|---|---|
| 15 min | Pojęcia | Porównanie API Gateway, Eureki, BFF i usług domenowych; analiza struktury trasy (`uri`, `Path`, `StripPrefix`) |
| 20 min | Przykład wspólny | Uruchomienie bramki z `lab4-support` nad demo z LAB3, analiza dwóch różnych błędów `404` i eksperyment ze `StripPrefix=2` |
| 15 min | Decyzje projektowe | Zaprojektowanie tabeli tras własnego projektu i wybór endpointów wystawianych przez `/api/...` |
| 35 min | Konfiguracja projektu | Włączenie katalogu `gateway` do repozytorium studenta i konfiguracja tras `lb://` do obu własnych usług |
| 25 min | Weryfikacja i awarie | Sprawdzenie odczytu (`X-Gateway` + `X-Cache`), zapisu, błędów `409`/`422`, przepływu z LAB3 oraz scenariuszy zatrzymania procesów |
| 10 min | Odbiór | Prezentacja działających tras własnego projektu i drobna modyfikacja konfiguracji na żywo |

## 5. Wymagania odbioru i kryteria zaliczenia

- Zachowane są obie usługi z LAB1–LAB3 wraz z bazą SQLite, cache Redis, rejestracją w Eurece i dotychczasowymi testami jednostkowymi.
- Bramka definiuje co najmniej dwie jawne trasy kierujące ruch przez `lb://NAZWA-USŁUGI` do dwóch różnych usług.
- Przez bramkę przechodzą: odczyt z obu usług, zapis modyfikujący stan i unieważniający cache oraz błędy `404`, `409`, `422`.
- Bramka nie zawiera logiki domenowej ani połączeń z bazą danych usług.
- Przechodzą co najmniej cztery własne testy integracyjne w osobnym katalogu testów integracyjnych.
- Dokumentacja zawiera tabelę tras, diagram, instrukcję uruchomienia, wyniki sześciu eksperymentów awarii oraz opis co najmniej dwóch wykorzystanych źródeł dokumentacji (EK_03).
