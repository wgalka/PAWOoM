# LAB1 — Od problemu biznesowego do pierwszej mikrousługi

**Czas:** 90–120 minut  
**Forma:** praca indywidualna lub w parach  
**Rezultat:** działająca usługa według opisu oraz propozycja własnego projektu mikroserwisowego

---

## 1. Cel ćwiczenia

Po wykonaniu ćwiczenia student powinien:

- rozróżniać monolit i architekturę mikroserwisową,
- wskazać podstawowe obszary domeny,
- zaproponować granice mikroserwisów,
- zdefiniować prosty kontrakt HTTP/REST,
- uruchomić usługę udostępniającą dane.

---

## 2. Organizacja pracy

Laboratorium składa się z dwóch etapów.

### Etap A — zadanie wspólne

Wszyscy pracują na tym samym, przygotowanym przez prowadzącego przykładzie. Celem jest poznanie sposobu pracy: analiza domeny, określenie odpowiedzialności usługi, zaprojektowanie API i uruchomienie aplikacji.

### Etap B — własny projekt

Po wykonaniu przykładu studenci pracują indywidualnie lub w parach. Sami wybierają problem, dyskutują jego zakres i proponują własny podział na mikroserwisy.

Nie należy zaczynać od wyboru technologii. Najpierw trzeba określić problem i odpowiedzialności biznesowe.

---

## 3. Etap A — zadanie wspólne: Building Service

### Opis problemu

Inteligentny budynek potrzebuje usługi odpowiedzialnej za ewidencję budynków, pomieszczeń i urządzeń. Usługa udostępnia podstawowe informacje innym częściom systemu.

Usługa nie obsługuje jeszcze automatyzacji, alarmów, zużycia energii ani uprawnień użytkowników. Jej odpowiedzialność ogranicza się do opisu infrastruktury budynku.

### Model pomieszczenia

Pomieszczenie posiada:

- identyfikator,
- nazwę,
- typ,
- piętro,
- maksymalną liczbę osób,
- status zajętości.

### Wymagane API

| Metoda | Endpoint | Opis | Kod sukcesu |
|---|---|---|---|
| GET | `/rooms` | Pobiera listę pomieszczeń | 200 |
| GET | `/rooms/{id}` | Pobiera pomieszczenie po identyfikatorze | 200 |
| POST | `/rooms` | Dodaje pomieszczenie | 201 |

### Przykładowa odpowiedź

```json
{
  "id": 1,
  "name": "Sala konferencyjna A",
  "type": "conference_room",
  "floor": 2,
  "capacity": 12,
  "occupancy_status": "free"
}
```

### Zadania do wykonania

1. Utwórz aplikację FastAPI lub w innej uzgodnionej technologii.
2. Zaimplementuj model pomieszczenia.
3. Dodaj minimum dwa endpointy.
4. Zwracaj dane w formacie JSON.
5. Obsłuż przypadek nieistniejącego pomieszczenia.
6. Sprawdź API w Swaggerze, Postmanie albo przez `curl`.

Na tym etapie dane mogą być przechowywane w pamięci aplikacji. Baza danych, sensory i Docker pojawią się w kolejnych ćwiczeniach.

---

## 4. Dyskusja po zadaniu wspólnym

Po uruchomieniu `Building Service` odpowiedzcie wspólnie:

- Czy ta usługa mogłaby być częścią monolitu?
- Jakie funkcje powinny należeć do `Automation Service`?
- Czy `Building Service` powinien znać dane użytkowników budynku?
- Co się stanie, gdy usługa budynku będzie niedostępna?
- Jakie informacje musi znać usługa rezerwacji sali?

Prowadzący powinien wykorzystać tę rozmowę do wprowadzenia pojęć: granica odpowiedzialności, kontrakt API, sprzężenie i spójność.

---

## 5. Etap B — wybór własnego projektu

### Wymagania dotyczące tematu

Własny temat powinien:

- rozwiązywać konkretny problem,
- mieć co najmniej trzy obszary odpowiedzialności,
- umożliwiać wydzielenie minimum dwóch mikroserwisów,
- zawierać proces, w którym później można zastosować komunikację asynchroniczną.

### Przykładowe kierunki

Wybierz jeden temat albo zaproponuj własny po uzgodnieniu z prowadzącym.

### Temat A — system zarządzania budynkiem

Pomieszczenia, urządzenia, sensory, alarmy i automatyzacja.

### Temat B — system zarządzania energią

Liczniki, zużycie, taryfy, prognozy i sterowanie urządzeniami.

### Temat C — system bezpieczeństwa budynku

Uprawnienia, wejścia, alarmy, monitoring i obsługa incydentów.

### Temat D — własny pomysł

Własny temat powinien mieć co najmniej trzy różne obszary odpowiedzialności.

---

## 6. Zadanie 1 — opis własnego problemu

W 5–10 zdaniach opisz:

- jaki problem rozwiązuje system,
- kto będzie jego użytkownikiem,
- jakie są trzy najważniejsze funkcje,
- jakie dane będą przechowywane,
- jakie działania mogą wywoływać zmiany w systemie.

---

## 7. Zadanie 2 — pojęcia i zdarzenia domenowe

Wypiszcie główne pojęcia, zdarzenia i polecenia.

### Przykład dla inteligentnego budynku

**Pojęcia:** Budynek, Pomieszczenie, Sensor, Urządzenie, Użytkownik, Alarm.  
**Zdarzenia:** Temperatura przekroczona, Pomieszczenie zajęte, Wykryto ruch, Alarm uruchomiony.  
**Polecenia:** Zarezerwuj salę, Włącz światło, Zmień temperaturę, Potwierdź alarm.

---

## 8. Zadanie 3 — propozycja mikroserwisów

Zaproponuj od 2 do 4 mikroserwisów.

| Mikroserwis | Za co odpowiada? | Jakie dane posiada? | Przykładowe operacje |
|---|---|---|---|
| Building Service | Budynki i pomieszczenia | Budynki, sale | Pobierz, dodaj |
| Device Service | Urządzenia i sensory | Urządzenia, odczyty | Zarejestruj, odczytaj |
| Automation Service | Reguły automatyzacji | Reguły, scenariusze | Włącz, wyłącz |
| Alert Service | Alarmy i incydenty | Alarmy | Utwórz, potwierdź |

Odpowiedz:

- Czy każda usługa ma jedną spójną odpowiedzialność?
- Czy podział wynika z domeny, a nie tylko z tabel?
- Czy usługi można rozwijać względnie niezależnie?

---

## 9. Zadanie 4 — wybór pierwszej usługi własnego projektu

Wybierz jedną usługę do implementacji. Rekomendowana opcja to `Building Service`, ponieważ może działać bez komunikacji z innymi usługami.

Na tym etapie dane mogą być przechowywane w pamięci aplikacji. Baza danych i Docker pojawią się w kolejnych ćwiczeniach.

---

## 10. Zadanie 5 — definicja API własnej usługi

Zaprojektuj minimum dwa endpointy.

| Metoda | Endpoint | Opis | Kod sukcesu |
|---|---|---|---|
| GET | `/rooms` | Pobiera listę pomieszczeń | 200 |
| GET | `/rooms/{id}` | Pobiera pomieszczenie po identyfikatorze | 200 |
| POST | `/rooms` | Dodaje pomieszczenie | 201 |

Przykładowa odpowiedź:

```json
{
  "id": 1,
  "name": "Sala konferencyjna A",
  "type": "conference_room",
  "floor": 2,
  "capacity": 12,
  "occupancy_status": "free"
}
```

Ustal, co stanie się, gdy:

- pomieszczenie nie istnieje,
- klient prześle niepoprawne dane,
- pojemność będzie ujemna,
- zabraknie wymaganego pola.

---

## 11. Zadanie 6 — implementacja

Utwórz aplikację webową w wybranej technologii, np. Java/Spring Boot lub .NET.

Minimalne wymagania:

- aplikacja uruchamia się lokalnie,
- usługa działa na określonym porcie,
- istnieje endpoint listujący dane,
- istnieje endpoint pobierający pojedynczy element,
- odpowiedzi mają format JSON,
- obsłużony jest przypadek braku elementu,
- kod znajduje się w repozytorium.

---

## 12. Testowanie

Przetestuj co najmniej:

1. pobranie listy,
2. pobranie istniejącego elementu,
3. pobranie nieistniejącego elementu,
4. wysłanie niepoprawnych danych, jeśli zaimplementowano `POST`.

Użyj przeglądarki, Swaggera, Postmana albo `curl`.

---

## 13. Minimalny rezultat do oddania

- opis domeny,
- schemat proponowanej architektury,
- tabela mikroserwisów,
- definicja API pierwszej usługi,
- kod źródłowy,
- instrukcja uruchomienia,
- przykłady testów.

---

## 14. Kryteria oceny

| Element | Punkty |
|---|---:|
| Opis problemu i domeny | 10 |
| Sensowny podział na mikroserwisy | 20 |
| Poprawny kontrakt API | 20 |
| Działająca implementacja | 30 |
| Obsługa błędów i testy | 10 |
| Czytelność dokumentacji | 10 |
| **Razem** | **100** |

---

## 15. Pytania podsumowujące

1. Dlaczego wybrałeś taki podział na mikroserwisy?
2. Które dane powinny należeć do pierwszej usługi?
3. Co stanie się, jeśli jedna usługa przestanie działać?
4. Czy pierwsza usługa mogłaby być częścią monolitu?
5. Jakie informacje powinny znaleźć się w dokumentacji API?

## Zadanie na kolejne zajęcia

Rozbuduj pierwszą usługę o persystencję danych przy użyciu wybranej bazy danych. Przygotuj również wstępną propozycję komunikacji pomiędzy pierwszą i drugą usługą.
