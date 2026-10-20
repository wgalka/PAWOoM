# LAB3 — Rejestracja i odnajdywanie usług (Eureka)

## Projektowanie aplikacji webowych opartych o mikrousługi

- **Czas:** 120 minut zajęć; konfigurację serwera Eureka i zależności należy przygotować przed zajęciami
- **Technologia:** Python, FastAPI, `py-eureka-client`; Eureka Server uruchamiany z dostarczonego pakietu
- **Forma:** praca indywidualna lub w parach
- **Rezultat:** dwie odrębne usługi zarejestrowane w Eurece oraz wywołanie HTTP odnajdujące usługę po jej nazwie

## 1. Cel i zakres laboratorium

Na tych zajęciach należy rozwinąć projekt z LAB1 i LAB2 o rejestrację oraz odnajdywanie instancji usług w Eurece. Jedna usługa zgłasza swoją nazwę, adres i port do rejestru. Druga pobiera adres usługi z rejestru i wykonuje do niej żądanie HTTP.

Po laboratorium należy umieć:

- odróżnić nazwę usługi od adresu konkretnej jej instancji,
- zarejestrować aplikację w Eurece i wyjaśnić rolę heartbeat,
- odnaleźć usługę po nazwie logicznej zamiast wpisywać jej adres w kodzie,
- wykonać żądanie HTTP do odnalezionej instancji,
- obsłużyć brak usługi lub błąd odpowiedzi zależnej usługi,
- sprawdzić zachowanie integracji testem i udokumentować jej ograniczenia.

### Powiązanie z efektami kształcenia

| Efekt | Ćwiczone działanie | Dowód wykonania |
|---|---|---|
| EK_03 — implementacja funkcjonalności z wykorzystaniem dokumentacji | Integracja dwóch aplikacji z rejestrem i wywołanie przez odnaleziony adres | Kod, testy oraz opis wykorzystanej dokumentacji |
| EK_04 — projektowanie i komunikacja kilku usług | Uzupełnienie planu z LAB1 o drugą usługę, jej właściciela danych i kontrakt HTTP | Dwie działające usługi, osobne odpowiedzialności i scenariusz komunikacji |
| EK_01 — rozumienie pojęć | Rozróżnienie rejestru usług, usługi i jej instancji | Wyjaśnienie przepływu rejestracji i odnajdywania |
| EK_02 — korzystanie z narzędzi | Eureka Server, klient Python, FastAPI i klient HTTP | Powtarzalna konfiguracja i testy |
| EK_05 — analiza jakości rozwiązania | Analiza błędu odnajdywania lub niedostępności zależnej usługi | Zapisany scenariusz błędu i zaobserwowany rezultat |

## 2. Zachowanie ciągłości projektu

Należy kontynuować repozytorium z LAB1 i LAB2. Nie należy przepisywać działającej usługi ani zastępować jej przykładem z paczki. Przed zmianami należy uruchomić dotychczasowe testy i zapisać działający etap w Git.

Należy zachować:

- temat, granice odpowiedzialności i regułę biznesową z LAB1,
- istniejące API i fabrykę aplikacji `create_app()`,
- trwały zapis i cache z LAB2,
- port pierwszej usługi; dla drugiej należy wybrać inny, wolny port,
- oddzielną własność danych każdej usługi.

Drugą usługę należy wybrać zgodnie z planem zapisanym w LAB1. Powinna obsługiwać własny, mały fragment domeny i udostępniać co najmniej jeden użyteczny endpoint. Nie należy tworzyć drugiej aplikacji wyłącznie z endpointem `/health` ani współdzielić tabel pierwszej usługi. Odczyt danych innej usługi należy realizować przez jej API.

W przypadku pracy w parze należy zmieniać role osoby piszącej i sprawdzającej. W dokumentacji należy wskazać wkład każdej osoby. Projekt semestralny nadal wymaga od każdej osoby implementacji co najmniej dwóch różnych mikrousług.

## 3. Pojęcia potrzebne do wykonania zadania

### Rejestr, usługa i instancja

**Rejestr usług** przechowuje informacje o uruchomionych instancjach: nazwę usługi, adres, port i stan. **Usługa** jest logicznym komponentem, np. `LOCKER-SERVICE`. **Instancja** jest konkretnym uruchomionym procesem tej usługi, np. procesem dostępnym pod `127.0.0.1:8101`.

