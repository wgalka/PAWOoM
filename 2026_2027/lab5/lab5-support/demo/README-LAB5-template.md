## Etap LAB5 — komunikacja asynchroniczna z wykorzystaniem RabbitMQ

### Autorzy i ciągłość projektu z LAB1–LAB4

- Autorzy i indywidualny wkład każdej osoby w parze:
- Zachowane komponenty z LAB1–LAB4 (pierwsza usługa z SQLite i Redis, druga usługa, Eureka Server, API Gateway):
- Dodane i zmodyfikowane pliki w repozytorium:

### Projekt komunikacji asynchronicznej i kontrakt zdarzenia

| Element kontraktu | Wartość we własnym projekcie | Uzasadnienie projektowe |
|---|---|---|
| Usługa publikująca (Producent) | | |
| Operacja wyzwalająca publikację | | |
| Nazwa zdarzenia domenowego (`event_type`) | | |
| Nazwa exchange i typ (`topic` / `direct`) | | |
| Klucz routingu (`routing_key`) | | |
| Nazwa kolejki (`queue`) | | |
| Usługa odbierająca (Konsument) | | |
| Skutek biznesowy po odebraniu zdarzenia | | |

- Przykładowy ładunek JSON zdarzenia domenowego (`event_id`, `event_type`, pola domenowe, `occurred_at`):
- Dlaczego wybrana operacja korzysta z komunikacji asynchronicznej przez RabbitMQ, a które sprawdzenie pozostaje synchroniczne (HTTP przez Eurekę z LAB3)?
- Kolejność operacji wobec bazy SQLite i cache Redis z LAB2 (dlaczego publikacja następuje po zatwierdzeniu transakcji w bazie i jakie ryzyko wiąże się z awarią pomiędzy commitem a publikacją):
- Sposób zapewnienia idempotentności konsumenta przy powtórnym dostarczeniu wiadomości o tym samym `event_id`:
- Diagram przepływu łączący API Gateway (LAB4), komunikację synchroniczną (LAB3), publikację i konsumpcję przez RabbitMQ (LAB5) oraz bazę SQLite i cache Redis (LAB2):

### Uruchomienie, konfiguracja i zatrzymanie środowiska

- Wersja Pythona, klienta AMQP (`pika`) oraz obraz/wersja brokera RabbitMQ:
- Zmienne środowiskowe (`RABBITMQ_URL`, `EUREKA_SERVER_URL`, `DATABASE_URL`, `REDIS_URL`, `CACHE_PREFIX`), porty i katalogi robocze wszystkich procesów:
- Polecenia uruchomienia całego środowiska we właściwej kolejności:
- Polecenia uruchomienia testów jednostkowych (z `InMemoryEventBroker`) oraz testów integracyjnych:
- Polecenia zatrzymania procesów i kontenerów:

### Wyniki weryfikacji i eksperymentów awarii

| Scenariusz | Stan początkowy i działanie | Oczekiwany wynik | Rzeczywisty status HTTP, stan kolejki RabbitMQ i stan danych | Wniosek techniczny |
|---|---|---|---|---|
| Publikacja zdarzenia po poprawnym zapisie (przez API Gateway `:8080`) | | | | |
| Konsumpcja wiadomości z kolejki, `ACK`, aktualizacja stanu i unieważnienie cache Redis | | | | |
| Idempotentność — ponowne dostarczenie tego samego `event_id` | | | | |
| Odrzucenie operacji przez walidację (`422`) lub regułę biznesową (`409`) — brak publikacji zdarzenia | | | | |
| Zatrzymany konsument podczas publikacji — buforowanie w kolejce i późniejsze przetworzenie | | | | |
| Zatrzymany broker RabbitMQ podczas próby publikacji lub konsumpcji | | | | |

- Wykaz co najmniej czterech własnych testów automatycznych dla komunikacji asynchronicznej:
- Zaobserwowane ograniczenia spójności ostatecznej (*eventual consistency*) w projekcie:

### Wykorzystana dokumentacja techniczna (EK_03) i użycie AI

| Źródło oficjalnej dokumentacji i wersja | Rozwiązywany problem | Zastosowane rozwiązanie w kodzie/konfiguracji | Sposób weryfikacji działania |
|---|---|---|---|
| Do uzupełnienia (1) | | | |
| Do uzupełnienia (2) | | | |

- Zakres wykorzystania narzędzi AI oraz sposób samodzielnej weryfikacji kodu (albo „nie korzystano”):
