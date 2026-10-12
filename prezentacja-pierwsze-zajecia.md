# Projektowanie aplikacji webowych opartych o mikrousługi

## Pierwsze zajęcia: od monolitu do pierwszej mikrousługi

**Czas:** około 30 minut  
**Cel:** zrozumieć, czym są mikrousługi, po co stosuje się DDD i jak rozpocząć projekt systemu rozproszonego.

---

## Slajd 1 — O czym jest ten przedmiot?

Na zajęciach zbudujemy mały system webowy składający się z kilku mikrousług.

W kolejnych tygodniach pojawią się:

- niezależne usługi,
- komunikacja REST,
- API Gateway,
- rejestr usług,
- komunikacja asynchroniczna,
- RabbitMQ,
- Docker,
- dokumentacja i testowanie.

**Notatka dla prowadzącego:**

Powiedz studentom, że nie będziemy tylko omawiać teorii. Każdy element będzie stopniowo dodawany do jednego projektu.

---

## Slajd 2 — Problem biznesowy

Wyobraźmy sobie internetowy system obsługi zamówień.

System powinien umożliwiać:

- przeglądanie produktów,
- tworzenie zamówień,
- sprawdzanie dostępności produktów,
- obsługę płatności,
- wysyłanie powiadomień.

Pytanie:

> Czy wszystkie funkcje powinny znajdować się w jednym programie?

**Notatka dla prowadzącego:**

Poproś studentów o krótkie propozycje. Nie oceniaj jeszcze odpowiedzi — chodzi o pokazanie, że podział systemu jest decyzją projektową.

---

## Slajd 3 — Monolit

Monolit to aplikacja, w której główne funkcje systemu są wdrażane jako jedna całość.

```text
+------------------------------------------+
|              Aplikacja                   |
|                                          |
|  Produkty | Zamówienia | Płatności      |
|  Dostawy  | Powiadomienia               |
|                                          |
|              Jedna baza danych           |
+------------------------------------------+
```

### Zalety

- prostszy start,
- łatwe uruchamianie lokalne,
- komunikacja w pamięci procesu,
- prostsze transakcje.

### Problemy przy rozwoju

- duża liczba zależności,
- trudniejsze niezależne wdrażanie funkcji,
- cały system może wymagać skalowania,
- awaria jednego elementu może wpływać na całość.

---

## Slajd 4 — Czym jest mikrousługa?

Mikrousługa to niewielka, samodzielna część systemu, która:

- ma jasno określoną odpowiedzialność,
- udostępnia interfejs,
- może być niezależnie rozwijana i wdrażana,
- komunikuje się z innymi usługami przez sieć.

Przykład:

```text
Product Service       — produkty i ceny
Order Service         — zamówienia
Payment Service       — płatności
Notification Service  — powiadomienia
```

Mikrousługa nie jest po prostu „jedną tabelą wystawioną przez REST”.

---

## Slajd 5 — Przykładowa architektura

```text
                 +----------------+
                 |    Klient      |
                 +--------+-------+
                          |
                 +--------v-------+
                 |   API Gateway  |
                 +---+--------+---+
                     |        |
          +----------v--+  +--v-----------+
          | Product      |  | Order        |
          | Service      |  | Service      |
          +------+------+  +------+-------+
                 |                |
          +------v------+  +------v-------+
          | Product DB  |  | Order DB     |
          +-------------+  +--------------+
```

Każda usługa powinna mieć własną odpowiedzialność i możliwie niezależne dane.

---

## Slajd 6 — Co zyskujemy?

Mikrousługi mogą zapewnić:

- niezależne wdrażanie,
- możliwość skalowania wybranych elementów,
- izolowanie części systemu,
- dopasowanie technologii do problemu,
- pracę kilku zespołów nad różnymi obszarami.

Ale pojawiają się również koszty:

- komunikacja sieciowa,
- opóźnienia i błędy połączeń,
- trudniejsze testowanie,
- rozproszone dane,
- konieczność monitorowania wielu procesów.

**Najważniejsza myśl:**

> Mikrousługi nie są automatycznie lepsze od monolitu. Są narzędziem do rozwiązywania określonych problemów.

---

## Slajd 7 — DDD, czyli projektowanie sterowane domeną

DDD (*Domain-Driven Design*) oznacza projektowanie systemu wokół problemu biznesowego, który system ma rozwiązać.

Najpierw pytamy:

- jakie pojęcia występują w domenie?
- jakie reguły obowiązują?
- jakie procesy zachodzą?
- kto jest odpowiedzialny za poszczególne działania?

Dopiero potem wybieramy klasy, moduły, bazy danych i frameworki.

---

## Slajd 8 — Przykład domeny zamówień

W domenie sklepu występują między innymi:

- Produkt,
- Koszyk,
- Zamówienie,
- Klient,
- Płatność,
- Dostawa.

Przykładowe zdarzenia:

- Zamówienie utworzone,
- Produkt zarezerwowany,
- Płatność zaakceptowana,
- Zamówienie wysłane.

Przykładowe polecenia:

- Utwórz zamówienie,
- Zarezerwuj produkt,
- Opłać zamówienie,
- Wyślij powiadomienie.

---

## Slajd 9 — Granice odpowiedzialności

Możliwy podział domeny:

```text
Product Service
  - produkty
  - ceny
  - dostępność

Order Service
  - koszyk
  - zamówienie
  - status zamówienia

Payment Service
  - płatność
  - status płatności
```

Dobra granica oznacza, że usługa:

- ma spójną odpowiedzialność,
- nie wymaga ciągłego zaglądania do danych innej usługi,
- może być rozwijana w dużej mierze niezależnie.

---

## Slajd 10 — Jak rozpoznać złą granicę?

Podejrzany podział:

```text
CustomerTableService
ProductTableService
OrderTableService
```

To może być tylko podział techniczny według tabel.

Lepsze pytania:

- jaka część systemu ma własne reguły?
- która część zmienia się niezależnie?
- jaki zespół lub osoba za nią odpowiada?
- czy usługa może działać bez ciągłego odpytywania innych usług?

---

## Slajd 11 — Kontrakt API

Usługa komunikuje się ze światem przez określony kontrakt.

Przykład API `Product Service`:

```http
GET /products
GET /products/{id}
POST /products
```

Przykładowa odpowiedź:

```json
{
  "id": 1,
  "name": "Klawiatura mechaniczna",
  "price": 249.99,
  "available": true
}
```

Kontrakt powinien być:

- prosty,
- jednoznaczny,
- udokumentowany,
- stabilny dla klientów usługi.

---

## Slajd 12 — Zadanie na dziś

W ramach laboratorium:

1. wybierzcie domenę systemu,
2. wypiszcie główne pojęcia i procesy,
3. zaproponujcie 2–4 mikroserwisy,
4. wybierzcie jedną usługę do implementacji,
5. zdefiniujcie jej API,
6. uruchomcie prostą implementację.

Na koniec powinna działać przynajmniej jedna usługa z jednym lub dwoma endpointami.

---

## Slajd 13 — Podsumowanie

- Monolit jest prosty na początku, ale może być trudniejszy w rozwoju.
- Mikrousługa ma jasno określoną odpowiedzialność i własny interfejs.
- DDD pomaga wyznaczać granice usług na podstawie domeny biznesowej.
- Mikrousługi przynoszą zarówno korzyści, jak i dodatkową złożoność.
- Dobry projekt zaczyna się od problemu, a nie od wyboru frameworka.

**Pytanie końcowe do grupy:**

> Jakie dwie usługi wydzielilibyście jako pierwsze w systemie obsługi zamówień i dlaczego?

