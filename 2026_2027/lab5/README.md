# LAB5 — Asynchroniczna komunikacja między mikrousługami (RabbitMQ)

## Projektowanie aplikacji webowych opartych o mikrousługi

- **Czas:** 120 minut zajęć; obraz brokera RabbitMQ oraz zależności Pythona należy przygotować przed zajęciami
- **Technologia:** Python + FastAPI + `pika` (AMQP 0-9-1), RabbitMQ Management, Eureka Server (z LAB3), Spring Cloud Gateway (z LAB4) oraz SQLite i Redis (z LAB2)
- **Forma:** praca indywidualna lub w parach, w dotychczasowym repozytorium projektu z LAB1–LAB4
- **Rezultat:** przepływ zdarzeniowy pomiędzy dwiema usługami za pośrednictwem brokera RabbitMQ, zintegrowany z bramką API Gateway, rejestrem Eureka, bazą danych i cache, wraz z obsługą idempotentności, potwierdzeń `ACK` oraz zestawem testów automatycznych

---

## 1. Cel i zakres laboratorium

W tym ćwiczeniu należy zrealizować piąty temat laboratoryjny z sylabusa: **„Komunikacja pomiędzy mikrousługami — wykorzystanie brokera wiadomości RabbitMQ”**, rozwijając system budowany w LAB1, LAB2, LAB3 i LAB4. Do działającego środowiska składającego się z bramki API Gateway, rejestru Eureka oraz dwóch mikrousług (z bazą SQLite i cache Redis) należy dodać broker wiadomości RabbitMQ, zaimplementować publikację oraz konsumpcję zdarzenia domenowego i zbadać zachowanie systemu w warunkach spójności ostatecznej (*eventual consistency*) oraz awarii komponentów.

Po wykonaniu laboratorium należy umieć:

- odróżnić komunikację synchroniczną (HTTP/REST z LAB3) od komunikacji asynchronicznej opartej o zdarzenia i kolejki wiadomości (RabbitMQ),
- wyjaśnić rolę elementów modelu AMQP 0-9-1: producenta (*Publisher*), wymiennika (*Exchange*), klucza routingu (*Routing Key*), powiązania (*Binding*), kolejki (*Queue*) oraz konsumenta (*Consumer*),
- powiązać transakcję bazodanową (z LAB2) z publikacją zdarzenia oraz odróżnić choreografię od orkiestracji w ramach wzorca Saga,
- opublikować trwałe zdarzenie domenowe w formacie JSON po pomyślnym przejściu walidacji i reguły biznesowej (z LAB1),
- odebrać wiadomość z kolejki RabbitMQ z jawnym potwierdzeniem (`basic_ack`), zaktualizować stan w bazie danych i unieważnić wpis w cache Redis (z LAB2),
- zapewnić idempotentność konsumenta po identyfikatorze `event_id` na wypadek ponownego dostarczenia wiadomości (*at-least-once delivery*) oraz stosować prawo Postela przy odczycie ładunku zdarzenia,
- wykazać eksperymentalnie różnicę między zatrzymaniem usługi wywoływanej synchronicznie (`503` w LAB3) a zatrzymaniem konsumenta wiadomości (buforowanie zdarzenia w kolejce RabbitMQ i przetworzenie po powrocie usługi),
- przetestować komunikację asynchroniczną za pomocą izolowanych testów jednostkowych oraz testów integracyjnych przez API Gateway.

### Powiązanie z efektami kształcenia

| Efekt | Ćwiczone działanie na LAB5 | Dowód wykonania |
|---|---|---|
| EK_04 — projektowanie systemu z kilku mikrousług i skomunikowanie komponentów | Połączenie komunikacji synchronicznej (API Gateway, Eureka) oraz asynchronicznej (RabbitMQ) pomiędzy dwiema usługami | Działający przepływ publikacji i konsumpcji zdarzenia wyzwalany przez API Gateway, diagram i tabela kontraktu zdarzenia |
| EK_03 — implementacja funkcjonalności z wykorzystaniem dokumentacji | Konfiguracja wymiennika, kolejki, publikacji i potwierdzeń `ACK`/`NACK` w `pika` na podstawie oficjalnej dokumentacji | Działający kod producenta i konsumenta, przechodzące testy automatyczne oraz opis dwóch źródeł dokumentacji |
| EK_01 — rozumienie pojęć architektury mikrousługowej | Rozróżnienie komunikacji synchronicznej i asynchronicznej, choreografii i orkiestracji (Saga), spójności ostatecznej i idempotentności | Poprawne wyjaśnienie decyzji architektonicznych oraz odpowiedzi podczas odbioru |
| EK_02 — dobór i wykorzystanie narzędzi | Użycie RabbitMQ Server i panelu Management, biblioteki `pika`, FastAPI, SQLite, Redis, Eureki i Spring Cloud Gateway | Powtarzalna konfiguracja uruchomieniowa i weryfikacja stanu kolejek |
| EK_05 — analiza wyzwań, jakości i ograniczeń rozwiązania | Badanie skutków niedostępności konsumenta, niedostępności brokera, duplikatów wiadomości oraz ryzyka rozbieżności między commitem bazy a publikacją | Udokumentowane wyniki eksperymentów awarii i wnioski projektowe |

---

## 2. Zachowanie ciągłości projektu z LAB1–LAB4

Pracę należy kontynuować w dotychczasowym repozytorium Git i w tej samej domenie biznesowej. Przed rozpoczęciem modyfikacji należy uruchomić dotychczasowe testy jednostkowe i integracyjne z LAB1–LAB4 oraz zapisać działający stan w Git.

### Zestawienie ewolucji systemu w LAB1–LAB5

