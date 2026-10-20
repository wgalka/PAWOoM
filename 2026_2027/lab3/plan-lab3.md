# Plan realizacji LAB3 — rejestracja i odnajdywanie usług

Aktualny zakres, kryteria i sposób pracy studentów określa [instrukcja LAB3](README.md). Kod demonstracyjny, lokalny serwer Eureka i szablon dokumentacji znajdują się w [pakiecie pomocniczym](lab3-support.zip).

## Zakres tematyczny

Laboratorium realizuje trzeci temat z sylabusa: **rejestrację usług z użyciem Eureka**. Kontynuuje projekt z LAB1 i LAB2. Student zachowuje pierwszą usługę, dodaje drugą usługę wynikającą z podziału domeny i uruchamia komunikację HTTP, w której adres odbiorcy jest odnajdywany po nazwie logicznej.

Minimalny przepływ do uzyskania:

```text
Usługa A ── rejestracja + heartbeat ──> Eureka
Usługa B ── rejestracja + heartbeat ──> Eureka
Usługa B ── odnajdź nazwę A ──> Eureka
Usługa B ── HTTP do adresu instancji A ──> Usługa A
```

Każda usługa pozostaje właścicielem swoich danych. Rejestr nie przechowuje danych domenowych i nie jest proxy dla żądań biznesowych.

## Cele i efekty kształcenia

Po laboratorium student powinien:

- rozumieć różnicę pomiędzy usługą, instancją i wpisem w rejestrze,
- zarejestrować obie usługi i zamykać klienta Eureka wraz z procesem aplikacji,
- wywołać zależną usługę przez nazwę logiczną,
- zachować granice i własność danych ustalone w LAB1 i LAB2,
- kontrolowanie obsłużyć brak zależności,
- napisać izolowany test wywołującej usługi i udokumentować test integracyjny.

| Efekt | Realizacja | Dowód |
|---|---|---|
| EK_03 | Integracja z API Eureka oraz HTTP na podstawie dokumentacji | Kod, test i źródła w README |
| EK_04 | Implementacja drugiej usługi i komunikacji przez kontrakt | Dwie usługi, osobni właściciele danych i test przepływu |
| EK_01 | Wyjaśnienie rejestracji, dzierżawy, heartbeatów i odnajdywania | Odpowiedzi na pytania kontrolne |
| EK_02 | Użycie FastAPI, `py-eureka-client` i lokalnego Eureka Server | Powtarzalna konfiguracja |
| EK_05 | Ocena błędu zależności i opóźnienia wygaszania wpisu | Wyniki eksperymentu i ograniczenia |

## Przygotowanie prowadzącego

Przed zajęciami należy:

1. Zbudować obraz serwera Eureka poleceniem `docker compose up --build -d eureka` w katalogu `lab3-support`.
2. Zweryfikować dostęp do panelu `http://localhost:8761/` i API rejestru.
3. Utworzyć środowisko Pythona w `lab3-support` i zainstalować `requirements.txt`.
4. Uruchomić obie usługi demonstracyjne na portach `8101` i `8102`.
5. Sprawdzić, czy dashboard pokazuje obie instancje oraz czy `/delivery-check/KRK-1024` zwraca dane z `LOCKER-SERVICE`.
6. Sprawdzić `pytest -q` i działanie testu z zamiennikiem klienta.

Docker Compose uruchamia wyłącznie przygotowaną infrastrukturę Eureka. Studenci nie projektują obrazu ani pełnego środowiska kontenerowego. Należy uprzedzić o wymaganiu Docker Desktop i przygotowaniu obrazu przed zajęciami, aby pobieranie zależności nie zajęło czasu na laboratorium.

## Organizacja 120 minut

| Czas | Etap | Działanie i rezultat |
|---:|---|---|
| 10 min | Pojęcia | Usługa, instancja, rejestr, heartbeat i różnica między discovery a gateway |
| 15 min | Przykład | Dashboard, dwie usługi FastAPI, call po nazwie i wskazanie kodu klienta |
| 15 min | Projekt | Powrót do granic i kontraktu z LAB1; wybór drugiej usługi i jej endpointu |
| 40 min | Implementacja | Osobny proces, port i rejestracja każdej usługi; żądanie przez nazwę logiczną |
| 25 min | Weryfikacja | Test jednostkowy z fake klientem, test ręczny, kontrolowana awaria zależności |
| 10 min | Odbiór | Wskazanie dowodów, dokumentacja i zapis etapu w Git |
| 5 min | Rezerwa | Opóźnienie rejestracji lub różnice konfiguracji środowiska |

