# Kod pomocniczy — LAB2

To uzupełnienie projektu z LAB1. Rozpakuj obok swojej usługi. Nie nadpisuj całej aplikacji. Przykład operuje na paczkomacie z tekstowym ID KRK-1024; pokazuje mechanizm bazy i cache, nie pełną usługę HTTP ani reguły skrytek.

## Uruchomienie

Python 3.12+, PowerShell. W tym katalogu:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
docker run --name lab2-redis -p 127.0.0.1:6379:6379 -d redis:7-alpine
$env:DATABASE_URL = 'sqlite:///./demo.db'
$env:REDIS_URL = 'redis://localhost:6379/0'
$env:CACHE_PREFIX = 'lab2:demo'
$env:CACHE_TTL_SECONDS = '60'
.\.venv\Scripts\python.exe demo.py seed
.\.venv\Scripts\python.exe demo.py get
.\.venv\Scripts\python.exe demo.py get
.\.venv\Scripts\python.exe demo.py rename --name 'Nowa nazwa'
.\.venv\Scripts\python.exe demo.py get
```

Redis wymaga działającego Dockera; istniejący kontener uruchom przez docker start lab2-redis. Możesz wskazać instancję prowadzącego i własny CACHE_PREFIX. Nie zatrzymuj wspólnego serwera.

Oczekiwane wyniki: MISS, HIT, udane unieważnienie, MISS z nową nazwą. Każde polecenie uruchamia nowy proces. Baza jest plikiem demo.db w katalogu uruchomienia. Seed nie nadpisuje istniejącego rekordu.

## Pliki i integracja

- database.py: wspólna baza modeli ORM i fabryka sesji (włącza PRAGMA foreign_keys=ON dla SQLite).
- cache.py: adapter JSON; obsługuje GET, SET i DELETE, krótkie timeouty i brak ponowień.
- demo.py: tabela, repozytorium, warstwa cache oraz program konsolowy.
- tests/test_storage.py: izolowana baza w tmp_path i zamiennik Redis.
- README-LAB2-template.md: uzupełnienie dokumentacji istniejącego projektu.

Przenieś mechanizm do własnego app/database.py i app/cache.py. Modele domenowe oraz zapytania napisz samodzielnie. Jeśli przenosisz importy do pakietu app, dopasuj je, np. from app.database import Base. Zachowaj create_app(), modele Pydantic, endpointy, regułę i testy z LAB1. Repozytorium demonstracyjne zwraca słowniki; możesz zamiast nich zwracać modele Pydantic.

Własna aplikacja musi także obsłużyć walidację i mapowanie wyjątków na HTTP. Demo nie waliduje wejścia jak FastAPI i nie jest gotowym rozwiązaniem do oddania.

## Ograniczenia i testy ręczne

Testy nie wymagają Redis. Zamiennik nie symuluje upływu TTL. Wykonaj osobno:
1. PING prawdziwego Redis.
2. MISS → HIT oraz GET i TTL własnego klucza.
3. Odczyt po wygaśnięciu TTL.
4. Zatrzymanie własnego Redis → get daje BYPASS.
5. Rename przy awarii → zapis pozostaje w bazie mimo cache_invalidated=False.
6. Przywrócenie Redis i sprawdzenie możliwej starej wartości.

Nieudane unieważnienie może pozostawić starą wartość aż do TTL. Test failed_invalidation pokazuje to ograniczenie. Współbieżność nie jest rozwiązana: prosty cache-aside nie gwarantuje ścisłej spójności.

Baza powstaje przez create_all; zmiana kolumn wymaga migracji. Demo nie odtwarza skrytek ani całego API z LAB1. Lokalna baza i środowisko nie należą do oddawanego repozytorium.
