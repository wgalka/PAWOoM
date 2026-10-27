## Etap LAB4 — konfiguracja wspólnego punktu wejścia (API Gateway)

### Autorzy i ciągłość projektu z LAB1–LAB3

- Autorzy i indywidualny wkład każdej osoby w parze:
- Temat projektu oraz zachowane komponenty z LAB1–LAB3 (pierwsza usługa z bazą SQLite i cache Redis, druga usługa, Eureka Server):
- Dodane i zmodyfikowane pliki w repozytorium:

### Kontrakt wejściowy i granice odpowiedzialności

| Metoda i ścieżka klienta (`:8080`) | Identyfikator trasy (`id`) | Usługa docelowa w Eurece (`uri`) | Ścieżka wewnętrzna po `StripPrefix` | Właściciel danych i uzasadnienie udostępnienia |
|---|---|---|---|---|
| Do uzupełnienia | | | | |

- Endpointy pozostawione wyłącznie wewnątrz usług (nieudostępnione w bramce) wraz z uzasadnieniem:
- Podział odpowiedzialności pomiędzy API Gateway, Eureka Server oraz dwie usługi domenowe (właściciele danych, cache i reguły biznesowej):
- Uzasadnienie limitów `connect-timeout` i `response-timeout` względem limitu wywołania usługa–usługa z LAB3:
- Diagram przepływu żądania przez bramkę, odnajdywania w Eurece, komunikacji między usługami oraz dostępu do SQLite i Redis:

### Uruchomienie, weryfikacja i zatrzymanie środowiska

- Wersje narzędzi (Python, JDK, Apache Maven, użyte biblioteki):
- Zestaw wymaganych procesów, ich katalogi robocze, porty oraz zmienne środowiskowe:
- Polecenia uruchomienia procesów we właściwej kolejności:
- Sposób przygotowania danych testowych bez kasowania bazy danych projektu:
- Polecenie uruchomienia dotychczasowych testów jednostkowych (LAB1–LAB3):
- Polecenie uruchomienia testów integracyjnych przechodzących przez bramkę (LAB4):
- Polecenia poprawnego zatrzymania procesów:

### Wyniki weryfikacji i eksperymentów awarii

| Scenariusz | Żądanie i stan procesów | Oczekiwany wynik | Rzeczywisty status, treść i nagłówki (`X-Gateway`, `X-Cache`) | Wniosek techniczny |
|---|---|---|---|---|
| Odczyt z pierwszej usługi przez bramkę (MISS → HIT) | | | | |
| Zapis przez bramkę, unieważnienie cache i ponowny odczyt | | | | |
| Błąd walidacji (`422`) i reguły biznesowej (`409`) przez bramkę | | | | |
| Odczyt z drugiej usługi przez bramkę (przepływ z LAB3) | | | | |
| Brak zasobu (`404` z usługi) vs brak trasy (`404` z bramki) | | | | |
| Zatrzymana druga usługa (wywołująca) | | | | |
| Zatrzymana pierwsza usługa (zależność z LAB3) | | | | |
| Ponowne uruchomienie zatrzymanej usługi i odświeżenie rejestru | | | | |
| Zatrzymany proces `API Gateway` | | | | |

- Wykaz co najmniej czterech własnych testów integracyjnych (nazwy funkcji testowych i sprawdzane asercje):
- Zaobserwowane opóźnienia aktualizacji rejestru oraz ograniczenia zastosowanego rozwiązania:

### Wykorzystana dokumentacja techniczna (EK_03) i użycie AI

| Źródło oficjalnej dokumentacji i wersja | Rozwiązywany problem | Zastosowana konfiguracja lub rozwiązanie | Sposób weryfikacji działania |
|---|---|---|---|
| Do uzupełnienia (1) | | | |
| Do uzupełnienia (2) | | | |

- Zakres wykorzystania narzędzi AI oraz sposób samodzielnej weryfikacji wygenerowanych fragmentów (albo „nie korzystano”):
