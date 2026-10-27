# Pakiet pomocniczy LAB4

Należy wykorzystać ten pakiet razem z działającymi usługami i Eureką z LAB3. Pakiet zawiera bramkę Spring Cloud Gateway, pięć testów integracyjnych przykładu oraz szablon dokumentacji. Nie zawiera kopii usług ani nowej bazy danych.

## Uruchomienie bramki

Należy przygotować JDK 21 i Maven 3.9.x oraz wolny port `8080`. Bramkę należy uruchomić lokalnie, w tym samym systemie co usługi Python. Docker nie jest wymagany dla bramki. Eureka może nadal działać w wariancie wybranym na LAB3.

Z katalogu `lab4-support` należy wykonać:

```powershell
java -version
mvn -version
Set-Location .\gateway
mvn spring-boot:run
```

Maven pobiera zależności podczas pierwszego uruchomienia. Należy wcześniej uruchomić Eurekę oraz demo LAB3: `LOCKER-SERVICE` na `8101` i `PARCEL-SERVICE` na `8102`. Szczegółowe polecenia znajdują się w pakiecie LAB3. Nie należy jednocześnie rejestrować własnych usług pod tymi samymi nazwami co demo.

W nowym terminalu należy sprawdzić:

```powershell
curl.exe -i http://127.0.0.1:8080/health
curl.exe -i http://127.0.0.1:8080/api/lockers/KRK-1024
curl.exe -i http://127.0.0.1:8080/api/delivery-check/KRK-1024
```

Należy oczekiwać trzech odpowiedzi `200`; odpowiedzi domenowe powinny zawierać nagłówek `X-Gateway: lab4`. Po rejestracji usług może być konieczne odczekanie na odświeżenie lokalnego rejestru klienta.

Konfigurację należy zmieniać w `gateway/src/main/resources/application.yml`, a następnie ponownie uruchamiać bramkę. Trasy używają nazw logicznych z Eureki, nie stałych portów usług. Gateway pobiera rejestr, ale sam się nie rejestruje, więc brak jego wpisu w panelu jest prawidłowy. Endpoint `/health` bramki potwierdza jedynie działanie jej procesu.

Opcjonalne zmienne, ustawiane przed uruchomieniem Maven w tym samym terminalu:

```powershell
$env:GATEWAY_PORT = '8080'
$env:GATEWAY_EUREKA_URL = 'http://127.0.0.1:8761/eureka/'
```

W odróżnieniu od `EUREKA_SERVER_URL` klienta Python z LAB3, adres `GATEWAY_EUREKA_URL` zawiera `/eureka/`. Nie należy przenosić bramki do kontenera bez zmiany adresów: `127.0.0.1` oznacza wtedy kontener, a nie komputer z usługami.

## Uruchomienie testów integracyjnych

Przy działających czterech procesach (Eureka, dwie usługi demo, gateway), w nowym terminalu w katalogu `lab4-support` należy wykonać:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

Testy wykonują prawdziwe żądania HTTP i niczego nie uruchamiają automatycznie. Należy oczekiwać `5 passed`. Błąd połączenia przy wyłączonym gateway nie oznacza błędu instalacji pytest. Przy innym porcie bramki należy ustawić `GATEWAY_URL`, np. `$env:GATEWAY_URL = 'http://127.0.0.1:8088'`.

Własny projekt wymaga innych nazw, ścieżek i danych testowych. Nie należy traktować pięciu testów demo jako własnych testów projektu. Scenariusze awarii należy wykonać oddzielnie, zgodnie z instrukcją główną.

## Zatrzymanie procesów

Bramkę należy zatrzymać skrótem `Ctrl+C` w jej terminalu. Następnie należy zatrzymać własne procesy usług oraz Eurekę metodą wybraną na LAB3. Nie należy usuwać baz ani cache w celu zatrzymania aplikacji.