| Etap | Dotychczasowy rezultat w projekcie | Rola i rozwinięcie na etapie LAB5 |
|---|---|---|
| **LAB1** | Pierwsza mikrousługa (`create_app()`), modele Pydantic, walidacja (`422`), reguła biznesowa (`409`), obsługa braku zasobu (`404`) | Walidacja i reguła biznesowa nadal chronią wejście: odrzucona operacja (`409` lub `422`) nie może opublikować zdarzenia do brokera RabbitMQ |
| **LAB2** | Baza danych SQLite (SQLAlchemy) oraz cache-aside w Redis (`JsonCache`, `TTL`, nagłówek `X-Cache`, unieważnianie po zapisie) | W usłudze producenta zdarzenie jest publikowane dopiero po zatwierdzeniu zapisu; w usłudze konsumenta odebranie zdarzenia zapisuje zmianę w bazie i unieważnia odpowiedni klucz w Redis |
| **LAB3** | Druga mikrousługa, rejestracja obu usług w Eureka Server (`:8761`), synchroniczne wywołanie HTTP `do_service()` po nazwie logicznej | Komunikacja synchroniczna zostaje zachowana tam, gdzie wymagana jest natychmiastowa odpowiedź przed podjęciem decyzji, natomiast powiadomienie o zrealizowanym fakcie domenowym przechodzi asynchronicznie przez RabbitMQ |
| **LAB4** | Wspólny punkt wejścia API Gateway (`:8080`), trasy `lb://NAZWA-USŁUGI`, `StripPrefix=1`, nagłówek `X-Gateway: lab4` | Klient zewnętrzny nadal wysyła żądania przez bramkę (`:8080/api/...`); bramka przekazuje żądanie HTTP do producenta i zwraca odpowiedź bez oczekiwania na asynchronicznego konsumenta |
| **LAB5** | Wyłącznie synchroniczna komunikacja HTTP między usługami | Włączenie brokera **RabbitMQ** (`:5672` / `:15672`): jedna z usług publikuje trwałe zdarzenie domenowe po zapisie, a druga odbiera je z kolejki, przetwarza idempotentnie i potwierdza przez `ACK` |

Podczas pracy w parze należy podzielić zadania pomiędzy implementację strony publikującej (producenta i integracji z bazą/regułą) oraz strony odbierającej (konsumenta, idempotentności i unieważnienia cache), a następnie zamienić się rolami podczas pisania testów i wykonywania eksperymentów awarii.

### Organizacja pracy na zajęciach i po zajęciach

Proponowany podział 120 minut zajęć:

- **15 minut** — omówienie modelu AMQP (Exchange, Routing Key, Queue, ACK), porównanie z HTTP oraz omówienie choreografii/Sagi i idempotentności,
- **20 minut** — uruchomienie przykładu wspólnego z RabbitMQ (`lab5-support`) i obserwacja kolejki w panelu `15672`,
- **15 minut** — zaprojektowanie kontraktu zdarzenia domenowego i przepływu asynchronicznego we własnym projekcie,
- **35 minut** — implementacja publikacji i konsumpcji zdarzenia w dwóch usługach własnego projektu,
- **25 minut** — weryfikacja przez API Gateway, eksperyment z zatrzymanym konsumentem i duplikatem wiadomości,
- **10 minut** — prezentacja punktu kontrolnego i odbiór na zajęciach.

**Punkt kontrolny na koniec zajęć:** opublikowanie zdarzenia domenowego przez jedną usługę własnego projektu, zaobserwowanie go w kolejce RabbitMQ oraz poprawne odebranie i przetworzenie przez drugą usługę. Testy automatyczne i pełną dokumentację eksperymentów można dokończyć po zajęciach przed terminem oddania etapu.

---

## 3. Pojęcia i wzorce komunikacji asynchronicznej

### Komunikacja synchroniczna (HTTP) a asynchroniczna (RabbitMQ)

W LAB3 druga usługa wywoływała pierwszą synchronicznie przez HTTP (`do_service()`). Oznaczało to **sprzężenie czasowe (*temporal coupling*)**: aby wywołanie się powiodło, obie usługi musiały działać w tej samej chwili. W komunikacji asynchronicznej usługa publikująca (**producent**) wysyła komunikat o zaistniałym zdarzeniu do **brokera wiadomości (RabbitMQ)** i kończy obsługę żądania HTTP klienta, nie czekając na przetworzenie wiadomości przez odbiorcę (**konsumenta**).

| Cecha | Komunikacja synchroniczna HTTP (LAB3) | Komunikacja asynchroniczna RabbitMQ (LAB5) |
|---|---|---|
| **Charakter komunikatu** | Żądanie / Polecenie lub Zapytanie (*Request / Query*) wymagające natychmiastowego wyniku | Zdarzenie domenowe (*Domain Event*) informujące o fakcie, który już nastąpił (np. `ParcelPlaced`, `ReservationCreated`) |
| **Sprzężenie czasowe** | Wysokie — odbiorca musi działać w momencie wywołania | Niskie — wiadomość może poczekać w trwałej kolejce na uruchomienie konsumenta |
| **Znajomość odbiorcy** | Nadawca wskazuje nazwę logiczną odbiorcy z Eureki (`LOCKER-SERVICE`) | Producent publikuje na `Exchange` z kluczem routingu; nie musi wiedzieć, ile kolejek i jakich usług nasłuchuje tego zdarzenia |
| **Spójność danych** | Natychmiastowa odpowiedź (sukces lub błąd `4xx`/`5xx`) | Spójność ostateczna (*Eventual Consistency*) — stan w drugiej usłudze aktualizuje się z niewielkim opóźnieniem |
| **Zachowanie przy wyłączonym odbiorcy** | Natychmiastowy błąd `503 Service Unavailable` | Producent zapisuje dane i publikuje zdarzenie; konsument odbiera je po wznowieniu pracy |

### Przepływ wiadomości w modelu AMQP 0-9-1 (RabbitMQ)

W RabbitMQ producent nigdy nie wysyła wiadomości bezpośrednio do kolejki. Wiadomość trafia najpierw do **wymiennika (*Exchange*)**, który na podstawie swojego typu (np. `topic` lub `direct`), **klucza routingu (*Routing Key*)** oraz zdefiniowanych **powiązań (*Bindings*)** kieruje kopię wiadomości do jednej lub wielu **kolejek (*Queues*)**.

<pre class="mermaid">
flowchart LR
    K["Klient HTTP"] -->|"1. POST /api/parcels"| G["API Gateway :8080"]
    G -->|"2. POST /parcels"| P["Parcel Service :8102<br/>(Producent zdarzenia)"]
    P -->|"3. Synchroniczne sprawdzenie (LAB3)<br/>GET /lockers/KRK-1024"| L["Locker Service :8101<br/>(Konsument zdarzenia)"]
    P -->|"4. basic_publish<br/>routing_key: parcel.placed"| EX[["Exchange: pawoom.events<br/>(topic, durable)"]]
    EX -->|"Binding: parcel.placed"| Q[("Queue: locker.parcel-events<br/>(durable)")]
    Q -->|"5. Pobranie wiadomości + basic_ack"| L
    L -->|"6. Aktualizacja stanu + DEL cache"| DB[("SQLite + Redis<br/>(zasoby z LAB2)")]
    G -.-> E["Eureka :8761"]
    P -.-> E
    L -.-> E
</pre>

Znaczenie podstawowych pojęć konfiguracyjnych w RabbitMQ:

| Pojęcie | Przykład w pakiecie `lab5-support` | Rola techniczna |
|---|---|---|
| **Exchange (`topic`)** | `pawoom.events` (`durable=True`) | Punkt przyjmujący wiadomości od producentów i rozdzielający je do powiązanych kolejek według wzorca klucza routingu |
| **Routing Key** | `parcel.placed` | Etykieta określająca kategorię i typ zdarzenia, używana przez `Exchange` do dopasowania powiązań |
| **Queue** | `locker.parcel-events` (`durable=True`) | Bufor przechowujący wiadomości przeznaczone dla konkretnej usługi konsumenckiej |
| **Binding** | `pawoom.events` → `locker.parcel-events` (`parcel.placed`) | Reguła łącząca wymiennik z kolejką dla wybranego klucza routingu |
| **Persistent Message** | `delivery_mode = 2` (`Persistent`) | Oznaczenie wiadomości jako trwałej, zapisywanej na dysku brokera |
| **Manual ACK (`basic_ack`)** | `auto_ack=False` + `channel.basic_ack(...)` | Jawne potwierdzenie przez konsumenta, że wiadomość została pomyślnie przetworzona i zapisana, po którym broker usuwa ją z kolejki |
| **Negative ACK (`basic_nack`)** | `channel.basic_nack(..., requeue=True)` | Odrzucenie wiadomości w razie błędu przetwarzania z możliwością przywrócenia jej do kolejki |

### Rola transakcji bazodanowych, wzorzec Saga, idempotentność i prawo Postela

Zgodnie z zagadnieniami wykładowymi sylabusa podczas integracji asynchronicznej należy uwzględnić cztery zjawiska:

1. **Kolejność wobec transakcji bazodanowej (LAB2):**
   W usłudze producenta należy najpierw zweryfikować dane wejściowe i regułę biznesową (LAB1), następnie zatwierdzić zmianę w lokalnej bazie danych (`COMMIT` w SQLite z LAB2) i unieważnić lokalny cache, a dopiero po zatwierdzeniu opublikować zdarzenie domenowe (lub wycofać operację, jeśli publikacja jest warunkiem przyjęcia żądania). Nigdy nie wolno publikować zdarzenia o utworzeniu zasobu przed sprawdzeniem reguł biznesowych — w przeciwnym razie konsument przetworzyłby zdarzenie, które w usłudze źródłowej zostało odrzucone kodem `409` lub `422`.
   *(W systemach produkcyjnych ryzyko awarii procesu dokładnie pomiędzy `COMMIT` w bazie a `basic_publish` do brokera rozwiązuje się wzorcem **Transactional Outbox**, zapisując zdarzenie w tabeli `outbox` w tej samej transakcji bazodanowej).*

2. **Wzorzec Saga — choreografia a orkiestracja:**
   Gdy proces biznesowy obejmuje zmianę stanu w kilku mikrousługach bez jednej wspólnej transakcji rozproszonej (2PC), stosuje się wzorzec **Saga**:
   - w **choreografii** usługi reagują bezpośrednio na publikowane zdarzenia domenowe (np. `Parcel Service` publikuje `ParcelPlaced`, a `Locker Service` nasłuchuje tego zdarzenia i aktualizuje stan paczkomatu bez centralnego koordynatora),
   - w **orkiestracji** wydzielony komponent koordynatora wysyła kolejne polecenia do usług i oczekuje na ich odpowiedzi, a w razie błędu uruchamia operacje kompensujące.
   W ramach ćwiczenia należy zaimplementować przepływ oparty o **choreografię zdarzeń**.

3. **Dostarczanie *at-least-once* i idempotentność konsumenta:**
   Brokerzy wiadomości zapewniają zazwyczaj dostarczanie **co najmniej raz (*at-least-once delivery*)**: jeżeli konsument przetworzy wiadomość, ale połączenie zostanie zerwane tuż przed wysłaniem `basic_ack`, RabbitMQ dostarczy tę samą wiadomość ponownie. Dlatego każde zdarzenie musi posiadać unikatowy identyfikator `event_id`, a konsument musi być **idempotentny** — ponowne odebranie zdarzenia o już przetworzonym `event_id` nie może drugi raz zwiększyć licznika ani utworzyć zduplikowanego rekordu, lecz powinno zakończyć się bezpiecznym potwierdzeniem `ACK`.

4. **Prawo Postela (*Tolerant Reader*) w kontraktach zdarzeń:**
   Zgodnie z prawem Postela (*„bądź zachowawczy w tym, co wysyłasz, i tolerancyjny w tym, co przyjmujesz”*) konsument wiadomości powinien odczytywać z JSON wyłącznie pola potrzebne mu do wykonania zadania (np. `event_id`, `locker_id`, `parcel_id`) i ignorować dodatkowe, nieznane mu pola. Dzięki temu dodanie nowego pola przez producenta nie psuje działających konsumentów.

---

## 4. Część A — uruchomienie i analiza przykładu wspólnego

W pierwszej części należy uruchomić wspólny przykład z pakietu `lab5-support`, w którym `PARCEL-SERVICE` weryfikuje paczkomat synchronicznie w `LOCKER-SERVICE` (jak w LAB3), a następnie po utworzeniu paczki publikuje zdarzenie `ParcelPlaced` do brokera RabbitMQ, skąd odbiera je `LOCKER-SERVICE`.

### Krok 1. Pobranie pakietu pomocniczego i uruchomienie brokera (Docker / RabbitMQ)

Należy pobrać [pakiet pomocniczy LAB5 — ZIP]({{ '/2026_2027/lab5/lab5-support.zip' | relative_url }}) i rozpakować go obok własnego projektu oraz obok katalogów `lab3-support` i `lab4-support`.

Struktura katalogu `lab5-support`:

```text
lab5-support/
├── compose.yaml
├── requirements.txt
├── README.md
└── demo/
    ├── README-LAB5-template.md
    ├── shared/
    │   ├── eureka.py
    │   └── messaging.py
    ├── locker_service/app/main.py
    ├── parcel_service/app/main.py
    └── tests/test_async_messaging.py
```

W terminalu PowerShell, w katalogu `lab5-support`, należy uruchomić środowisko wirtualne, zainstalować zależności i uruchomić testy jednostkowe przykładu:

```powershell
Set-Location .\lab5-support
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Oczekiwany wynik to `5 passed`. Testy jednostkowe używają klasy `InMemoryEventBroker` z pliku `demo/shared/messaging.py`, więc działają bez uruchomionego kontenera RabbitMQ.

Następnie należy uruchomić kontener RabbitMQ z wtyczką Management:

```powershell
docker compose up -d rabbitmq
```

Po kilku sekundach należy otworzyć w przeglądarce panel zarządzania pod adresem `http://127.0.0.1:15672/` i zalogować się danymi `guest` / `guest`. W zakładkach **Exchanges** oraz **Queues** będzie można na żywo obserwować tworzone wymienniki, powiązania oraz liczbę oczekujących wiadomości (*Ready* / *Unacked*).

### Krok 2. Analiza implementacji producenta i konsumenta (`pika` / FastAPI)

Należy otworzyć i przeanalizować trzy kluczowe fragmenty kodu w pakiecie `lab5-support`:

1. **Publikacja trwałego zdarzenia w `demo/shared/messaging.py` (`RabbitEventBroker.publish`):**
   ```python
   channel.exchange_declare(
       exchange=self.exchange_name,
       exchange_type="topic",
       durable=True,
   )
   body = json.dumps(event).encode("utf-8")
   channel.basic_publish(
       exchange=self.exchange_name,
       routing_key=routing_key,
       body=body,
       properties=pika.BasicProperties(
           content_type="application/json",
           delivery_mode=pika.DeliveryMode.Persistent,
           message_id=str(event.get("event_id", "")),
       ),
   )
   ```
   Metoda deklaruje trwały wymiennik typu `topic` (`pawoom.events`) i publikuje wiadomość JSON oznaczoną jako trwała (`Persistent`).

2. **Konsumpcja z jawnym potwierdzeniem `ACK`/`NACK` w `demo/shared/messaging.py` (`RabbitEventBroker.consume_available`):**
   ```python
   method_frame, _properties, body = channel.basic_get(
       queue=queue_name, auto_ack=False
   )
   if method_frame is None:
       break
   try:
       event = json.loads(body.decode("utf-8"))
       handler(event)
   except Exception:
       channel.basic_nack(
           delivery_tag=method_frame.delivery_tag, requeue=True
       )
       raise
   else:
       channel.basic_ack(delivery_tag=method_frame.delivery_tag)
       processed += 1
   ```
   Parametr `auto_ack=False` wyłącza automatyczne usuwanie wiadomości w chwili jej pobrania. Broker usuwa wiadomość z kolejki dopiero po wywołaniu `basic_ack`, czyli po pomyślnym wykonaniu funkcji `handler(event)`.

3. **Idempotentna obsługa zdarzenia w `demo/locker_service/app/main.py` (`handle_parcel_placed`):**
   ```python
   def handle_parcel_placed(event: dict[str, Any]) -> None:
       event_id = str(event.get("event_id") or "")
       locker_id = str(event.get("locker_id") or "")
       if not event_id or not locker_id:
           raise ValueError("Missing event_id or locker_id in event payload")
       if event_id in processed_event_ids:
           return
       locker = lockers.get(locker_id)
       if locker is None:
           raise LookupError(f"Unknown locker_id: {locker_id}")
       processed_event_ids.add(event_id)
       locker["placed_parcels_count"] += 1
       event_history.setdefault(locker_id, []).append(event)
   ```
   Jeżeli `event_id` znajduje się już w zbiorze `processed_event_ids`, funkcja kończy się bez ponownego zwiększania `placed_parcels_count`, a metoda `consume_available` wysyła `basic_ack`, zdejmując duplikat z kolejki.

### Krok 3. Uruchomienie usług i obserwacja przepływu zdarzenia w RabbitMQ

Należy upewnić się, że działa serwer **Eureka** (`:8761`, uruchomiony z `lab3-support`) oraz kontener **RabbitMQ** (`:5672` i `:15672`).

1. **Terminal 1 — uruchomienie `LOCKER-SERVICE` (`:8101`, w katalogu `lab5-support`):**
   ```powershell
   $env:EUREKA_SERVER_URL = 'http://127.0.0.1:8761'
   $env:RABBITMQ_URL = 'amqp://guest:guest@127.0.0.1:5672/%2F'
   $env:SERVICE_NAME = 'LOCKER-SERVICE'
   $env:SERVICE_PORT = '8101'
   .\.venv\Scripts\python.exe -m uvicorn demo.locker_service.app.main:app --port 8101
   ```
   Podczas startu `LOCKER-SERVICE` wywołuje `broker.bind_queue("locker.parcel-events", "parcel.placed")`, tworząc trwałą kolejkę w RabbitMQ i wiążąc ją z wymiennikiem `pawoom.events`.

2. **Terminal 2 — uruchomienie `PARCEL-SERVICE` (`:8102`, w katalogu `lab5-support`):**
   ```powershell
   $env:EUREKA_SERVER_URL = 'http://127.0.0.1:8761'
   $env:RABBITMQ_URL = 'amqp://guest:guest@127.0.0.1:5672/%2F'
   $env:SERVICE_NAME = 'PARCEL-SERVICE'
   $env:SERVICE_PORT = '8102'
   .\.venv\Scripts\python.exe -m uvicorn demo.parcel_service.app.main:app --port 8102
   ```

3. **Terminal 3 — nadanie paczki i obserwacja stanu przed oraz po konsumpcji:**
   Po pojawieniu się obu usług jako `UP` w panelu Eureki (`http://127.0.0.1:8761/`), należy wykonać:
   ```powershell
   curl.exe -i -X POST http://127.0.0.1:8102/parcels -H "Content-Type: application/json" -d "{\"id\":\"PCK-101\",\"locker_id\":\"KRK-1024\",\"size\":\"M\"}"
   curl.exe -i http://127.0.0.1:8101/lockers/KRK-1024
   ```
   Należy zwrócić uwagę na rezultat:
   - `POST /parcels` natychmiast zwraca `201 Created` z identyfikatorem wygenerowanego zdarzenia `last_event_id`,
   - w panelu RabbitMQ (`http://127.0.0.1:15672/#/queues`) w kolejce `locker.parcel-events` widoczna jest **1 oczekująca wiadomość (`Ready: 1`)**,
   - odczyt `GET /lockers/KRK-1024` przed uruchomieniem konsumpcji pokazuje jeszcze `placed_parcels_count: 0` (ilustracja opóźnienia w modelu *eventual consistency*).

4. **Pobranie i przetworzenie wiadomości przez konsumenta:**
   W tym samym terminalu należy wyzwolić pobranie wiadomości z kolejki i ponownie odczytać stan paczkomatu:
   ```powershell
   curl.exe -i -X POST http://127.0.0.1:8101/events/consume
   curl.exe -i http://127.0.0.1:8101/lockers/KRK-1024
   curl.exe -i http://127.0.0.1:8101/lockers/KRK-1024/events
   ```
   Oczekiwany rezultat: `consumed_messages: 1`, w panelu RabbitMQ liczba wiadomości w kolejce `locker.parcel-events` spada do `0`, a `GET /lockers/KRK-1024` zwraca `placed_parcels_count: 1` wraz z zapisanym zdarzeniem `ParcelPlaced`.

