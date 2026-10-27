# Plan realizacji LAB5 — komunikacja asynchroniczna z wykorzystaniem RabbitMQ

Aktualny zakres zadań, kryteria oceny oraz instrukcję krok po kroku dla studentów określa [instrukcja LAB5](README.md). Konfiguracja brokera RabbitMQ, adapter AMQP, przykładowe usługi oraz testy znajdują się w [pakiecie pomocniczym](lab5-support.zip).

## 1. Zgodność z sylabusem i ciągłość projektu

Laboratorium realizuje piąty temat ćwiczeń laboratoryjnych z sylabusa: **„Komunikacja pomiędzy mikrousługami — wykorzystanie brokera wiadomości RabbitMQ”** oraz rozwija zagadnienia wykładowe:

- komunikacja synchroniczna i asynchroniczna, kolejki i brokery wiadomości,
- przepływ pracy (orkiestracja i choreografia, rola transakcji bazodanowych, wzorzec Saga),
- prawo Postela oraz idempotentność konsumenta przy dostarczaniu *at-least-once*.

Ćwiczenie rozwija ten sam projekt studencki z LAB1–LAB4:

```text
LAB1 — pierwsza mikrousługa, kontrakt REST, walidacja (422) i reguła biznesowa (409)
  ↓
LAB2 — trwała baza danych SQLite (SQLAlchemy) oraz cache-aside w Redis (X-Cache, TTL, unieważnianie)
  ↓
LAB3 — druga mikrousługa, rejestracja w Eureka Server i wywołanie synchroniczne po nazwie logicznej
  ↓
LAB4 — wspólny punkt wejścia API Gateway kierujący ruch klienta przez nazwy z Eureki do obu usług
  ↓
LAB5 — asynchroniczna publikacja i idempotentna konsumpcja zdarzeń domenowych przez RabbitMQ
```

## 2. Cele dydaktyczne i efekty kształcenia

Po wykonaniu laboratorium student potrafi:

- odróżnić synchroniczne żądanie HTTP od asynchronicznej publikacji zdarzenia domenowego,
- skonfigurować wymiennik (`Exchange`), powiązanie (`Binding`), klucz routingu (`Routing Key`) i trwałą kolejkę (`Queue`) w RabbitMQ,
- powiązać moment publikacji zdarzenia z zatwierdzeniem transakcji w bazie danych (LAB2) i walidacją reguły biznesowej (LAB1),
- odebrać wiadomość z użyciem `auto_ack=False` i jawnego `basic_ack`, zaktualizować stan w bazie danych i unieważnić klucz w cache Redis (LAB2),
- zapewnić idempotentność konsumenta po identyfikatorze `event_id`,
- wykazać eksperymentalnie buforowanie wiadomości w kolejce przy zatrzymanym konsumencie.

| Efekt | Realizacja na LAB5 | Dowód wykonania |
|---|---|---|
| EK_04 | Skomunikowanie usług za pomocą brokera wiadomości RabbitMQ w układzie z API Gateway i Eureką | Działający przepływ zdarzeniowy między dwiema usługami projektu, diagram i kontrakt zdarzenia |
| EK_03 | Implementacja producenta i konsumenta AMQP (`pika`) na podstawie oficjalnej dokumentacji | Kod obsługi `publish`/`consume`, cztery testy automatyczne i opis dwóch źródeł dokumentacji |
| EK_01 | Rozróżnienie komunikacji synchronicznej i asynchronicznej, choreografii i orkiestracji (Saga) oraz idempotentności | Poprawne wyjaśnienie przepływu i odpowiedzi podczas odbioru |
| EK_02 | Użycie RabbitMQ Server i Management UI, biblioteki `pika`, FastAPI, SQLite, Redis, Eureki i Gatewaya | Odtwarzalna instrukcja uruchomienia i weryfikacji |
| EK_05 | Analiza zachowania przy wyłączonym konsumencie, duplikacie wiadomości i awarii brokera | Udokumentowane wyniki eksperymentów awarii i wnioski |

## 3. Przygotowanie przed zajęciami

Przed rozpoczęciem zajęć należy:

1. Pobrać obraz `rabbitmq:3.13-management-alpine` poleceniem `docker compose up -d rabbitmq` w katalogu `lab5-support`.
2. Zweryfikować dostępność panelu `http://127.0.0.1:15672/` (`guest` / `guest`) oraz portu AMQP `5672`.
3. Utworzyć środowisko wirtualne w `lab5-support`, zainstalować `requirements.txt` i uruchomić `pytest -q` (`5 passed`).
4. Sprawdzić współpracę demo `LOCKER-SERVICE` i `PARCEL-SERVICE` z serwerem Eureka z `lab3-support` oraz bramką z `lab4-support`.

## 4. Organizacja 120 minut zajęć

| Czas | Etap | Działanie i oczekiwany rezultat |
|---:|---|---|
| 15 min | Pojęcia | Model AMQP (Exchange, Routing Key, Queue, ACK), porównanie z HTTP z LAB3, wzorzec Saga (choreografia vs orkiestracja) i idempotentność |
| 20 min | Przykład wspólny | Uruchomienie RabbitMQ i usług z `lab5-support`, obserwacja oczekującej wiadomości w panelu `15672` i jej konsumpcji z `ACK` |
| 15 min | Projekt zdarzenia | Wybór zdarzenia domenowego we własnym projekcie, określenie producenta, konsumenta, klucza routingu i wpływu na SQLite/Redis |
| 35 min | Implementacja | Włączenie `messaging.py` do obu usług własnego projektu, publikacja po zapisie i idempotentna konsumpcja z unieważnieniem cache |
| 25 min | Weryfikacja i awarie | Przepływ przez API Gateway (`:8080`), eksperyment z zatrzymanym konsumentem, duplikatem `event_id` i zatrzymanym brokerem |
| 10 min | Odbiór | Prezentacja działającego przepływu w panelu RabbitMQ i rozmowa techniczna |

## 5. Wymagania odbioru i kryteria zaliczenia

- Zachowane są mechanizmy z LAB1–LAB4 (baza SQLite, cache Redis, Eureka, API Gateway oraz dotychczasowe testy).
- Jedna usługa publikuje trwałe zdarzenie domenowe JSON z `event_id` po pomyślnym zapisie, a odrzucona operacja (`404`/`409`/`422`) nie publikuje zdarzenia.
- Druga usługa konsumuje wiadomość z trwałej kolejki z użyciem `basic_ack`, aktualizuje swój stan i unieważnia odpowiedni wpis w cache Redis.
- Konsument jest idempotentny względem powtórzonego `event_id`.
- Udokumentowano eksperyment buforowania wiadomości przy wyłączonym konsumencie oraz awarii brokera.
- Przechodzą co najmniej cztery własne testy automatyczne dla komunikacji asynchronicznej.
