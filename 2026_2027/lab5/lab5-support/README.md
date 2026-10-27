# Pakiet pomocniczy LAB5

Pakiet ilustruje asynchroniczną komunikację między dwiema usługami za pośrednictwem brokera wiadomości RabbitMQ, w połączeniu z rejestrem Eureka (z LAB3) oraz bramką API Gateway (z LAB4). Pakiet zawiera konfigurację kontenera RabbitMQ z panelem zarządzania, adapter klienta AMQP (`pika`) wraz z zamiennikiem pamięciowym do testów jednostkowych, dwie usługi demonstracyjne (`LOCKER-SERVICE` i `PARCEL-SERVICE`), zestaw pięciu testów automatycznych oraz szablon dokumentacji etapu LAB5.

## Wymagania wstępne

- Python 3.12 lub nowszy,
- serwer RabbitMQ 3.13 z wtyczką Management (uruchamiany przez `docker compose` z pliku `compose.yaml` albo jako usługa lokalna),
- działający serwer Eureka z pakietu `lab3-support` (`:8761`) oraz opcjonalnie bramka API Gateway z `lab4-support` (`:8080`),
- wolne porty `5672` (AMQP), `15672` (panel RabbitMQ Management), `8761`, `8101`, `8102` (oraz `8080` dla bramki).

## Uruchomienie brokera RabbitMQ

Z katalogu `lab5-support` należy uruchomić kontener RabbitMQ:

```powershell
docker compose up -d rabbitmq
```

Panel zarządzania RabbitMQ Management jest dostępny w przeglądarce pod adresem `http://127.0.0.1:15672/` (domyślny login i hasło: `guest` / `guest`). Port `5672` służy do komunikacji protokołem AMQP 0-9-1.

## Instalacja zależności i uruchomienie testów jednostkowych

W katalogu `lab5-support` należy utworzyć środowisko wirtualne, zainstalować zależności i uruchomić testy:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Testy w `demo/tests/test_async_messaging.py` korzystają z klas `InMemoryEventBroker` oraz `FakeEurekaClient`, dzięki czemu sprawdzają logikę publikacji, konsumpcji, idempotentności i obsługi błędów bez wymagania działającego kontenera RabbitMQ ani serwera Eureka (`5 passed`).

## Uruchomienie usług demonstracyjnych

Przed uruchomieniem usług należy upewnić się, że działają serwer Eureka (`:8761`) oraz broker RabbitMQ (`:5672`).

W pierwszym terminalu (w katalogu `lab5-support`) należy uruchomić `LOCKER-SERVICE`:

```powershell
$env:EUREKA_SERVER_URL = 'http://127.0.0.1:8761'
$env:RABBITMQ_URL = 'amqp://guest:guest@127.0.0.1:5672/%2F'
$env:SERVICE_NAME = 'LOCKER-SERVICE'
$env:SERVICE_PORT = '8101'
.\.venv\Scripts\python.exe -m uvicorn demo.locker_service.app.main:app --port 8101
```

W drugim terminalu (w katalogu `lab5-support`) należy uruchomić `PARCEL-SERVICE`:

```powershell
$env:EUREKA_SERVER_URL = 'http://127.0.0.1:8761'
$env:RABBITMQ_URL = 'amqp://guest:guest@127.0.0.1:5672/%2F'
$env:SERVICE_NAME = 'PARCEL-SERVICE'
$env:SERVICE_PORT = '8102'
.\.venv\Scripts\python.exe -m uvicorn demo.parcel_service.app.main:app --port 8102
```

Po zarejestrowaniu obu usług w Eurece można nadać paczkę w trzecim terminalu:

```powershell
curl.exe -i -X POST http://127.0.0.1:8102/parcels -H "Content-Type: application/json" -d "{\"id\":\"PCK-101\",\"locker_id\":\"KRK-1024\",\"size\":\"M\"}"
```

`PARCEL-SERVICE` weryfikuje synchronicznie paczkomat w `LOCKER-SERVICE`, zapisuje paczkę i publikuje zdarzenie `ParcelPlaced` do RabbitMQ (`exchange: pawoom.events`, `routing_key: parcel.placed`, kolejka: `locker.parcel-events`).

Następnie należy pobrać i przetworzyć oczekujące zdarzenia w `LOCKER-SERVICE` oraz sprawdzić stan paczkomatu:

```powershell
curl.exe -i -X POST http://127.0.0.1:8101/events/consume
curl.exe -i http://127.0.0.1:8101/lockers/KRK-1024
curl.exe -i http://127.0.0.1:8101/lockers/KRK-1024/events
```

## Zatrzymanie środowiska

Procesy Uvicorna należy zatrzymać skrótem `Ctrl+C`. Kontener RabbitMQ można zatrzymać poleceniem:

```powershell
docker compose down
```
