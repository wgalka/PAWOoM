## Etap LAB3 — rejestracja i odnajdywanie usług

### Usługi i granice odpowiedzialności

| Usługa | Odpowiedzialność | Właściciel danych | Nazwa w Eurece | Port |
|---|---|---|---|---:|
| … | … | … | … | … |
| … | … | … | … | … |

### Konfiguracja i uruchomienie

- wersja Pythona i zależności:
- adres Eureka Server:
- konfiguracja każdej instancji:
- komendy uruchomienia i testów:

Nie zapisuj haseł ani lokalnych sekretów w repozytorium. Adresy, porty i nazwy powinny być zgodne z uruchomionymi procesami.

### Kontrakt komunikacji między usługami

- usługa wywołująca:
- nazwa logiczna odnajdywanej usługi:
- metoda i ścieżka HTTP:
- dane wejściowe i odpowiedź:
- sposób obsługi błędów zależności:

### Wyniki weryfikacji

| Scenariusz | Żądanie lub czynność | Oczekiwany wynik | Wynik rzeczywisty |
|---|---|---|---|
| Rejestracja | Panel Eureka po uruchomieniu obu usług | Obie instancje `UP` | … |
| Odnajdywanie | Wywołanie przepływu między usługami | Odpowiedź z zależnej usługi | … |
| Błąd zależności | Zatrzymanie jednej usługi i ponowienie żądania | Kontrolowany kod HTTP | … |
| Test jednostkowy | `pytest` bez Eureka Server | Testy przechodzą z zamiennikiem klienta | … |

### Ograniczenia i dokumentacja

- zachowanie po niedostępności usługi lub rejestru:
- obserwacja czasu wygaśnięcia wpisu:
- dwa wykorzystane źródła dokumentacji i sprawdzone wersje:
- sposób weryfikacji sugestii AI:

### Wkład autorów

- osoba 1:
- osoba 2:
