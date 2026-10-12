# Konspekt pierwszego laboratorium

## Projektowanie aplikacji webowych opartych o mikrousługi

**Temat:** Od problemu biznesowego do pierwszej mikrousługi  
**Czas:** 90–120 minut  
**Forma:** praca indywidualna lub w parach  
**Rezultat:** propozycja architektury oraz działająca pierwsza usługa webowa

---

## 1. Cel ćwiczenia

Celem ćwiczenia jest przejście od opisu problemu biznesowego do zaprojektowania i uruchomienia pierwszej mikrousługi.

Po wykonaniu ćwiczenia student powinien:

- rozróżniać monolit i architekturę mikroserwisową,
- wskazać podstawowe obszary domeny,
- zaproponować granice mikroserwisów,
- zdefiniować prosty kontrakt HTTP/REST,
- uruchomić usługę udostępniającą dane.

---

## 2. Wybór domeny

Wybierz jeden temat albo zaproponuj własny po uzgodnieniu z prowadzącym.

### Temat A — system zamówień

System obsługuje produkty, zamówienia, płatności i powiadomienia.

### Temat B — system rezerwacji wizyt

System obsługuje klientów, pracowników, terminy i rezerwacje.

### Temat C — system wydarzeń

System obsługuje wydarzenia, uczestników, bilety i płatności.

### Temat D — własny pomysł

Własny temat powinien mieć co najmniej trzy różne obszary odpowiedzialności.

---

## 3. Zadanie 1 — opis problemu

W 5–10 zdaniach opisz:

- jaki problem rozwiązuje system,
- kto będzie jego użytkownikiem,
- jakie są trzy najważniejsze funkcje,
- jakie dane będą przechowywane,
- jakie działania mogą wywoływać zmiany w systemie.

### Przykład

System zamówień pozwala klientowi przeglądać produkty i składać zamówienia. Klient może dodać produkty do zamówienia, a następnie je opłacić. System powinien sprawdzać dostępność produktów i informować klienta o statusie zamówienia.

---

## 4. Zadanie 2 — pojęcia i zdarzenia domenowe

Wypiszcie:

### Główne pojęcia

Przykład:

- Produkt,
- Klient,
- Zamówienie,
- Płatność,
- Dostawa.

### Zdarzenia

Przykład:

- Zamówienie utworzone,
- Produkt zarezerwowany,
- Płatność zaakceptowana,
- Zamówienie wysłane.

### Polecenia

Przykład:

- Utwórz zamówienie,
- Zarezerwuj produkt,
- Opłać zamówienie,
- Wyślij powiadomienie.

---

## 5. Zadanie 3 — propozycja mikroserwisów

Zaproponuj od 2 do 4 mikroserwisów.

Uzupełnij tabelę:

| Mikroserwis | Za co odpowiada? | Jakie dane posiada? | Przykładowe operacje |
|---|---|---|---|
| Product Service | Produkty i ceny | Produkty | Pobierz produkt, dodaj produkt |
| Order Service | Zamówienia | Zamówienia | Utwórz zamówienie, zmień status |
| Payment Service | Płatności | Płatności | Rozpocznij płatność |

### Pytania pomocnicze

- Czy każda usługa ma jedną spójną odpowiedzialność?
- Czy podział wynika z domeny, a nie tylko z tabel w bazie?
- Czy usługi można rozwijać względnie niezależnie?
- Czy jedna usługa nie przejmuje zbyt wielu obowiązków?

---

## 6. Zadanie 4 — wybór pierwszej usługi

Wybierz jedną usługę do implementacji.

Najlepiej zacząć od usługi, która:

- ma prosty model danych,
- nie wymaga jeszcze komunikacji z innymi usługami,
- może zwrócić użyteczną odpowiedź HTTP,
- będzie potrzebna w dalszej części projektu.

Rekomendowana opcja: `Product Service`.

---

## 7. Zadanie 5 — definicja API

Zaprojektuj minimum dwa endpointy.

### Przykład

| Metoda | Endpoint | Opis | Kod sukcesu |
|---|---|---|---|
| GET | `/products` | Pobiera listę produktów | 200 |
| GET | `/products/{id}` | Pobiera produkt po identyfikatorze | 200 |
| POST | `/products` | Dodaje produkt | 201 |

Zdefiniuj również przykładową odpowiedź JSON:

```json
{
  "id": 1,
  "name": "Klawiatura mechaniczna",
  "price": 249.99,
  "available": true
}
```

Ustal, co powinno się stać, gdy:

- produkt nie istnieje,
- klient prześle niepoprawne dane,
- cena będzie ujemna,
- zabraknie wymaganego pola.

---

## 8. Zadanie 6 — implementacja

Utwórz aplikację webową w wybranej technologii, np. Java/Spring Boot lub .NET.

Minimalne wymagania:

- aplikacja uruchamia się lokalnie,
- usługa działa na określonym porcie,
- istnieje endpoint listujący dane,
- istnieje endpoint pobierający pojedynczy element,
- odpowiedzi mają format JSON,
- obsłużony jest przypadek braku elementu,
- kod jest umieszczony w repozytorium.

Na tym etapie dane mogą być przechowywane w pamięci aplikacji. Baza danych i Docker pojawią się w kolejnych ćwiczeniach.

---

## 9. Testowanie usługi

Sprawdź usługę przy użyciu przeglądarki, Swaggera, Postmana albo `curl`.

Przetestuj co najmniej:

1. pobranie listy,
2. pobranie istniejącego elementu,
3. pobranie nieistniejącego elementu,
4. wysłanie niepoprawnych danych, jeśli zaimplementowano `POST`.

Zapisz przykładowe żądania i odpowiedzi.

---

## 10. Minimalny rezultat do oddania

Oddaj:

- krótki opis domeny,
- diagram lub schemat proponowanej architektury,
- tabelę mikroserwisów,
- definicję API pierwszej usługi,
- kod źródłowy,
- instrukcję uruchomienia,
- przykłady testów.

---

## 11. Kryteria oceny ćwiczenia

Ćwiczenie może być oceniane punktowo lub jako zaliczone/niezaliczone.

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

## 12. Pytania do podsumowania

Odpowiedz krótko:

1. Dlaczego wybrałeś taki podział na mikroserwisy?
2. Które dane powinny należeć do pierwszej usługi?
3. Co stanie się, jeśli jedna usługa przestanie działać?
4. Czy pierwsza usługa mogłaby być częścią monolitu? Jakie byłyby konsekwencje?
5. Jakie informacje powinny znaleźć się w dokumentacji API?

---

## Zadanie na kolejne zajęcia

Rozbuduj pierwszą usługę o persystencję danych przy użyciu wybranej bazy danych. Przygotuj również wstępną propozycję komunikacji pomiędzy pierwszą i drugą usługą.
