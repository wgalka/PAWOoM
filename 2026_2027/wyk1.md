# WYK1 — Od monolitu do pierwszej mikrousługi

**Czas:** około 30 minut  
**Cel:** wyjaśnić podstawy mikroserwisów, DDD i granic odpowiedzialności.

---

## 1. O czym jest przedmiot?

W ramach przedmiotu zbudujemy mały system webowy składający się z kilku mikrousług.

W kolejnych zajęciach pojawią się:

- niezależne usługi,
- komunikacja REST,
- API Gateway,
- rejestr usług,
- RabbitMQ,
- Docker,
- dokumentacja i testowanie.

Nie chodzi tylko o poznanie narzędzi. Najważniejsze jest zrozumienie, jak dzielić system na odpowiedzialne części.

---

## 2. Przykład problemu

Rozważmy system inteligentnego budynku. Powinien umożliwiać:

- monitorowanie pomieszczeń i urządzeń,
- odczytywanie danych z sensorów,
- automatyczne sterowanie oświetleniem i temperaturą,
- obsługę alarmów,
- zarządzanie dostępem użytkowników.

Pytanie do grupy:

> Czy wszystkie funkcje powinny znajdować się w jednym programie?

---

## 3. Monolit

Monolit jest aplikacją wdrażaną jako jedna całość.

```text
+------------------------------------------+
|              Aplikacja                   |
| Pomieszczenia | Urządzenia | Automatyzacja |
| Alarmy       | Dostęp     | Energia       |
|              Jedna baza danych           |
+------------------------------------------+
```

### Zalety

- prosty start,
- łatwe uruchamianie,
- komunikacja w pamięci procesu,
- prostsze transakcje.

### Problemy przy rozwoju

- rosnąca liczba zależności,
- trudniejsze niezależne wdrażanie,
- konieczność skalowania całej aplikacji,
- większe ryzyko wpływu awarii na całość.

---

## 4. Mikrousługa

Mikrousługa to samodzielna część systemu, która ma:

- jasno określoną odpowiedzialność,
- własny interfejs,
- możliwość niezależnego rozwoju i wdrażania,
- komunikację z innymi usługami przez sieć.

Przykładowy podział:

```text
Building Service      — budynki i pomieszczenia
Device Service        — urządzenia i sensory
Automation Service    — reguły automatyzacji
Alert Service         — alarmy i incydenty
```

Mikrousługa nie jest po prostu pojedynczą tabelą wystawioną przez REST.

---

## 5. Korzyści i koszty

### Praktyczny przykład: awaria części systemu

Wyobraźmy sobie system paczkomatów. Moduł powiadomień zawiera błąd, który kończy proces aplikacji.

W monolicie wszystkie funkcje są częścią jednego procesu:

```text
Paczkomaty + paczki + śledzenie + powiadomienia
                  |
             jeden proces
```

Ponieważ wszystkie moduły działają w jednym procesie, awaria modułu powiadomień może zakończyć cały proces. Wtedy użytkownicy mogą stracić dostęp również do produktów, paczek i śledzenia. Trzeba jednak odróżnić tę sytuację od zwykłego błędu HTTP 500, który często kończy tylko jedno żądanie, a proces nadal działa.

W architekturze mikroserwisowej powiadomienia mogą działać osobno:

```text
Locker Service       działa
Parcel Service       działa
Tracking Service     działa
Notification Service awaria
```

Użytkownik nadal może sprawdzić status paczki albo odebrać przesyłkę. Powiadomienie może zostać wysłane później, gdy usługa wróci do działania.

Mikroserwisy nie rozwiązują jednak wszystkich problemów. Awaria może objąć większą część systemu, jeśli przestanie działać:

- API Gateway,
- usługa uwierzytelniania,
- wspólna baza danych,
- broker wiadomości,
- usługa, od której zależą wszystkie pozostałe komponenty.

Może też wystąpić awaria kaskadowa: jedna niedostępna usługa powoduje błędy w kolejnych usługach. Dlatego potrzebne są timeouty, retry, circuit breaker, kolejki, cache i monitorowanie.

**Wniosek:** w monolicie błąd zabijający wspólny proces może wyłączyć wszystkie moduły naraz. W mikroserwisach podobny błąd zwykle zabija tylko proces jednej usługi, o ile pozostałe usługi nie są od niej krytycznie zależne.

### Korzyści

- niezależne wdrażanie,
- skalowanie wybranych elementów,
- izolowanie części systemu,
- możliwość pracy kilku zespołów.

### Koszty

- komunikacja sieciowa,
- opóźnienia i błędy połączeń,
- trudniejsze testowanie,
- rozproszone dane,
- potrzeba monitorowania wielu procesów.

> Mikrousługi nie są automatycznie lepsze od monolitu. Są narzędziem do rozwiązywania określonych problemów.

---

## 6. DDD — projektowanie sterowane domeną

DDD (*Domain-Driven Design*) oznacza projektowanie systemu wokół problemu biznesowego.

Najpierw pytamy:

- jakie pojęcia występują w domenie?
- jakie reguły obowiązują?
- jakie procesy zachodzą?
- kto odpowiada za poszczególne działania?

Dopiero potem wybieramy klasy, moduły, bazy danych i frameworki.

### Domena inteligentnego budynku

Pojęcia:

- Budynek,
- Pomieszczenie,
- Sensor,
- Urządzenie,
- Użytkownik,
- Alarm.

Zdarzenia:

- Pomieszczenie zajęte,
- Temperatura przekroczona,
- Wykryto ruch,
- Alarm uruchomiony.

---

## 7. Granice odpowiedzialności

```text
Building Service
  - budynki
  - pomieszczenia
  - przeznaczenie i pojemność

Device Service
  - urządzenia
  - sensory
  - bieżące odczyty

Automation Service
  - reguły
  - scenariusze
  - polecenia sterujące
```

Dobra granica oznacza, że usługa:

- ma spójną odpowiedzialność,
- nie wymaga ciągłego dostępu do danych innych usług,
- może być rozwijana względnie niezależnie.

Podejrzany podział:

```text
RoomTableService
SensorTableService
AlertTableService
```

Taki podział może być tylko rozdzieleniem tabel, a nie sensownym podziałem domeny.

---

## 8. Kontrakt API

Przykład API `Building Service`:

```http
GET /rooms
GET /rooms/{id}
POST /rooms
```

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

Kontrakt powinien być prosty, jednoznaczny, udokumentowany i możliwie stabilny.

---

## 9. Zadanie na laboratorium

1. Przeanalizujcie domenę inteligentnego budynku.
2. Wypiszcie główne pojęcia, zdarzenia i polecenia.
3. Zaproponujcie 2–4 mikroserwisy.
4. Wybierzcie jedną usługę do implementacji.
5. Zdefiniujcie jej API.
6. Uruchomcie prostą usługę z co najmniej dwoma endpointami.

Na koniec powinna działać przynajmniej jedna usługa z odpowiedziami JSON.

---

## 10. Podsumowanie

- Monolit jest prosty na początku, ale może być trudniejszy w rozwoju.
- Mikrousługa ma jasno określoną odpowiedzialność i własny interfejs.
- DDD pomaga wyznaczać granice usług na podstawie domeny biznesowej.
- Mikrousługi przynoszą korzyści, ale zwiększają złożoność systemu.
- Dobry projekt zaczyna się od problemu, a nie od wyboru frameworka.

