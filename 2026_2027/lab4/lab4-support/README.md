# Pakiet pomocniczy LAB4

Pakiet należy wykorzystać razem z serwerem Eureka oraz dwiema usługami demonstracyjnymi z pakietu pomocniczego LAB3. Zawiera on gotowy szkielet bramki Spring Cloud Gateway (Server WebFlux), zestaw pięciu testów integracyjnych przykładu oraz szablon dokumentacji etapu LAB4. Pakiet nie zawiera kopii usług domenowych ani bazy danych.

## Wymagania wstępne

- JDK 21 oraz Apache Maven 3.9.x (do uruchomienia bramki API Gateway),
- Python 3.12 lub nowszy (do uruchomienia usług z LAB3 oraz testów integracyjnych),
- wolny port `8080` dla bramki (oraz porty `8761`, `8101` i `8102` dla komponentów z LAB3).

Bramkę należy uruchamiać lokalnie w tym samym systemie operacyjnym co usługi Python. Serwer Eureka może działać w wariancie wybranym na LAB3 (Docker Compose albo Maven).

## Uruchomienie przykładu i weryfikacja bramki

Przed uruchomieniem bramki należy w osobnych terminalach uruchomić serwer Eureka (`:8761`) oraz dwie usługi demonstracyjne z pakietu `lab3-support`: `LOCKER-SERVICE` (`:8101`) i `PARCEL-SERVICE` (`:8102`).

Następnie z katalogu `lab4-support` należy wykonać:

```powershell
java -version
mvn -version
Set-Location .\gateway
mvn spring-boot:run
```

Podczas pierwszego uruchomienia Maven pobierze wymagane zależności. Po starcie aplikacji w osobnym terminalu należy zweryfikować działanie endpointu własnego bramki oraz obu skonfigurowanych tras:

```powershell
curl.exe -i http://127.0.0.1:8080/health
curl.exe -i http://127.0.0.1:8080/api/lockers/KRK-1024
curl.exe -i http://127.0.0.1:8080/api/delivery-check/KRK-1024
```

Wszystkie trzy żądania powinny zwrócić kod `200 OK`, przy czym odpowiedzi z tras domenowych zawierają nagłówek `X-Gateway: lab4`. Po pierwszym zarejestrowaniu usług w Eurece może być konieczne krótkie odczekanie na odświeżenie lokalnej kopii rejestru w bramce.

Konfiguracja tras znajduje się w pliku `gateway/src/main/resources/application.yml`. Każda zmiana tego pliku wymaga ponownego uruchomienia procesu Maven (`Ctrl+C` i ponowne `mvn spring-boot:run`). Trasy odwołują się do usług przez nazwy logiczne z Eureki (`lb://LOCKER-SERVICE`, `lb://PARCEL-SERVICE`). Bramka pobiera rejestr (`fetch-registry: true`), ale sama nie rejestruje swojej instancji (`register-with-eureka: false`), dlatego nie pojawia się na liście instancji w panelu Eureki.

W razie potrzeby port nasłuchiwania bramki lub adres rejestru Eureka można zmienić przed uruchomieniem Mavena w tym samym terminalu:

```powershell
$env:GATEWAY_PORT = '8080'
$env:GATEWAY_EUREKA_URL = 'http://127.0.0.1:8761/eureka/'
```

Należy pamiętać, że w konfiguracji Spring Cloud adres `GATEWAY_EUREKA_URL` musi kończyć się sufiksem `/eureka/`.

## Uruchomienie testów integracyjnych przykładu

Przy działających czterech procesach (Eureka Server, `LOCKER-SERVICE`, `PARCEL-SERVICE` oraz `API Gateway`), w nowym terminalu otwartym w katalogu `lab4-support` należy wykonać:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

Testy w `tests/test_gateway_demo.py` wysyłają rzeczywiste żądania HTTP do uruchomionej bramki i oczekują wyniku `5 passed`. Jeżeli zmieniono port bramki, przed uruchomieniem `pytest` należy ustawić zmienną `$env:GATEWAY_URL = 'http://127.0.0.1:8088'`.

We własnym projekcie należy skopiować katalog `gateway` (bez `target/`) do repozytorium projektu z LAB1–LAB3, zastąpić trasy demonstracyjne własnymi oraz przygotować co najmniej cztery własne testy integracyjne zgodnie z główną instrukcją LAB4.

## Zatrzymanie procesów

Proces bramki należy zatrzymać skrótem `Ctrl+C` w terminalu Mavena. Następnie należy zatrzymać obie usługi Python oraz serwer Eureka metodą wybraną w LAB3.