5. **Sprawdzenie reguły biznesowej przed publikacją:**
   Należy spróbować nadać paczkę do wyłączonego paczkomatu `KRK-2048` (`status: offline`):
   ```powershell
   curl.exe -i -X POST http://127.0.0.1:8102/parcels -H "Content-Type: application/json" -d "{\"id\":\"PCK-102\",\"locker_id\":\"KRK-2048\",\"size\":\"S\"}"
   ```
   Żądanie zostaje odrzucone kodem `409 Conflict`, a do kolejki `locker.parcel-events` nie trafia żadna wiadomość.

---

## 5. Część B — zaprojektowanie przepływu asynchronicznego we własnym projekcie

Po przeanalizowaniu przykładu należy zatrzymać procesy demonstracyjne z `lab5-support`, pozostawiając uruchomiony kontener **RabbitMQ** (`:5672` / `:15672`), serwer **Eureka** (`:8761`), serwer **Redis** (`:6379`) oraz bramkę **API Gateway** (`:8080`).

### Krok 1. Wybór zdarzenia domenowego i określenie kontraktu wiadomości

W oparciu o dwie własne usługi z LAB1–LAB4 należy zaprojektować jeden spójny przepływ asynchroniczny, w którym po wykonaniu operacji zapisu lub modyfikacji w jednej usłudze (**Producent**) publikowane jest zdarzenie domenowe do RabbitMQ, a druga usługa (**Konsument**) odbiera je z kolejki i wykonuje określoną aktualizację własnych danych.

Przykłady dla typowych domen studenckich:

- **Rezerwacja sal:** utworzenie lub potwierdzenie rezerwacji w `RESERVATION-SERVICE` publikuje zdarzenie `ReservationConfirmed` (`reservation_id`, `room_id`, `reserved_by`); `ROOM-SERVICE` odbiera zdarzenie, zwiększa licznik rezerwacji sali `reservations_count` (lub zapisuje ostatnią rezerwację w tabeli SQLite z LAB2) i unieważnia cache sali w Redis.
- **Biblioteka / wypożyczenia:** utworzenie wypożyczenia w `LOAN-SERVICE` publikuje zdarzenie `BookBorrowed` (`loan_id`, `book_id`); `CATALOG-SERVICE` odbiera zdarzenie, aktualizuje stan egzemplarza lub licznik wypożyczeń w SQLite i unieważnia klucz książki w Redis.
- **Wydarzenia i bilety:** zakup biletu w `TICKET-SERVICE` publikuje zdarzenie `TicketIssued` (`ticket_id`, `event_id`); `EVENT-SERVICE` odbiera zdarzenie, aktualizuje liczbę sprzedanych biletów w SQLite i unieważnia cache wydarzenia w Redis.

Należy uzupełnić tabelę projektową dla własnej domeny:

| Element kontraktu asynchronicznego | Decyzja we własnym projekcie |
|---|---|
| **Usługa publikująca (Producent)** i endpoint wyzwalający | np. `RESERVATION-SERVICE`, `POST /reservations` (przez bramkę: `POST /api/reservations`) |
| **Usługa odbierająca (Konsument)** | np. `ROOM-SERVICE` |
| **Nazwa zdarzenia (`event_type`)** | np. `ReservationCreated` |
| **Wymiennik (`exchange`) i typ** | np. `pawoom.events` (`topic`, `durable=True`) |
| **Klucz routingu (`routing_key`)** | np. `reservation.created` |
| **Nazwa kolejki (`queue_name`)** | np. `room.reservation-events` (`durable=True`) |
| **Pola ładunku JSON zdarzenia** | `event_id`, `event_type`, identyfikatory zasobów, istotne dane domenowe, `occurred_at` |
| **Skutek w usłudze konsumenta (SQLite + Redis)** | np. aktualizacja pola/tabeli w SQLite, zapis `event_id` dla idempotentności oraz wywołanie `cache.delete(id)` w Redis |

Przed przystąpieniem do implementacji należy odpowiedzieć pisemnie na pięć pytań projektowych:

1. Dlaczego wybrana operacja publikuje zdarzenie domenowe asynchronicznie, a które sprawdzenie między usługami (z LAB3) nadal powinno pozostać synchroniczne?
2. W którym dokładnie miejscu kodu producenta (względem walidacji Pydantic z LAB1, sprawdzenia reguły biznesowej i zatwierdzenia transakcji w bazie z LAB2) następuje wywołanie `broker.publish(...)`?
3. Co musi zrobić konsument po odebraniu wiadomości względem własnej bazy SQLite i cache Redis z LAB2, aby kolejny odczyt przez API Gateway (`GET /api/...`) nie zwrócił przestarzałej wartości z cache?
4. W jaki sposób konsument rozpozna duplikat wiadomości o tym samym `event_id` i dlaczego potwierdzenie `basic_ack` wysyła się dopiero po zapisaniu zmiany?
5. Co dzieje się z wiadomością opublikowaną przez producenta, gdy proces konsumenta jest w tym momencie zatrzymany?

---

## 6. Implementacja komunikacji przez RabbitMQ we własnym projekcie

### Krok 1. Dodanie modułu brokera wiadomości i zależności (`pika`)

Do pliku `requirements.txt` obu własnych usług należy dopisać zależność `pika>=1.3,<2.0` i zainstalować ją w środowiskach wirtualnych usług:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Do obu usług własnego projektu należy skopiować moduł adaptera `messaging.py` z pakietu `lab5-support` (zawierający klasy `RabbitEventBroker`, `InMemoryEventBroker` oraz wyjątek `BrokerUnavailableError`).

W funkcji `create_app(...)` obu usług należy dodać opcjonalny parametr `event_broker=None` (obok dotychczasowych parametrów `database_url`, `redis_client`, `eureka_client` z LAB2 i LAB3), tak aby:

- podczas normalnego uruchomienia aplikacja tworzyła `RabbitEventBroker()`,
- w testach jednostkowych można było wstrzyknąć `InMemoryEventBroker()` bez łączenia się z siecią,
- przy starcie aplikacji konsumenta (`lifespan`) wywoływane było powiązanie kolejki `broker.bind_queue(QUEUE_NAME, ROUTING_KEY)` z bezpiecznym przechwyceniem `BrokerUnavailableError` (aby chwilowa niedostępność RabbitMQ podczas startu nie uniemożliwiała uruchomienia procesu HTTP).

### Krok 2. Publikacja zdarzenia w usłudze producenta po zapisie

W wybranym endpointzie zapisu usługi pełniącej rolę producenta należy:

