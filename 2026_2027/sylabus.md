# Sylabus

## Przedmiot

**Nazwa:** Projektowanie aplikacji webowych opartych o mikrousługi  
**Rok akademicki:** 2026/2027  
**Kierunek:** Informatyka, studia II stopnia  
**Forma:** wykład i laboratorium  
**Wymiar:** 15 godzin wykładu, 30 godzin laboratorium  
**Zaliczenie:** zaliczenie z oceną

## Wymagania wstępne

- znajomość podstaw aplikacji internetowych,
- znajomość co najmniej jednej technologii tworzenia aplikacji webowych,
- podstawowa znajomość HTTP, REST i baz danych.

## Cele przedmiotu

1. Poznanie pojęć, cech i zalet architektury mikroserwisowej.
2. Nabycie umiejętności modelowania mikroserwisów z wykorzystaniem DDD.
3. Poznanie sposobów migracji monolitu do architektury mikroserwisowej.
4. Poznanie wzorców komunikacji, orkiestracji, choreografii i Saga.
5. Poznanie roli CI/CD, konteneryzacji i podstaw Kubernetes.

## Główne zagadnienia wykładowe

- monolit i mikrousługi,
- niezależne wdrażanie, skalowanie i monitorowanie,
- spójność i sprzężenie,
- Domain-Driven Design i Event Storming,
- kontrakty API i wersjonowanie,
- komunikacja synchroniczna i asynchroniczna,
- RabbitMQ i brokery wiadomości,
- Saga, orkiestracja i choreografia,
- API Gateway i BFF,
- Docker i podstawy Kubernetes,
- CI/CD oraz wzorce Monorepo, Multirepo i Strangler.

## Główne zagadnienia laboratoryjne

1. Utworzenie podstawowej mikrousługi i zaprojektowanie API.
2. Persystencja danych i cachowanie.
3. Rejestracja usług z użyciem Eureka.
4. Konfiguracja API Gateway.
5. Komunikacja przez RabbitMQ.
6. Konteneryzacja usług przy użyciu Docker.

## Zaliczenie

### Wykład

Test wiedzy (kolokwium testowe z wykładu, efekty EK_01, EK_02, EK_05). Warunkiem zaliczenia jest uzyskanie minimum 50% punktów.

### Laboratorium

Warunkiem zaliczenia laboratorium jest **zaliczenie kolokwium oraz projektu**.

- **Kolokwium:** sprawdza wiedzę i umiejętności objęte zajęciami laboratoryjnymi (zgodnie z sylabusem weryfikuje efekty EK_03 i EK_04). Jego zaliczenie jest warunkiem koniecznym uzyskania oceny pozytywnej.
- **Projekt:** rozwijany etapami. Każda osoba musi zaimplementować co najmniej dwie różne mikrousługi oraz pozostałe wymagane komponenty systemu.
  Ocena projektu obejmuje:
  - **jakość i kompletność kodu — 60%,**
  - **jakość dokumentacji — 40%.**