```text
PARCEL-SERVICE ── rejestracja ──> Eureka Server
LOCKER-SERVICE ── rejestracja ──> Eureka Server

PARCEL-SERVICE ── „znajdź LOCKER-SERVICE” ──> Eureka Server
PARCEL-SERVICE ── HTTP do adresu z odpowiedzi ──> LOCKER-SERVICE
```

Rejestr nie przechowuje danych domenowych i nie pośredniczy w każdym żądaniu. Klient pobiera z niego adres instancji, a następnie łączy się z usługą bezpośrednio. Rejestracja i heartbeat nie gwarantują, że instancja odpowie na każde żądanie; adres może być chwilowo nieaktualny, a zależna usługa może zwrócić błąd.

### Konfiguracja a odnajdywanie

Adres serwera Eureka jest konfiguracją środowiska, np. `EUREKA_SERVER_URL`. Adres instancji wywoływanej usługi należy natomiast pobrać z rejestru. W endpointzie biznesowym nie należy wpisywać na stałe `http://localhost:8101` dla zależnej usługi.

W przykładzie wykorzystano `py-eureka-client`, czyli zewnętrzną bibliotekę Python do komunikacji z Eureka Server. Nie jest to oficjalny klient Netflix. Eureka udostępnia API REST dla klientów nie-Java; dokumentację protokołu należy porównać z dokumentacją biblioteki.

## 4. Przygotowanie środowiska

### Pobranie materiałów i uruchomienie Eureka Server

Pobierz [pakiet pomocniczy LAB3](lab3-support.zip) albo pracuj z katalogu [lab3-support](lab3-support/). Pakiet zawiera lokalny projekt Eureka Server, minimalną parę usług FastAPI oraz test przykładowego wywołania.

Do uruchomienia przygotowanego serwera potrzebny jest Docker Desktop z obsługą polecenia `docker compose`. Kontener uruchamia wyłącznie rejestr; własne usługi należy uruchomić lokalnie jako osobne procesy.

W terminalu PowerShell przejdź do katalogu `lab3-support` i uruchom serwer:

```powershell
docker compose up --build -d eureka
```