## Prowadzenie przykładu wspólnego

Przykład korzysta z `Locker Service` znanej z LAB1. Minimalny `Parcel Service` pyta o paczkomat przez `LOCKER-SERVICE`. Należy pokazać tylko:

- dwa wpisy `UP` w panelu Eureka,
- konfigurację nazwy i portu instancji,
- start i stop `EurekaClient` w lifespan FastAPI,
- wywołanie asynchroniczne `do_service()` z nazwą usługi i ścieżką,
- odpowiedź błędu po zatrzymaniu zależnej usługi.

Nie należy omawiać klastra Eureka, mechanizmów wysokiej dostępności, wyboru równoważenia ruchu, API Gateway ani komunikacji asynchronicznej.

## Główna praca studentów

Student powinien najpierw uruchomić własną usługę z LAB2 i potwierdzić niezmienność testów. Następnie powinien zapisać commit, zaprojektować drugą granicę usług zgodną z planem LAB1, uruchomić osobną aplikację na innym porcie, zarejestrować obie usługi i zaimplementować jeden przepływ HTTP przez Eureka.

Druga usługa powinna mieć co najmniej jeden endpoint domenowy. Jej persystencja nie jest kryterium LAB3, o ile nie wymaga jej scenariusz domenowy; nie wolno jednak współdzielić bazy pierwszej usługi. Integracja powinna korzystać z API właściciela danych.

Test automatyczny powinien wstrzykiwać zamiennik klienta Eureka. Ręczny test integracyjny powinien korzystać z prawdziwego rejestru. W eksperymencie awarii należy oddzielić dostępność rejestru od dostępności usługi: wpis może pozostać w rejestrze do czasu wygaśnięcia dzierżawy, mimo że połączenie z procesem już nie działa.

## Minimalne wymagania odbioru

- Wszystkie testy z LAB2 nadal przechodzą.
- Są dwie osobno uruchamiane aplikacje z własnymi nazwami i portami.
- Obie aplikacje rejestrują instancje w Eureka.
- Jedna usługa odnajduje drugą po nazwie logicznej i wykonuje żądanie HTTP.
- Błąd zależności nie zwraca tracebacku ani nie pozostawia operacji w nieokreślonym stanie.
- Test jednostkowy nie wymaga serwera Eureka.
- README zawiera konfigurację, kontrakt, test oraz wynik scenariusza awarii.
- Każda osoba potrafi wskazać własny wkład i wyjaśnić przepływ.

## Typowe problemy i wskazówki

| Objaw | Co sprawdzić |
|---|---|
| Brak panelu Eureka | Czy kontener działa, czy port `8761` jest wolny i czy budowanie obrazu się zakończyło |
| Usługa nie pojawia się jako `UP` | URL API Eureka, nazwę usługi, port procesu i logi klienta |
| Rejestr pokazuje usługę, lecz wywołanie nie działa | Czy zarejestrowane IP jest osiągalne z procesu wywołującego i czy port jest zgodny z Uvicornem |
| Port zajęty | Czy każda aplikacja ma inny port; należy ustawić zgodny port klienta i serwera HTTP |
| Pierwsze odnajdywanie nie działa | Czy obie usługi uruchomiono po serwerze i czy panel pokazuje ich stan `UP`; odświeżenie rejestru może być okresowe |
| Aplikacja odpowiada, ale Eureka nadal pokazuje instancję | Wpis jest dzierżawą odnawianą heartbeatami; nie jest to aktywny test każdego żądania |
| Testy wymagają uruchomionej Eureki | Należy wstrzyknąć zamiennik klienta i odseparować test jednostkowy od ręcznego testu integracji |

## Poza zakresem

W ramach LAB3 nie implementuje się Gateway, RabbitMQ, Sagi, klastra Eureki, własnych obrazów usług ani pełnego Docker Compose dla systemu. Nie przebudowuje się persystencji i cache z LAB2.