1. wykonać dotychczasową walidację danych (`422`), sprawdzenie reguły biznesowej (`409`) oraz ewentualne synchroniczne sprawdzenie w drugiej usłudze przez Eurekę (`do_service()` z LAB3),
2. zapisać stan domenowy (w bazie SQLite, jeśli producent posiada warstwę z LAB2, oraz unieważnić jego własny cache),
3. utworzyć słownik zdarzenia zawierający unikatowe `event_id` (np. `f"evt-{uuid.uuid4().hex[:12]}"`), `event_type`, identyfikatory zasobów oraz znacznik czasu `occurred_at` w formacie ISO 8601 UTC,
4. wywołać `request.app.state.event_broker.publish(ROUTING_KEY, event)` i obsłużyć ewentualny wyjątek `BrokerUnavailableError` kontrolowanym kodem `503 Service Unavailable`.

Przykład konstrukcji publikacji zdarzenia:

```python
event = {
    "event_id": f"evt-{uuid.uuid4().hex[:12]}",
    "event_type": "ReservationCreated",
    "reservation_id": created["id"],
    "room_id": created["room_id"],
    "occurred_at": datetime.now(timezone.utc).isoformat(),
}
try:
    request.app.state.event_broker.publish("reservation.created", event)
except BrokerUnavailableError as exc:
    raise HTTPException(
        status_code=503, detail="RabbitMQ broker is unavailable"
    ) from exc
```

### Krok 3. Konsumpcja wiadomości, idempotentność oraz integracja z bazą SQLite i cache Redis (LAB2)

W usłudze pełniącej rolę konsumenta (rekomendowane jest, aby była to pierwsza usługa posiadająca bazę SQLite i cache Redis z LAB2, albo druga usługa zapisująca odebrane zdarzenia) należy zaimplementować:

1. **Funkcję obsługującą zdarzenie (`handle_event`)**, która:
   - sprawdza obecność `event_id` oraz wymaganych pól identyfikujących zasób,
   - sprawdza, czy `event_id` został już wcześniej przetworzony (w tabeli przetworzonych zdarzeń w SQLite lub w strukturze stanu usługi) — jeśli tak, kończy działanie bez ponownego aplikowania zmiany (**idempotentność**),
   - zapisuje zmianę stanu domenowego w bazie danych (np. zwiększa licznik operacji na zasobie, zmienia status lub dopisuje rekord historii zdarzeń w transakcji SQLAlchemy z LAB2),
   - **unieważnia klucz zmienionego zasobu w cache Redis** (`cache.delete(resource_id)` z LAB2), aby kolejny odczyt `GET` pobrał zaktualizowany stan z bazy SQLite, a nie przestarzałą kopię z Redis!
2. **Endpoint wyzwalający pobranie oczekujących wiadomości z kolejki** (np. `POST /events/consume` oraz udostępnienie go przez trasę w bramce API Gateway z LAB4 lub pod ścieżką zasobu, np. `POST /rooms/consume-events` → przez bramkę `POST /api/rooms/consume-events`), który wywołuje `broker.consume_available(QUEUE_NAME, handle_event)` i zwraca liczbę pobranych wiadomości oraz liczbę unikatowych przetworzonych zdarzeń.

Przykład połączenia konsumpcji wiadomości z repozytorium SQLAlchemy i cache Redis z LAB2:

```python
def handle_reservation_created(event: dict[str, Any]) -> None:
    event_id = str(event.get("event_id") or "")
    room_id = str(event.get("room_id") or "")
    if not event_id or not room_id:
        raise ValueError("Brak wymaganego pola event_id lub room_id")

    # 1. Idempotentny zapis w bazie SQLite (w ramach transakcji repozytorium z LAB2):
    applied = repository.apply_reservation_event(event_id=event_id, room_id=room_id)

    # 2. Unieważnienie klucza w Redis PO zatwierdzeniu transakcji w bazie (LAB2):
    if applied:
        cache.delete(room_id)
```

### Krok 4. Weryfikacja pełnego przepływu LAB1–LAB5 przez API Gateway

Przy uruchomionych wszystkich procesach (RabbitMQ, Redis, Eureka Server, obie usługi własne oraz API Gateway na porcie `8080`) należy wykonać pełny scenariusz integracyjny przez port bramki (`8080`):

1. **Zapełnienie cache w pierwszej usłudze (LAB2 + LAB4):**
   Należy dwukrotnie odczytać zasób przez bramkę (`GET http://127.0.0.1:8080/api/<zasob-1>/<id>`), potwierdzając nagłówki `X-Gateway: lab4` oraz przejście `X-Cache: MISS` → `X-Cache: HIT`.
2. **Wyzwolenie operacji w usłudze producenta przez bramkę (LAB1 + LAB3 + LAB4 + LAB5):**
   Należy wywołać przez bramkę operację zapisu publikującą zdarzenie (`POST http://127.0.0.1:8080/api/<zasob-2>`), a następnie sprawdzić w panelu RabbitMQ (`http://127.0.0.1:15672/#/queues`), że wiadomość pojawiła się w kolejce konsumenta (`Ready: 1`).
3. **Konsumpcja wiadomości i weryfikacja unieważnienia cache (LAB2 + LAB4 + LAB5):**
   Należy wywołać konsumpcję wiadomości (`POST .../consume`), a następnie ponownie odczytać zasób pierwszej usługi przez bramkę (`GET http://127.0.0.1:8080/api/<zasob-1>/<id>`). Należy potwierdzić, że:
   - odpowiedź zawiera zaktualizowany stan po przetworzeniu zdarzenia,
   - nagłówek `X-Cache` ma wartość `MISS` (dowód, że konsument unieważnił klucz w Redis po zapisie do SQLite!), a przy kolejnym odczycie zmienia się na `HIT`.

### Krok 5. Eksperymenty awarii, buforowania w kolejce i idempotentności

Należy wykonać pojedynczo poniższe eksperymenty i udokumentować ich przebieg w README:

