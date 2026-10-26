# Pakiet pomocniczy LAB3

Pakiet zawiera lokalny Eureka Server, minimalny przykład dwóch usług FastAPI oraz test jednostkowy klienta usługi. Przykład ilustruje integrację; nie stanowi gotowego projektu semestralnego.

## Wymagania

- Docker Desktop z `docker compose` albo JDK 21 i Maven do lokalnego uruchomienia serwera,
- Python 3.12 lub nowszy,
- wolne porty `8761`, `8101` i `8102`.

Jeśli komputer nie obsługuje Dockera, serwer można uruchomić lokalnie. Ta metoda wymaga JDK 21 i Maven.

## Uruchomienie rejestru Eureka

W katalogu pakietu należy uruchomić:

```powershell
docker compose up --build -d eureka
```

Przy pierwszym uruchomieniu obraz serwera jest budowany lokalnie, a Maven pobiera zależności. Panel znajduje się pod adresem `http://localhost:8761/`. Kontener nie uruchamia usług przykładowych.

Alternatywnie, z katalogu pakietu należy uruchomić serwer przez Maven:

```powershell
Set-Location .\eureka-server
mvn spring-boot:run
```

Maven pobierze zależności przy pierwszym uruchomieniu. Proces można zatrzymać skrótem `Ctrl+C`. Należy wybrać uruchomienie przez Docker Compose albo Maven.

## Uruchomienie dwóch usług

Środowisko Python należy utworzyć, a zależności zainstalować z katalogu pakietu:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

W pierwszym terminalu należy uruchomić `LOCKER-SERVICE`:

```powershell
$env:EUREKA_SERVER_URL = 'http://127.0.0.1:8761'
$env:SERVICE_PORT = '8101'
.\.venv\Scripts\python.exe -m uvicorn demo.locker_service.app.main:app --port 8101
```

W drugim terminalu należy uruchomić `PARCEL-SERVICE`:

```powershell
$env:EUREKA_SERVER_URL = 'http://127.0.0.1:8761'
$env:SERVICE_PORT = '8102'
.\.venv\Scripts\python.exe -m uvicorn demo.parcel_service.app.main:app --port 8102
```

Po pojawieniu się obu wpisów `UP` w panelu należy wykonać:

```powershell
Invoke-RestMethod http://127.0.0.1:8102/delivery-check/KRK-1024
```

`PARCEL-SERVICE` odnajduje `LOCKER-SERVICE` przez Eurekę i wywołuje `GET /lockers/KRK-1024`. Kod HTTP `404` dla `GET /delivery-check/UNKNOWN` pochodzi z odpowiedzi usługi paczkomatów. Po zatrzymaniu `LOCKER-SERVICE` wywołanie zależne zwraca `503`.

## Testy jednostkowe

Testy nie wymagają działającego serwera Eureka:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Zatrzymanie

Oba procesy Uvicorna należy zatrzymać skrótem `Ctrl+C`. Serwer Eureka należy zatrzymać w zależności od wybranej metody:

```powershell
docker compose down
```

Jeśli Eureka działa przez Maven, proces należy zakończyć skrótem `Ctrl+C` w terminalu, w którym uruchomiono `mvn spring-boot:run`.

Adresy i porty można zmieniać przez zmienne środowiskowe, ale port klienta rejestrowany w Eurece musi odpowiadać portowi Uvicorna. `SERVICE_PORT` w przykładzie jest używany przez klienta rejestru; parametr `--port` uruchamia serwer HTTP.
