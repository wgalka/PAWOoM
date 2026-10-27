## Etap LAB6 — konteneryzacja systemu mikrousługowego (Docker / Docker Compose)

### Autorzy i kompletność systemu z LAB1–LAB6

- Autorzy i indywidualny wkład każdej osoby w parze (wskazanie co najmniej dwóch różnych mikrousług zaimplementowanych przez każdą osobę w projekcie semestralnym):
- Zestaw skonteneryzowanych komponentów własnego projektu:
- Dodane pliki `Dockerfile`, `.dockerignore` oraz `compose.yaml`:

### Architektura kontenerowa, sieć i wolumeny

| Usługa w `compose.yaml` | Obraz / `Dockerfile` | Port wewnętrzny (`expose`) | Port opublikowany na hoście (`ports`) | Zmienne środowiskowe i zależności (`depends_on` / `volumes`) |
|---|---|---|---|---|
| `eureka` | | `8761` | `127.0.0.1:8761:8761` | |
| `redis` | `redis:7-alpine` | `6379` | Brak (sieć wewnętrzna) | |
| `rabbitmq` | `rabbitmq:3.13-management-alpine` | `5672` | `127.0.0.1:15672:15672` | |
| Pierwsza usługa | | | Brak (sieć wewnętrzna) | Wolumen bazy SQLite, adresy `redis`, `eureka`, `rabbitmq` |
| Druga usługa | | | Brak (sieć wewnętrzna) | Adresy `eureka`, `rabbitmq` |
| `api-gateway` | | `8080` | `127.0.0.1:8080:8080` | `SERVER_ADDRESS=0.0.0.0`, `GATEWAY_EUREKA_URL=http://eureka:8761/eureka/` |

- Wyjaśnienie różnicy między adresem `127.0.0.1` na hoście a nazwami DNS usług w sieci Docker Compose (`eureka`, `redis`, `rabbitmq`, nazwy usług w `INSTANCE_HOST`):
- Dlaczego procesy wewnątrz kontenerów muszą nasłuchiwać na `0.0.0.0`, a które porty zostały ukryte przed bezpośrednim dostępem z hosta (`expose` zamiast `ports`)?
- Sposób zapewnienia trwałości bazy SQLite z LAB2 poza cyklem życia kontenera (nazwany wolumen Docker):
- Diagram pełnej architektury skonteneryzowanego systemu (LAB1–LAB6):

### Instrukcja zbudowania, uruchomienia i zatrzymania systemu

- Polecenie zbudowania i uruchomienia całego systemu jedną komendą (`docker compose up --build -d`):
- Polecenie sprawdzenia statusu i zdrowia kontenerów (`docker compose ps`, `docker compose logs`):
- Polecenia uruchomienia testów jednostkowych oraz testów integracyjnych przeciwko skonteneryzowanemu systemowi:
- Polecenia zatrzymania systemu z zachowaniem danych (`docker compose down`) oraz z pełnym wyczyszczeniem wolumenów (`docker compose down -v`):

### Wyniki weryfikacji i eksperymentów kontenerowych

| Scenariusz weryfikacyjny | Wykonane działanie | Oczekiwany rezultat | Rzeczywisty wynik i obserwacja | Wniosek techniczny |
|---|---|---|---|---|
| Start całego środowiska z `compose.yaml` | `docker compose up --build -d` i sprawdzenie `docker compose ps` oraz panelu Eureki | Wszystkie kontenery działają, usługi mają status `UP` pod nazwami kontenerowymi | | |
| Izolacja sieciowa usług za bramką | Próba wywołania usługi przez `:8080/api/...` oraz próba bezpośredniego połączenia z nieopublikowanym portem usługi z hosta | Dostęp przez bramkę działa (`200`), port wewnętrzny usługi jest niedostępny z hosta | | |
| Pełny przepływ synchroniczny i cache (LAB1–LAB4) | Zapis i odczyt przez bramkę (`X-Gateway: lab4`, `X-Cache: MISS/HIT`, wywołanie usługa–usługa z LAB3) | Poprawne odpowiedzi HTTP i działanie cache w kontenerze Redis | | |
| Pełny przepływ asynchroniczny (LAB5) | Publikacja zdarzenia przez bramkę i konsumpcja z kontenera RabbitMQ | Zdarzenie przetworzone idempotentnie, stan zaktualizowany, cache unieważniony | | |
| Trwałość danych na wolumenie po odtworzeniu kontenera | Zapis danych, wykonanie `docker compose down` i ponowne `docker compose up -d`, odczyt danych przez bramkę | Rekord zapisany w SQLite na nazwanym wolumenie przetrwał usunięcie i odtworzenie kontenera | | |
| Restart pojedynczego kontenera usługi | `docker compose restart <usluga>` i obserwacja logów oraz powrotu komunikacji przez bramkę | Kontener wstaje ponownie, odnawia rejestrację i przywraca obsługę tras | | |

### Wykorzystana dokumentacja techniczna (EK_03) i użycie AI

| Źródło oficjalnej dokumentacji i wersja | Rozwiązywany problem | Zastosowana dyrektywa w `Dockerfile` / `compose.yaml` | Sposób weryfikacji działania |
|---|---|---|---|
| Do uzupełnienia (1) | | | |
| Do uzupełnienia (2) | | | |

- Zakres wykorzystania narzędzi AI oraz sposób samodzielnej weryfikacji konfiguracji (albo „nie korzystano”):