| Scenariusz eksperymentalny | Działanie do wykonania | Oczekiwane zachowanie i wniosek |
|---|---|---|
| **1. Buforowanie wiadomości przy wyłączonym konsumencie** | Opublikowanie zdarzenia (lub zatrzymanie konsumenta po sprawdzeniu synchronicznym / bezpośrednia publikacja do kolejki, gdy proces konsumenta jest zatrzymany `Ctrl+C`) | Wiadomość nie ginie — w panelu RabbitMQ `15672` widnieje w kolejce jako `Ready: 1`. Po ponownym uruchomieniu procesu konsumenta i wywołaniu konsumpcji zdarzenie zostaje przetworzone i zatwierdzone przez `ACK` (`Ready: 0`) |
| **2. Idempotentność przy duplikacie wiadomości** | Dwukrotne opublikowanie w panelu RabbitMQ Management (sekcja *Publish message* na kolejce lub przez skrypt/test) wiadomości JSON z identycznym `event_id` | Konsument pobiera obie wiadomości (`consumed_messages: 2`), ale skutek domenowy w bazie SQLite jest aplikowany tylko **jeden raz** (`unique_events_processed` zwiększa się o 1) |
| **3. Odrzucenie operacji przez walidację (`422`) lub regułę biznesową (`409`)** | Wysłanie przez bramkę niepoprawnych lub konfliktowych danych do producenta | Producent zwraca `422` lub `409`; w kolejce RabbitMQ nie pojawia się żadna nowa wiadomość |
| **4. Niedostępność brokera RabbitMQ** | Zatrzymanie kontenera RabbitMQ (`docker compose stop rabbitmq`) i próba wywołania publikacji oraz konsumpcji | Obie operacje zwracają kontrolowany kod `503 Service Unavailable` bez nieobsłużonego wyjątku i bez pozostawienia niespójnego stanu. Po `docker compose start rabbitmq` komunikacja wraca do działania |

### Krok 6. Implementacja testów automatycznych (pytest)

Należy zachować wszystkie dotychczasowe testy z LAB1–LAB4 oraz dodać **co najmniej cztery własne testy automatyczne** weryfikujące komunikację asynchroniczną:

1. **Test 1 — publikacja i konsumpcja zdarzenia domenowego:** wykonanie poprawnej operacji w usłudze producenta, potwierdzenie opublikowania zdarzenia z właściwym `routing_key` i polami JSON, a następnie uruchomienie konsumpcji w drugiej usłudze i potwierdzenie zmiany stanu domenowego (oraz unieważnienia cache Redis, jeśli konsument korzysta z cache z LAB2).
2. **Test 2 — idempotentność konsumenta dla zduplikowanego `event_id`:** dwukrotne dostarczenie tego samego zdarzenia (z tym samym `event_id`) do kolejki i potwierdzenie, że stan domenowy zmienił się dokładnie raz.
3. **Test 3 — brak publikacji zdarzenia przy błędzie walidacji (`422`), konflikcie (`409`) lub braku zasobu (`404`):** wywołanie niepoprawnej operacji w usłudze producenta i potwierdzenie, że lista opublikowanych zdarzeń w brokerze pozostaje pusta (`broker.published == []`).
4. **Test 4 — kontrolowana obsługa awarii brokera (`503`):** wstrzyknięcie `InMemoryEventBroker(down=True)` i potwierdzenie, że usługa zwraca kontrolowany kod `503` bez uszkodzenia stanu danych.

W testach jednostkowych należy używać wstrzykiwanego `InMemoryEventBroker` (analogicznie do `MemoryRedis` z LAB2 i `FakeEurekaClient` z LAB3), tak aby podstawowy zestaw testów `pytest` wykonywał się szybko i deterministycznie bez wymagania kontenera RabbitMQ. Dodatkowo w katalogu testów integracyjnych (`tests/integration/`) warto dodać test sprawdzający pełny przepływ przez uruchomioną bramkę API Gateway (`:8080`) i rzeczywisty broker RabbitMQ.

---

## 7. Diagnostyka typowych problemów z brokerem wiadomości

| Objaw problemu | Przyczyna i sposób rozwiązania |
|---|---|
| Błąd połączenia z portem `5672` (`BrokerUnavailableError` / `503`) | Kontener `lab5-rabbitmq` nie jest uruchomiony lub jeszcze inicjalizuje proces brokera; należy sprawdzić `docker ps` oraz `docker compose logs rabbitmq` i upewnić się, że `RABBITMQ_URL` wskazuje `amqp://guest:guest@127.0.0.1:5672/%2F` |
| Producent zwraca `201`, ale w panelu `15672` w kolejce jest `0` wiadomości | Kolejka konsumenta nie została jeszcze zadeklarowana i powiązana (`bind_queue`) przed publikacją wiadomości, albo `routing_key` producenta nie zgadza się z kluczem powiązania kolejki. Wiadomość wysłana na `Exchange` bez pasującej kolejki jest odrzucana |
| Wiadomości w panelu RabbitMQ wiszą w stanie `Unacked` i wracają do `Ready` | Konsument pobrał wiadomość z `auto_ack=False`, ale rzucił wyjątek przed wywołaniem `basic_ack` lub wykonał `basic_nack(..., requeue=True)`. Należy sprawdzić logi konsumenta i poprawność formatu JSON |
| Po przetworzeniu zdarzenia w bazie SQLite endpoint `GET` nadal zwraca starą wartość | W obsłudze zdarzenia konsumenta zapomniano wywołać `cache.delete(resource_id)` po zatwierdzeniu transakcji w bazie, przez co usługa zwraca nieaktualny wpis `HIT` z Redis (LAB2) |
| Stare testy jednostkowe z LAB1–LAB3 próbują łączyć się z RabbitMQ | Do funkcji `create_app(...)` w fixture testowych należy przekazać `event_broker=InMemoryEventBroker()`, aby odizolować testy jednostkowe od sieci |

### Granice zakresu zadania na LAB5

W ramach LAB5 nie należy budować klastrowego środowiska RabbitMQ, orkiestratora Sagi opartego o osobną bazę stanów maszyn stanowych, brokera Kafka ani pełnego wdrożenia wszystkich usług Python i Java w jednym wspólnym pliku Docker Compose. Należy skupić się na rzetelnej implementacji publikacji i konsumpcji zdarzenia przez RabbitMQ pomiędzy istniejącymi usługami projektu.

---

## 8. Punkty kontrolne, odbiór i kryteria oceny etapu

### Punkty kontrolne weryfikowane przy odbiorze

| Punkt kontrolny | Oczekiwany dowód wykonania |
|---|---|
| **Punkt A — ciągłość LAB1–LAB4** | Działają obie usługi, baza SQLite i cache Redis (LAB2), rejestracja i odnajdywanie w Eurece (LAB3), trasy w API Gateway (LAB4) oraz wcześniejsze testy |
| **Punkt B — kontrakt zdarzenia** | Zdefiniowany typ zdarzenia, wymiennik, klucz routingu, kolejka oraz struktura JSON z `event_id` i `occurred_at` |
| **Punkt C — publikacja i kolejka** | Wywołanie operacji przez API Gateway (`:8080`) publikuje trwałą wiadomość widoczną w kolejce w panelu RabbitMQ (`15672`), natomiast odrzucona operacja (`409`/`422`) nie publikuje wiadomości |
| **Punkt D — konsumpcja, baza i cache** | Konsument pobiera wiadomość, potwierdza ją przez `ACK`, aktualizuje stan w bazie danych, unieważnia wpis w cache Redis i zachowuje idempotentność dla powtórzonego `event_id` |
| **Punkt E — awarie i buforowanie** | Udokumentowany eksperyment z zatrzymanym konsumentem (wiadomość czeka w kolejce i zostaje przetworzona po wznowieniu procesu) oraz z zatrzymanym brokerem RabbitMQ (`503`) |
| **Punkt F — testy automatyczne** | Przechodzą co najmniej cztery własne testy automatyczne dla przepływu asynchronicznego oraz wszystkie wcześniejsze testy projektu |