Budowanie obrazu pobiera zależności Maven i może potrwać przy pierwszym uruchomieniu. Otwórz panel [Eureka](http://localhost:8761/). Serwer należy uruchomić przed usługami i pozostawić aktywnym podczas testu.

Przydatne polecenia:

```powershell
docker compose logs -f eureka
docker compose stop eureka
docker compose start eureka
```

Po ćwiczeniu serwer można zatrzymać poleceniem `docker compose down` wykonanym w katalogu `lab3-support`.

### Instalacja zależności przykładu

W katalogu `lab3-support` należy utworzyć środowisko Pythona i zainstalować zależności:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Pakiet pomocniczy przypina `py-eureka-client` do wersji `0.13.3`, aby przykład był odtwarzalny. W projekcie studenta należy dodać tę zależność do `requirements.txt` i używać tej samej wersji podczas laboratorium.

### Uruchomienie przykładu wspólnego

Przykład pokazuje rejestrację `LOCKER-SERVICE` i `PARCEL-SERVICE`. `PARCEL-SERVICE` wywołuje endpoint paczkomatu, odnajdując `LOCKER-SERVICE` przez Eurekę.

W pierwszym terminalu, w katalogu `lab3-support`, uruchom:

```powershell
$env:EUREKA_SERVER_URL = 'http://127.0.0.1:8761'
$env:SERVICE_PORT = '8101'
.\.venv\Scripts\python.exe -m uvicorn demo.locker_service.app.main:app --port 8101
```

W drugim terminalu, również w katalogu `lab3-support`, uruchom:

```powershell
$env:EUREKA_SERVER_URL = 'http://127.0.0.1:8761'
$env:SERVICE_PORT = '8102'
.\.venv\Scripts\python.exe -m uvicorn demo.parcel_service.app.main:app --port 8102
```

Należy poczekać, aż panel Eureka pokaże obie usługi jako `UP`. Następnie w trzecim terminalu sprawdź odpowiedź bezpośrednią i wywołanie przez drugą usługę:

```powershell
Invoke-RestMethod http://127.0.0.1:8101/lockers/KRK-1024
Invoke-RestMethod http://127.0.0.1:8102/delivery-check/KRK-1024
```

Drugie żądanie przechodzi przez `PARCEL-SERVICE`, która pobiera adres `LOCKER-SERVICE` z Eureki i dopiero wtedy wysyła HTTP. Dla nieznanego paczkomatu żądanie `GET /delivery-check/UNKNOWN` powinno zwrócić `404`.

## 5. Analiza przykładu przed implementacją

Na podstawie kodu przykładu należy wskazać:

1. Jakie informacje wysyła usługa podczas rejestracji?
2. Po co klient wysyła heartbeat?
3. Który adres jest konfiguracją, a który jest pobierany z rejestru?
4. Czy żądanie biznesowe przechodzi przez Eurekę?
5. Która usługa jest właścicielem informacji o paczkomacie?
6. Co zwraca `PARCEL-SERVICE`, gdy `LOCKER-SERVICE` nie odpowie?

Przykład jest krótki i służy do rozpoznania mechanizmu. Nie trzeba przepisywać go przed rozpoczęciem własnej implementacji.

## 6. Rejestracja i odnajdywanie usług we własnym projekcie

### Krok 1 — weryfikacja wersji z LAB2

Należy uruchomić dotychczasowe testy i potwierdzić działanie pierwszej usługi, bazy oraz cache. Następnie należy utworzyć commit etapu przed zmianami, np.:

```powershell
git status
git add app tests requirements.txt README.md
git diff --cached --stat
git commit -m "chore(lab2): zapisz dzialajacy etap przed LAB3"
```

Jeżeli etap LAB2 jest już zatwierdzony, nowy commit nie jest potrzebny.

### Krok 2 — wyznaczenie granicy drugiej usługi

Należy wrócić do podziału domeny i kontraktu z LAB1. Dla obu usług trzeba zapisać w tabeli:

| Usługa | Odpowiedzialność | Właściciel danych | Endpoint potrzebny do scenariusza | Port |
|---|---|---|---|---:|
| Pierwsza usługa | … | … | … | dotychczasowy |
| Druga usługa | … | … | … | wolny port |

Należy wybrać taki scenariusz, w którym jedna usługa potrzebuje informacji należącej do drugiej. Nie należy kopiować jej tabel ani bezpośrednio łączyć się z jej bazą.

### Krok 3 — przygotowanie drugiej usługi

Należy utworzyć osobną aplikację FastAPI z własnym `create_app()`, własną nazwą, portem i co najmniej jednym endpointem domenowym. Na potrzeby etapu endpoint może korzystać z małego lokalnego zestawu danych, jeżeli persystencja drugiej usługi nie jest jeszcze zaimplementowana. Dane pierwszej usługi pozostają w jej bazie.

Obie aplikacje należy uruchamiać jako odrębne procesy. W konfiguracji każdej należy ustawić:

- nazwę logiczną usługi,
- port nasłuchiwania,
- adres serwera Eureka,
- adres IP instancji osiągalny dla drugiej usługi.

Lokalnie można użyć adresu `127.0.0.1`; adresu zarejestrowanego w Eurece nie należy zgadywać, jeżeli usługi są uruchamiane w innym środowisku.

### Krok 4 — rejestracja cyklu życia aplikacji

Należy utworzyć klienta Eureka i uruchamiać go w cyklu życia FastAPI. Przykład korzysta z asynchronicznego klienta `EurekaClient`:

```python
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from py_eureka_client.eureka_client import EurekaClient

client = EurekaClient(
    eureka_server=os.getenv("EUREKA_SERVER_URL", "http://127.0.0.1:8761"),
    eureka_context="/eureka",
    app_name="LOCKER-SERVICE",
    instance_ip=os.getenv("INSTANCE_IP", "127.0.0.1"),
    instance_host=os.getenv("INSTANCE_HOST", "localhost"),
    instance_port=int(os.getenv("SERVICE_PORT", "8101")),
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await client.start()
    app.state.eureka_client = client
    try:
        yield
    finally:
        await client.stop()

app = FastAPI(lifespan=lifespan)
```

Nazwę, URL rejestru, IP i port należy pobierać z konfiguracji środowiska zamiast utrwalać w kodzie produkcyjnym. Dla przygotowanego serwera Spring Cloud należy podać adres bazowy, np. `http://127.0.0.1:8761`, a ścieżkę API ustawić jako `eureka_context="/eureka"`. Fragment pokazuje jedynie kolejność: utworzenie klienta, start przy uruchamianiu aplikacji i stop przy jej zamykaniu.

Każda usługa powinna zarejestrować własną nazwę i port. Należy potwierdzić w panelu Eureki, że obie instancje mają stan `UP`.

### Krok 5 — wykonanie żądania przez nazwę usługi

W wybranym endpointzie należy pobrać dane z drugiej usługi przez klienta Eureka. Dla przykładu:

```python
result = await app.state.eureka_client.do_service(
    "LOCKER-SERVICE",
    "/lockers/KRK-1024",
    return_type="json",
)
```

Należy zastąpić nazwę i ścieżkę własnym kontraktem. Nie należy wpisywać adresu `http://127.0.0.1:8101` w kodzie endpointu. Adres Eureki pozostaje parametrem konfiguracyjnym, a adres wywoływanej usługi pochodzi z rejestru.

Jeżeli zależna usługa zwraca błąd lub nie jest dostępna, API wywołującej usługi powinno zwrócić kontrolowany kod HTTP, np. `502` albo `503`, bez ujawniania tracebacku i sekretów. Nie należy dodawać na tym etapie pełnego circuit breakera ani mechanizmu ponawiania żądań.

### Krok 6 — sprawdzenie odporności na błąd zależności

Należy wykonać dwa testy ręczne:

1. Przy obu usługach działających sprawdzić poprawny przepływ i odpowiedź.
2. Zatrzymać usługę wywoływaną, wywołać endpoint zależny i zapisać kod oraz treść odpowiedzi.

Po zatrzymaniu proces może przez pewien czas pozostawać widoczny w rejestrze, ponieważ Eureka używa heartbeatów i dzierżawy instancji. Nie należy uznawać samej obecności nazwy w panelu za dowód, że usługa odpowiada. Należy opisać czas obserwacji oraz faktyczny rezultat żądania.

Po teście należy ponownie uruchomić usługę i potwierdzić, że przepływ działa.

### Krok 7 — testy automatyczne

Testy jednostkowe nie powinny wymagać działającego Eureka Server. Należy wstrzyknąć zamiennik klienta, który udostępnia asynchroniczne metody `start()`, `stop()` i `do_service()`. Test powinien sprawdzać:

- kod i treść odpowiedzi endpointu wywołującego,
- nazwę logiczną oraz ścieżkę przekazane do klienta,
- kontrolowaną odpowiedź przy błędzie zależności.

Test rzeczywistej rejestracji i odnajdywania należy wykonać ręcznie z uruchomioną Eureką. Nie należy wykonywać połączeń sieciowych w podstawowym zestawie testów `pytest`.

Przykład testu z zamiennikiem znajduje się w `lab3-support/demo/tests/test_parcel_service.py`.

### Krok 8 — aktualizacja dokumentacji

Do README własnego projektu należy dopisać sekcje z [szablonu dokumentacji LAB3](lab3-support/demo/README-LAB3-template.md). Dokumentacja powinna opisywać oba serwisy, ich właścicieli danych, porty, nazwy rejestrowane w Eurece, konfigurację, endpoint komunikacji i rzeczywiste wyniki testów.

## 7. Zakres poza laboratorium

W tym etapie nie należy dodawać API Gateway, RabbitMQ, komunikacji asynchronicznej, Sagi, klastra Eureki, własnych obrazów kontenerowych ani pełnego Docker Compose dla wszystkich usług. Docker Compose z pakietu służy wyłącznie do uruchomienia przygotowanego rejestru. Nie należy zmieniać modelu persystencji ani cache z LAB2, jeśli nie jest to konieczne do zachowania działania istniejącego API.

## 8. Punkty kontrolne i kryteria zaliczenia etapu

### Punkty kontrolne

| Punkt | Oczekiwany rezultat |
|---|---|
| A — ciągłość | Testy z LAB2 przechodzą, działający etap został zachowany w Git |
| B — granice usług | Dwie usługi mają różne odpowiedzialności, osobne porty i właścicieli danych |
| C — rejestracja | Eureka pokazuje obie instancje jako `UP` |
| D — odnajdywanie | Jedna usługa wywołuje drugą przez nazwę logiczną pobraną z rejestru |
| E — błąd | Niedostępność zależnej usługi daje kontrolowaną odpowiedź i została opisana |
| F — weryfikacja | Testy jednostkowe przechodzą, test ręczny integracji został wykonany |

### Kryteria oceny

| Obszar | Element | Punkty |
|---|---|---:|
| Kod | Zachowanie pierwszej usługi z LAB2: API, baza, cache i testy | 10 |
| Kod | Druga odrębna usługa z własną odpowiedzialnością i endpointem domenowym | 15 |
| Kod | Rejestracja obu usług, konfiguracja adresów i poprawny cykl życia klienta | 15 |
| Kod | Wywołanie przez nazwę usługi oraz kontrola błędów zależności | 10 |
| Kod | Testy izolowane od prawdziwego rejestru | 10 |
| Dokumentacja | Granice usług, własność danych, kontrakt i konfiguracja | 10 |
| Dokumentacja | Kroki uruchomienia, testu i resetu środowiska | 10 |
| Dokumentacja | Wyniki awarii, ograniczenia i wykorzystana dokumentacja | 10 |
| Dokumentacja | Wkład autorów i wykorzystanie AI | 10 |
| **Razem** | **Kod 60 + dokumentacja 40** | **100** |

**Zaliczenie etapu:** minimum 50 punktów oraz spełnienie wszystkich warunków minimum:

- pierwsza usługa nadal przechowuje i udostępnia dane zgodnie z etapem LAB2,
- druga usługa ma odrębny endpoint domenowy i nie zapisuje bezpośrednio do bazy pierwszej,
- obie usługi rejestrują się w Eurece pod różnymi nazwami i portami,
- co najmniej jedno żądanie HTTP odnajduje zależność przez nazwę logiczną,
- błąd zależności jest obsłużony kontrolowanym kodem HTTP,
- przechodzą testy jednostkowe, a ręczny test z Eureką jest udokumentowany,
- każda osoba potrafi wyjaśnić rejestrację, odnajdywanie i granice obu usług.

## 9. Oznaczenie i przekazanie wersji projektu LAB3

Należy oddać to samo repozytorium rozwijane w LAB1 i LAB2. Przed dodaniem plików do Git należy sprawdzić, czy nie zawierają sekretów, lokalnych baz, środowiska wirtualnego ani cache Pythona.

```powershell
git status
git add .
git diff --cached --stat
git commit -m "feat(lab3): rejestracja i odnajdywanie usług przez Eurekę"
git tag lab3
git push origin HEAD
git push origin refs/tags/lab3
```

Jeżeli tag `lab3` już istnieje, nie należy nadpisywać go siłą. Należy uzgodnić oznaczenie poprawionej wersji. Nie należy wysyłać lokalnych konfiguracji, haseł ani plików `.env`.

## 10. Dokumentacja techniczna

W README należy podać wersje użytych narzędzi oraz dwa wykorzystane źródła: dokumentację biblioteki i dokumentację protokołu lub serwera. W przypadku informacji o cyklu życia FastAPI należy wskazać wykorzystane źródło dotyczące lifespan.

Prefix API zależy od implementacji serwera. Dokumentacja REST Netflix pokazuje ścieżkę `/eureka/v2`; przygotowany serwer Spring Cloud udostępnia endpointy pod `/eureka/*`. W kliencie przykładowym należy ustawić `eureka_context="/eureka"` i jako `EUREKA_SERVER_URL` podać adres bazowy serwera.

- [Eureka REST operations — Netflix](https://github.com/Netflix/eureka/wiki/Eureka-REST-operations) — rejestracja, heartbeat, odnajdywanie i wyrejestrowanie klienta nie-Java.
- [Eureka Server — Spring Cloud Netflix](https://docs.spring.io/spring-cloud-netflix/reference/spring-cloud-netflix.html) — konfiguracja serwera i endpointów rejestru.
- [Service Registration and Discovery — Spring](https://spring.io/guides/gs/service-registration-and-discovery/) — przykład rejestru i dwóch usług komunikujących się po nazwie.
- [py-eureka-client — dokumentacja projektu](https://github.com/keijack/python-eureka-client) oraz [wydanie na PyPI](https://pypi.org/project/py-eureka-client/0.13.3/) — integracja klienta Python, w tym API asynchroniczne.
- [Lifespan Events — FastAPI](https://fastapi.tiangolo.com/advanced/events/) — uruchamianie i zamykanie klienta razem z aplikacją.

Nie należy traktować materiałów biblioteki jako źródła oficjalnej specyfikacji Netflix. Przed użyciem kodu z dokumentacji należy sprawdzić zgodność wersji i uruchomić testy.
