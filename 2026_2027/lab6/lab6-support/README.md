# Pakiet pomocniczy LAB6

Pakiet zawiera wzorcowe pliki `Dockerfile` (dla mikrousług Python/FastAPI oraz bramki Spring Cloud Gateway), plik `.dockerignore`, kompletną definicję wielokontenerowego środowiska `compose.yaml` łączącą komponenty z LAB1–LAB5, zestaw testów integracyjnych uruchamianych przez bramkę oraz szablon końcowej dokumentacji etapu LAB6.

## Zawartość pakietu

- `docker/Dockerfile.python` — wzorcowy obraz dla usług Python 3.12 + FastAPI uruchamianych z nieuprzywilejowanym użytkownikiem `appuser` i nasłuchiwaniem `--host 0.0.0.0`,
- `docker/Dockerfile.gateway` — wieloetapowy (*multi-stage*) obraz budujący i uruchamiający bramkę Spring Cloud Gateway z LAB4,
- `docker/.dockerignore` — lista wykluczeń kontekstu budowania obrazu,
- `compose.yaml` — orkiestracja całego przykładowego systemu (`eureka`, `redis`, `rabbitmq`, `locker-service`, `parcel-service`, `api-gateway`) wraz z kontrolą zdrowia (`healthcheck`), siecią kontenerową i nazwanym wolumenem danych (`locker_data`),
- `tests/test_containerized_system.py` — testy integracyjne weryfikujące skonteneryzowany system wyłącznie przez opublikowany port bramki (`127.0.0.1:8080`),
- `README-LAB6-template.md` — szablon dokumentacji etapu LAB6 oraz podsumowania projektu semestralnego.

## Uruchomienie skonteneryzowanego przykładu

Przed uruchomieniem przykładu należy zatrzymać wcześniejsze lokalne procesy nasłuchujące na portach `8080`, `8761` i `15672`. Z katalogu `2026_2027/lab6/lab6-support` należy wykonać:

```powershell
docker compose up --build -d
docker compose ps
```

Należy poczekać, aż kontenery infrastruktury uzyskają status `(healthy)`, a obie usługi zarejestrują się w panelu Eureki (`http://127.0.0.1:8761/`) pod swoimi nazwami kontenerowymi (`locker-service:8101`, `parcel-service:8102`).

Następnie z hosta należy sprawdzić działanie systemu przez opublikowany port bramki `8080`:

```powershell
curl.exe -i http://127.0.0.1:8080/health
curl.exe -i http://127.0.0.1:8080/api/lockers/KRK-1024
curl.exe -i http://127.0.0.1:8080/api/delivery-check/KRK-1024
```

## Uruchomienie testów integracyjnych z hosta

W katalogu `lab6-support` należy utworzyć środowisko wirtualne do uruchomienia klienta testowego i wykonać `pytest`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

## Zatrzymanie środowiska

Zatrzymanie kontenerów z zachowaniem nazwanego wolumenu danych:

```powershell
docker compose down
```

Zatrzymanie kontenerów wraz z usunięciem wolumenu (pełny reset stanu danych):

```powershell
docker compose down -v
```