### Pytania do rozmowy technicznej podczas odbioru

Każda osoba powinna umieć samodzielnie wyjaśnić:

1. Czym różni się wywołanie synchroniczne HTTP przez Eurekę (z LAB3) od publikacji zdarzenia przez RabbitMQ (z LAB5) i kiedy należy wybrać każde z nich?
2. Jaka jest rola `Exchange`, `Routing Key`, `Binding` oraz `Queue` i dlaczego producent nie wpisuje nazwy kolejki odbiorcy w `basic_publish`?
3. Dlaczego należy stosować `auto_ack=False` i jawne `basic_ack` po przetworzeniu zdarzenia zamiast automatycznego potwierdzania w chwili pobrania wiadomości?
4. Dlaczego konsument wiadomości musi być idempotentny i jak w projekcie zabezpieczono się przed dwukrotnym przetworzeniem tego samego `event_id`?
5. Dlaczego po aktualizacji stanu przez konsumenta należy unieważnić klucz w cache Redis z LAB2?
6. Czym różni się choreografia zdarzeń od orkiestracji we wzorcu Saga?

### Kryteria oceny etapu LAB5

Punktacja zachowuje podział z sylabusa przedmiotu: **60 punktów za kod** oraz **40 punktów za dokumentację**.

| Obszar | Oceniany element | Maksimum |
|---|---|---:|
| **Kod** | Zachowanie działania mechanizmów z LAB1–LAB4 (baza SQLite, cache Redis, Eureka, API Gateway i wcześniejsze testy) | 10 |
| **Kod** | Poprawna deklaracja wymiennika i kolejki oraz publikacja trwałego zdarzenia domenowego po walidacji i zapisie | 15 |
| **Kod** | Konsumpcja wiadomości z jawnym `ACK`/`NACK`, idempotentność po `event_id`, aktualizacja stanu i unieważnienie cache Redis | 20 |
| **Kod** | Co najmniej cztery własne testy automatyczne weryfikujące publikację, konsumpcję, idempotentność i błędy brokera | 15 |
| **Dokumentacja** | Projekt kontraktu zdarzenia, diagram łączący LAB2–LAB5, uzasadnienie komunikacji synchronicznej vs asynchronicznej i opis Sagi | 10 |
| **Dokumentacja** | Powtarzalna instrukcja uruchomienia RabbitMQ, usług, Eureki i API Gateway oraz komendy weryfikacji i testów | 10 |
| **Dokumentacja** | Udokumentowane wyniki eksperymentów (buforowanie przy wyłączonym konsumencie, duplikat `event_id`, awaria brokera) i ograniczenia | 10 |
| **Dokumentacja** | Opis co najmniej dwóch wykorzystanych źródeł dokumentacji technicznej (EK_03), wkład autorów i informacja o weryfikacji AI | 10 |
| **Razem** | **Kod 60 pkt + Dokumentacja 40 pkt** | **100** |

**Warunki zaliczenia etapu:** uzyskanie co najmniej **50 punktów** oraz spełnienie wszystkich poniższych warunków minimum:

- zachowana jest ciągłość działania usług, bazy SQLite, cache Redis, Eureki i bramki API Gateway z LAB1–LAB4,
- jedna z usług projektu publikuje trwałe zdarzenie domenowe JSON z `event_id` do wymiennika RabbitMQ po pomyślnej operacji, a nie publikuje go przy błędzie `404`/`409`/`422`,
- druga usługa odbiera wiadomość z powiązanej kolejki z użyciem `auto_ack=False` i jawnego `basic_ack`, aktualizuje swój stan (oraz unieważnia odpowiedni klucz w cache) i jest idempotentna względem powtórzonego `event_id`,
- udokumentowano eksperyment buforowania wiadomości w kolejce przy zatrzymanym konsumencie oraz zachowanie przy niedostępności brokera,
- przechodzą co najmniej cztery własne testy automatyczne dla komunikacji asynchronicznej oraz dotychczasowe testy projektu,
- każda osoba potrafi samodzielnie wyjaśnić przepływ wiadomości w RabbitMQ i wykonać drobną zmianę podczas odbioru.

---

## 9. Oznaczenie i przekazanie wersji projektu LAB5

Zmiany należy zatwierdzić w dotychczasowym repozytorium projektu, upewniając się wcześniej, że `.gitignore` wyklucza `.venv/`, `gateway/target/`, `*.db`, `__pycache__/` oraz `.env`:

```powershell
git status
git add .
git diff --cached --stat
git commit -m "feat(lab5): komunikacja asynchroniczna przez RabbitMQ, idempotentny konsument i testy"
git tag lab5
git push origin HEAD
git push origin refs/tags/lab5
```

---

## 10. Dokumentacja techniczna

Podczas realizacji zadania należy wykorzystać co najmniej dwa źródła z oficjalnej dokumentacji technicznej (wymaganie **EK_03**) i opisać w README rozwiązany problem, zastosowany mechanizm oraz sposób weryfikacji:

- [RabbitMQ Tutorials — AMQP Concepts](https://www.rabbitmq.com/tutorials/amqp-concepts) — model AMQP 0-9-1: wymienniki (`direct`, `topic`, `fanout`), kolejki, powiązania i klucze routingu.
- [RabbitMQ Tutorials — Publish/Subscribe & Routing in Python (`pika`)](https://www.rabbitmq.com/tutorials/tutorial-four-python) — deklaracja wymiennika, wiązanie kolejek (`queue_bind`) i publikacja z kluczem routingu.
- [RabbitMQ — Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms) — działanie `basic_ack`, `basic_nack`, parametru `requeue` oraz gwarancje dostarczania *at-least-once*.
- [RabbitMQ — Queues and Durability](https://www.rabbitmq.com/docs/queues) — trwałość kolejek (`durable=True`) oraz trwałość wiadomości (`delivery_mode=2`).
- [Pika Documentation — BlockingConnection & Channel](https://pika.readthedocs.io/en/stable/modules/channel.html) — dokumentacja metod `exchange_declare`, `queue_declare`, `basic_publish`, `basic_get`, `basic_ack` i `basic_nack`.
