# Pytania otwarte na zaliczenie laboratoriów

**Przedmiot:** Projektowanie aplikacji webowych opartych o mikrousługi  
**Zakres:** LAB1–LAB6  


Zaliczenie sprawdza rozumienie granic odpowiedzialności usług, przepływu żądań i zdarzeń, zarządzania danymi oraz zachowania systemu podczas awarii. Odpowiedzi można przedstawiać na przykładzie własnego projektu lub systemu paczkomatów.

Gwiazdka **★** oznacza 10 pytań podstawowych tworzących krótszy zestaw: **1, 2, 3, 5, 7, 9, 11, 14, 17 i 18**.

## Pytania i wskazówki do oceny

Odpowiedzi przedstawiają przykładowe poprawne rozumowanie. Nie wymagają odtworzenia słowo w słowo. Przykłady z innej domeny są równoważne, jeżeli zachowują sens mechanizmu. Szczegóły oznaczone jako rozszerzenie służą pogłębieniu rozmowy; nie stanowią dodatkowych warunków zaliczenia laboratoriów.

### 1. ★ Czym różni się mikrousługa od modułu aplikacji? Wyjaśnij na przykładzie, co zmienia wydzielenie fragmentu systemu do osobnej usługi.

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**W poprawnej odpowiedzi:** osobny proces, komunikacja przez sieć, możliwość niezależnego wdrażania i spójna odpowiedzialność biznesowa. Należy dostrzec także koszt: opóźnienia, awarie połączeń i trudniejszą integrację. Sam osobny folder lub port nie wystarcza.

**Odpowiedź wzorcowa:**

Moduł jest częścią kodu aplikacji i zwykle działa w tym samym procesie co pozostałe moduły. Można wywołać jego funkcję bez komunikacji sieciowej, a wdrożenie obejmuje całą aplikację. W modularnym monolicie granice modułów mogą być bardzo wyraźne, mimo wspólnego uruchamiania.

Mikrousługa jest osobno uruchamianą aplikacją o spójnej odpowiedzialności biznesowej i określonym interfejsie. Można ją wdrażać i restartować niezależnie. Po wydzieleniu obsługi skrytek do Locker Service inne usługi korzystają z jej API lub komunikatów, zamiast wywoływać wewnętrzną funkcję. Zyskuje się możliwość niezależnego rozwoju i skalowania, ale trzeba obsłużyć opóźnienia, niedostępność i częściowe awarie. Awaria jednej usługi może nadal wpływać na zależne operacje. Dla małego systemu modularny monolit może być wystarczający.

**Na co zwracać uwagę:** rozróżnienie granicy kodu, procesu i wdrożenia; powiązanie podziału z biznesem; przynajmniej jedna korzyść i jeden koszt.

**Błędy świadczące o niezrozumieniu:** „każdy folder to mikrousługa”, „mikrousługa musi działać na osobnym komputerze”, „mikrousługi zawsze są lepsze” lub „awaria nigdy nie przenosi się na inne usługi”.

</details>

### 2. ★ Za co odpowiada każda usługa w Twoim projekcie? Jakie dane przechowuje i dlaczego tak podzielono zadania?

<details markdown="block">
<summary>Przykładowa odpowiedź i ocena</summary>

**Przykładowa odpowiedź:**

W przykładzie paczkomatów jedna usługa zajmuje się skrytkami: wie, gdzie są i czy są wolne, zarezerwowane lub zajęte. Druga zajmuje się paczkami: przechowuje ich numery i informacje o przesyłkach. Każda ma więc inne zadanie.

Jeśli usługa paczek chce zarezerwować skrytkę, prosi o to usługę skrytek przez API. Nie zmienia samodzielnie jej tabel w bazie. To usługa skrytek sprawdza, czy skrytka jest wolna, i zapisuje zmianę. Dzięki temu sprawdzanie poprawności rezerwacji jest w jednym miejscu.

**Sprawdź:** czy student potrafi powiedzieć „ta usługa robi to, przechowuje te dane, a tego już nie robi” i wyjaśnić ten podział na swoim projekcie.

**Błędne rozumienie:** „Każda usługa może dowolnie zmieniać dane pozostałych, bo tak jest wygodniej”.

</details>

### 3. ★ Wyjaśnij różnicę między niepoprawnymi danymi wejściowymi, brakiem zasobu i naruszeniem reguły biznesowej. Podaj przykłady z własnego API.

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

To trzy różne powody odrzucenia żądania. Na przykładzie skrytki:

- **Niepoprawne dane — „nie rozumiem podanej wartości”.** Aplikacja przyjmuje tylko określone statusy, np. `free` (wolna), `reserved` (zarezerwowana) i `occupied` (zajęta). Jeśli wyślę status `xyz`, podaję wartość spoza dozwolonej listy. W przykładzie z FastAPI otrzymam `422`.
- **Brak zasobu — „nie ma takiej skrytki”.** Proszę o zmianę skrytki o numerze, którego nie zapisano w systemie. Otrzymam `404`.
- **Naruszenie reguły biznesowej — „ta skrytka istnieje, ale nie wolno teraz wykonać takiej zmiany”.** Statusy `free` i `occupied` są poprawnymi wartościami, ale w ćwiczeniu nie można zmienić wolnej skrytki od razu na zajętą. Najpierw trzeba ją zarezerwować: `free → reserved → occupied`. Próba pominięcia rezerwacji kończy się `409`.

We wszystkich trzech sytuacjach operacja zostaje odrzucona. Dane powinny pozostać bez zmian. Aplikacja nie powinna też wysłać wiadomości, że operacja się udała. Te sprawdzenia muszą działać po stronie usługi, nawet jeśli formularz również sprawdza dane.

**Na co zwracać uwagę:** czy student potrafi odróżnić „podano złą wartość”, „nie ma takiego obiektu” i „obiekt jest, ale ta zmiana jest zabroniona”. Powinien podać przykład każdej sytuacji i wiedzieć, że odrzucone żądanie nie może zmienić stanu. Ważniejsze jest rozumienie tej różnicy niż samo wyliczenie kodów HTTP.

**Błędy świadczące o niezrozumieniu:** uznanie, że każda znana wartość statusu może być ustawiona w dowolnej chwili; sprawdzanie danych tylko w formularzu; zapisanie zmiany mimo odrzucenia żądania; traktowanie każdego błędu jako awarii serwera (`500`).

</details>

### 4. Co zmienia przeniesienie danych ze słownika w pamięci do bazy danych? Co powinno pozostać takie samo dla klienta API?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Gdy przechowuję dane w słowniku Pythona, są one tylko w pamięci działającego programu. Mogę dodać paczkomat i odczytać go w następnym żądaniu, ale po wyłączeniu i ponownym uruchomieniu aplikacji ten dodany paczkomat zniknie.

Po przeniesieniu danych do SQLite aplikacja zapisuje je w pliku bazy. Po ponownym uruchomieniu może odczytać wcześniej dodany paczkomat, o ile korzysta z tego samego, zachowanego pliku. W środowisku Docker ten plik trzeba dodatkowo umieścić na trwałym wolumenie, jeśli dane mają przetrwać usunięcie kontenera.

Dla klienta API sposób korzystania z usługi powinien pozostać taki sam. Na przykład nadal wysyła `POST /lockers`, żeby dodać paczkomat, i `GET /lockers/{id}`, żeby go odczytać. Nie musi wiedzieć, czy aplikacja korzysta ze słownika, czy z bazy. Powinien otrzymywać taką samą strukturę JSON i takie samo znaczenie odpowiedzi. Nadal obowiązują też te same zasady, np. zakaz niedozwolonej zmiany statusu skrytki.

W kodzie aplikacji zmienia się sposób odczytu i zapisu. Trzeba też obsłużyć sytuację, gdy zapis do bazy się nie powiedzie. Powiązane zmiany można wykonać w transakcji: zatwierdzić je razem (`commit`) albo wycofać, jeśli nie zostały jeszcze zatwierdzone (`rollback`). Nie należy potwierdzać klientowi udanego zapisu, który się nie powiódł.

**Na co zwracać uwagę:** czy student potrafi wyjaśnić dwie rzeczy: „baza pozwala zachować dane po restarcie” oraz „klient nadal korzysta z tego samego API”. Dobrym sprawdzeniem jest przykład: dodaj rekord, uruchom aplikację ponownie i spróbuj odczytać ten sam rekord. Student powinien też wiedzieć, że błąd zapisu wymaga obsługi.

**Błędy świadczące o niezrozumieniu:** „Słownik zachowa dodane dane po restarcie”, „Każdy restart aplikacji usuwa plik SQLite”, „Po zmianie słownika na bazę klient musi wysyłać inne żądania” albo „Można zwrócić sukces, mimo że zapis do bazy się nie udał”.

</details>

### 5. ★ Opowiedz krok po kroku, jak działa odczyt z cache oraz co powinno się wydarzyć po zmianie danych w bazie.

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Cache to dodatkowe miejsce na kopie często odczytywanych danych. W naszym projekcie tę rolę pełni Redis. Dzięki temu aplikacja nie musi za każdym razem pobierać tego samego rekordu z bazy.

Przykład: klient pyta o paczkomat `KRK-1024`.

1. Aplikacja szuka jego danych w Redis.
2. Jeśli kopia tam jest, zwraca ją klientowi. To **HIT**, czyli trafienie w cache.
3. Jeśli kopii nie ma, odczytuje dane z bazy, zapisuje kopię w Redis i zwraca wynik. To **MISS**, czyli brak wpisu w cache.
4. Kopia otrzymuje **TTL**, czyli czas, po którym wpis wygaśnie.

Jeśli zmieniam nazwę paczkomatu, najpierw zatwierdzam nową nazwę w bazie, a potem usuwam starą kopię z Redis. Następny odczyt pobierze nową nazwę z bazy i ponownie utworzy kopię. Jeżeli zmiana została odrzucona, nie należy zapisywać jej w bazie ani w cache.

Gdy opcjonalny cache jest niedostępny, aplikacja powinna móc skorzystać z bazy. Cache można odtworzyć z danych w bazie; nie powinien być jedynym miejscem ich zapisu.

**Na co zwracać uwagę:** Czy student umie prześledzić pierwszy odczyt, drugi odczyt i odczyt po zmianie nazwy. Powinien wiedzieć, po co usuwa się starą kopię. Samo podanie nazw HIT, MISS i TTL nie wystarcza.

**Błędy świadczące o niezrozumieniu:** „Brak wpisu w Redis oznacza brak paczkomatu”, „Wystarczy zmienić sam cache” albo „TTL sprawia, że kopia zawsze jest aktualna”.

</details>

### 6. Zmiana została zapisana w bazie, ale nie udało się usunąć starego wpisu z Redis. Jakie skutki może zobaczyć użytkownik?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Załóżmy, że paczkomat nazywał się „Dworzec”, a użytkownik zmienił nazwę na „Dworzec Główny”. Nowa nazwa jest już zapisana w bazie. Usunięcie starej kopii z Redis jednak się nie udało.

Jeśli aplikacja odczyta tę starą kopię, użytkownik zobaczy „Dworzec”, mimo że dostał wcześniej potwierdzenie zmiany. Nie oznacza to utraty zapisu: baza ma nową nazwę, ale odczyt korzysta ze starej kopii.

Gdy Redis nie odpowiada, aplikacja może odczytywać dane z bazy. Po powrocie Redis problem może pojawić się ponownie, jeśli stary wpis nadal istnieje. Usunięcie wpisu lub upływ jego TTL pozwoli pobrać nową wartość. TTL ogranicza czas życia tej kopii, ale nie daje natychmiastowej aktualności.

Znaczenie takiego opóźnienia zależy od danych. Stara nazwa paczkomatu może być małym problemem. Przy przydzielaniu ostatniej wolnej skrytki trzeba sprawdzić aktualny stan po stronie usługi, która nią zarządza, i zabezpieczyć zapis przed podwójną rezerwacją.

**Na co zwracać uwagę:** Czy student potrafi powiedzieć: „zapis się udał, ale odczyt może pokazać stare dane”. Powinien też rozumieć, dlaczego problem może pozostać po powrocie Redis.

**Błędy świadczące o niezrozumieniu:** „Błąd Redis automatycznie cofa zapis w bazie” albo „Po powrocie Redis wszystkie wpisy same stają się aktualne”.

</details>

### 7. ★ Po co w systemie jest Eureka? Wyjaśnij, jak jedna usługa odnajduje drugą i kto wykonuje właściwe żądanie biznesowe.

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Eureka przechowuje informacje, pod jakimi adresami działają usługi. Na przykład usługa skrytek zgłasza: „Nazywam się `LOCKER-SERVICE`, działam pod tym adresem i na tym porcie”. Co pewien czas odnawia zgłoszenie. To okresowe potwierdzenie nazywa się **heartbeat**.

Usługa paczek potrzebuje informacji o skrytce. Zamiast mieć adres usługi skrytek wpisany na stałe w kodzie, korzysta z informacji pobranych z Eureki. Wyszukuje nazwę `LOCKER-SERVICE`, wybiera adres działającej instancji i wysyła do niej żądanie HTTP.

Właściwe pytanie o skrytkę trafia bezpośrednio do usługi skrytek. Eureka jedynie pomaga znaleźć jej adres. Nie przechowuje danych skrytek ani nie wykonuje rezerwacji. Klient przechowuje i okresowo odświeża kopię rejestru, więc nie musi pytać Eureki przed każdym żądaniem.

Dwie uruchomione kopie `LOCKER-SERVICE` to dwie instancje tej samej usługi. Obie realizują ten sam rodzaj zadania.

**Na co zwracać uwagę:** Czy student odróżnia znalezienie adresu od wykonania operacji. Powinien umieć wskazać, kto zgłasza adres, kto go odczytuje i kto odpowiada na pytanie o skrytkę.

**Błędy świadczące o niezrozumieniu:** „Pytania o skrytki przechodzą przez Eurekę”, „Eureka rezerwuje skrytkę” albo „Dwie kopie jednej usługi to dwie różne usługi biznesowe”.

</details>

### 8. Usługa widnieje w Eurece jako `UP`, ale wywołanie do niej się nie udaje. Jak to wyjaśnisz i co sprawdzisz?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Status `UP` nie oznacza, że każda funkcja usługi na pewno działa. Informacja może być opóźniona: proces właśnie się wyłączył, a rejestr lub jego kopia u klienta jeszcze tego nie uwzględniły. Usługa mogła też zgłosić błędny adres lub port. Może działać sam program, ale nie działać jego baza.

Sprawdziłbym kolejno:

1. Czy proces usługi nadal działa i co pokazują jego logi.
2. Na jakim adresie i porcie rzeczywiście przyjmuje połączenia.
3. Czy taki sam adres i port widnieją w Eurece.
4. Czy druga usługa może dotrzeć pod ten adres ze swojego środowiska.
5. Czy wysyła żądanie na właściwą ścieżkę.

Żądanie powinno mieć limit czasu oczekiwania, czyli **timeout**. Gdy zależna usługa nie odpowiada, aplikacja powinna zwrócić kontrolowany błąd, a nie czekać bez końca. Odpowiedź `404` o nieistniejącym paczkomacie to inna sytuacja: usługa odpowiedziała, tylko nie znalazła obiektu.

**Na co zwracać uwagę:** Czy student proponuje konkretne sprawdzenia i rozróżnia brak połączenia od poprawnie zwróconej informacji o braku danych.

**Błędy świadczące o niezrozumieniu:** „Skoro jest `UP`, to usługa na pewno działa poprawnie” albo „Każde `404` oznacza awarię usługi”.

</details>

### 9. ★ Czym różni się rola API Gateway od roli Eureki i mikrousługi domenowej? Prześledź przykładowe żądanie klienta.

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Każdy z tych elementów ma inne zadanie:

- **API Gateway, czyli bramka,** przyjmuje żądanie klienta i przekazuje je do odpowiedniej usługi.
- **Eureka** dostarcza informacje o adresach uruchomionych usług.
- **Usługa domenowa**, np. usługa skrytek, wykonuje właściwą pracę: sprawdza zasady, odczytuje dane i zapisuje zmiany.

Przykład: klient wysyła do bramki `GET /api/lockers/KRK-1024`. Bramka rozpoznaje, że chodzi o usługę skrytek, usuwa prefiks `/api` i wybiera jej adres na podstawie informacji z Eureki. Przekazuje `GET /lockers/KRK-1024`. Usługa odczytuje dane ze swojego cache lub bazy. Wynik wraca przez bramkę do klienta.

To usługa skrytek decyduje, czy wolno zarezerwować skrytkę. Bramka nie powinna w tym celu samodzielnie zmieniać jej tabel. W naszym układzie usługi komunikują się także bezpośrednio ze sobą; nie muszą zawracać każdego wewnętrznego żądania przez bramkę.

**Na co zwracać uwagę:** Czy student umie opowiedzieć drogę żądania i nie miesza trzech ról: przekazania żądania, znalezienia adresu i wykonania operacji.

**Błędy świadczące o niezrozumieniu:** „Eureka działa jak bramka” albo „Bramka powinna przechowywać wszystkie dane i wykonywać zasady rezerwacji”.

</details>

### 10. Klient wywołuje `/api/lockers/KRK-1024`, a bramka usuwa pierwszy segment ścieżki. Jakie żądanie otrzyma usługa i jak odróżnisz brak trasy od braku paczkomatu?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Po usunięciu pierwszego segmentu ścieżki usługa otrzyma `/lockers/KRK-1024`. W konfiguracji robi to filtr `StripPrefix=1`. Sama ta zmiana nie zmienia metody HTTP ani przesłanego JSON.

Odpowiedź `404` może mieć różne przyczyny:

- Bramka nie zna trasy pasującej do żądania. Nie przekazuje go do usługi.
- Bramka przekazała żądanie, ale pod błędną ścieżką. Usługa nie ma takiego endpointu.
- Żądanie trafiło do właściwego endpointu, ale paczkomatu `KRK-1024` nie ma w danych.

Żeby ustalić przyczynę, sprawdzę trasę w bramce i ścieżkę po usunięciu prefiksu. Z logów spróbuję ustalić, czy żądanie dotarło do usługi. Jeśli mogę wywołać usługę bezpośrednio z jej sieci, porównam wynik. Sam numer `404` nie mówi jeszcze, który z tych przypadków wystąpił.

**Na co zwracać uwagę:** Czy student podaje poprawną ścieżkę po zmianie i odróżnia „nie ma trasy”, „nie ma endpointu” oraz „nie ma rekordu”.

**Błędy świadczące o niezrozumieniu:** „Każde `404` oznacza brak rekordu w bazie” albo „Usunięcie prefiksu zmienia także GET na inną metodę”.

</details>

### 11. ★ Kiedy wybrać bezpośrednie wywołanie HTTP, a kiedy zdarzenie przesyłane przez RabbitMQ? Porównaj zachowanie obu rozwiązań przy wyłączonym odbiorcy.

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

**HTTP wybieram, gdy potrzebuję odpowiedzi do wykonania bieżącej operacji.** Na przykład usługa paczek pyta usługę skrytek o paczkomat i czeka na wynik. Gdy odbiorca nie działa, połączenie się nie uda albo minie czas oczekiwania. Trzeba wtedy zwrócić odpowiedni błąd lub zastosować wcześniej zaplanowaną obsługę tej sytuacji.

**Wiadomość wybieram, gdy odbiorca może zareagować później.** Po utworzeniu paczki wysyłam zdarzenie „paczka została utworzona”. Usługa historii może je odebrać i uzupełnić historię za chwilę. Jeżeli jest wyłączona, wiadomość może poczekać w poprawnie skonfigurowanej kolejce działającego RabbitMQ.

Samo opublikowanie wiadomości nie oznacza, że odbiorca już ją przetworzył. Nadal trzeba obsłużyć awarię brokera. Jeżeli producent przed wysłaniem wiadomości musi wykonać HTTP do wyłączonej usługi, jego operacja może zatrzymać się jeszcze wcześniej. Kolejka nie usuwa tej wcześniejszej zależności.

**Na co zwracać uwagę:** Czy student potrafi uzasadnić wybór: „potrzebuję wyniku teraz” albo „odbiorca może zareagować później”. Powinien odróżniać wyłączenie odbiorcy od wyłączenia brokera.

**Błędy świadczące o niezrozumieniu:** „Wysłanie wiadomości oznacza zakończenie pracy odbiorcy” albo „Przy RabbitMQ żadna awaria już nie przeszkadza”.

</details>

### 12. Opowiedz, jak wiadomość trafia od producenta do konsumenta w RabbitMQ. Jaką rolę pełnią exchange, routing key, binding i kolejka?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Wiadomość przechodzi drogę: **producent → exchange → kolejka → konsument**.

- **Producent** to aplikacja wysyłająca wiadomość.
- **Exchange** to element RabbitMQ, który kieruje wiadomości do kolejek.
- **Routing key** to oznaczenie wiadomości, np. `parcel.created`.
- **Binding** to powiązanie exchange z kolejką. Określa, jakie wiadomości mają do niej trafić, zgodnie z typem exchange.
- **Kolejka** przechowuje wiadomości oczekujące na obsługę.
- **Konsument** odbiera je z kolejki i wykonuje pracę.

Na przykład zdarzenie o utworzeniu paczki może trafić do kolejki historii i do osobnej kolejki powiadomień. Dzięki temu obie usługi dostaną własną kopię.

Jeżeli natomiast uruchomię dwa procesy odbierające z jednej kolejki, będą dzielić jej pracę. Nie należy zakładać, że każdy dostanie wszystkie wiadomości. Nie należy też zakładać, że samo wysłanie do exchange wystarczy: bez odpowiedniego powiązania wiadomość może nie trafić do żadnej kolejki.

**Na co zwracać uwagę:** Czy student rozumie drogę wiadomości i umie wyjaśnić, po co są oznaczenie oraz powiązanie. Ważna jest różnica między dwiema kolejkami a dwoma odbiorcami jednej kolejki.

**Błędy świadczące o niezrozumieniu:** „Exchange przechowuje wiadomości zamiast kolejki” albo „Każdy odbiorca jednej kolejki zawsze dostaje każdą wiadomość”.

</details>

### 13. Co oznacza, że system jest spójny ostatecznie? Opisz sytuację, w której dwie usługi przez chwilę pokazują różny stan.

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Załóżmy, że usługa paczek zapisała nową przesyłkę i wysłała o tym wiadomość. Usługa historii jeszcze jej nie odebrała. Przez chwilę paczka już istnieje, ale jej historia jest pusta.

Kiedy usługa historii odbierze i poprawnie przetworzy wiadomość, doda wpis. Informacje będą wtedy zgodne. **Spójność ostateczna** oznacza właśnie, że zgodny stan jest osiągany po pewnym czasie, zamiast natychmiast we wszystkich usługach.

Użytkownik może w tym czasie widzieć np. „historia oczekuje na uzupełnienie”. Nie ma jednak automatycznej gwarancji, że potrwa to jedną sekundę. Przy zatrzymanym odbiorcy opóźnienie będzie większe. Jeżeli wiadomość zginie albo odbiorca stale zgłasza błąd, samo czekanie nie wystarczy. Potrzebne jest skuteczne dostarczenie i przetworzenie zmiany.

Dlatego do decyzji o zajęciu ostatniej skrytki nie wystarczy opóźniona kopia informacji o jej dostępności.

**Na co zwracać uwagę:** Czy student potrafi wskazać, dlaczego przez chwilę widać różne dane, co wyrówna ten stan i jaki skutek opóźnienie ma dla użytkownika.

**Błędy świadczące o niezrozumieniu:** „Wszystkie usługi aktualizują dane jednocześnie” albo „Nawet utracona wiadomość nie ma znaczenia, bo dane kiedyś same się wyrównają”.

</details>

### 14. ★ Konsument zapisał zmianę w bazie, ale przestał działać przed wysłaniem ACK. Co może się wydarzyć po jego ponownym uruchomieniu i jak uniknąć podwójnego skutku?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

**ACK to potwierdzenie dla brokera: „ta wiadomość została obsłużona”.** Jeśli odbiorca zapisze wynik, ale wyłączy się przed potwierdzeniem, broker może dostarczyć wiadomość ponownie. Bez zabezpieczenia ten sam wpis historii mógłby powstać drugi raz.

Dlatego każda wiadomość ma identyfikator, np. `event_id`. Odbiorca sprawdza, czy już go obsłużył:

1. Jeśli nie, wykonuje zmianę i zapisuje identyfikator jako przetworzony.
2. Jeśli tak, nie powtarza zmiany.
3. Po poprawnej obsłudze wysyła ACK, także dla rozpoznanego duplikatu.

Wynik operacji i informację o przetworzeniu trzeba zapisać w jednej transakcji: oba zapisy mają się zatwierdzić razem albo wcale. Identyfikatory powinny przetrwać restart, a zabezpieczenie powinno działać także przy równoległym odbiorze.

Takie zachowanie nazywa się **idempotentnością**: ponowne obsłużenie tego samego zdarzenia nie daje dodatkowego skutku. Wysłanie ACK przed wykonaniem pracy jest ryzykowne — po awarii broker może już nie powtórzyć niewykonanej operacji.

**Na co zwracać uwagę:** Czy student rozumie, dlaczego wiadomość może wrócić, i umie zapobiec podwójnemu skutkowi. Ważne jest trwałe zapisanie identyfikatora razem ze zmianą, a nie tylko zapamiętanie go w zmiennej.

**Błędy świadczące o niezrozumieniu:** „ACK sprawia, że wiadomość zawsze jest wykonana dokładnie raz”, „Broker nigdy nie powtarza dostawy” albo „Zapis identyfikatora można bezpiecznie odłożyć na później”.

</details>

### 15. Usługa zatwierdziła zmianę w bazie, ale uległa awarii przed publikacją zdarzenia. Jaki problem powstaje? Czy zwrócenie błędu klientowi cofa zapis?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Może powstać sytuacja: **paczka jest już w bazie, ale usługa historii nie dostała informacji o jej utworzeniu**. Zapis w bazie i wysłanie wiadomości to dwie osobne czynności. Awaria między nimi pozostawia wykonaną tylko pierwszą.

Zwrócenie klientowi błędu, np. `503`, nie usuwa paczki z bazy, jeśli zapis został już zatwierdzony. Nie można uznać, że „skoro odpowiedź była błędna, nic się nie zmieniło”. Ponowienie operacji przez klienta też wymaga uwagi, żeby nie utworzyć drugiej paczki.

Rozwiązaniem rozszerzającym jest **Transactional Outbox**. Razem z paczką zapisuję w tej samej transakcji wpis: „trzeba wysłać zdarzenie o tej paczce”. Osobny mechanizm wysyła takie oczekujące zdarzenia i ponawia próbę po awarii. Zamiar wysłania nie ginie wraz z procesem. Nadal może dojść do ponownej wysyłki, więc odbiorca musi rozpoznawać duplikaty.

**Na co zwracać uwagę:** Podstawą jest zauważenie problemu „zapisane, ale niewysłane” oraz tego, że błąd odpowiedzi nie cofa zatwierdzonego zapisu. Wyjaśnienie Outbox jest pogłębieniem odpowiedzi, nie obowiązkiem implementacji.

**Błędy świadczące o niezrozumieniu:** „Każdy wyjątek cofa wcześniejszy commit”, „Wystarczy wysłać zdarzenie przed sprawdzeniem danych” albo „Outbox usuwa wszystkie duplikaty”.

</details>

### 16. Jak sprawdzisz, że Twój system działa poprawnie także podczas awarii? Co zweryfikujesz testem z atrapą, a co testem integracyjnym?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

**Atrapa** zastępuje prawdziwy komponent w teście i pozwala ustawić jego zachowanie. Mogę kazać atrapie Redis zgłosić błąd i sprawdzić, czy aplikacja odczyta dane z bazy. Mogę też podać dwa razy ten sam `event_id` i sprawdzić, czy historia zmieniła się tylko raz.

Taki test jest szybki i pozwala łatwo odtworzyć awarię. Nie potwierdzi jednak, że prawdziwy Redis ma poprawny adres i hasło.

**Test integracyjny** sprawdza współpracę rzeczywistych elementów. Uruchamiam usługi, bramkę i potrzebną infrastrukturę. Wysyłam żądanie przez bramkę i sprawdzam, czy dane zostały zapisane, wiadomość dotarła, a odbiorca wykonał zmianę. Mogę wyłączyć jeden komponent i zobaczyć, jak zachowają się pozostałe.

W obu przypadkach sprawdzam konkretny wynik. Sam brak wyjątku nie wystarcza. Przy odrzuconej operacji sprawdzam również, że dane się nie zmieniły. Przy wiadomościach dopuszczam czas na ich przetworzenie, ale nie czekam bez końca.

**Na co zwracać uwagę:** Czy student umie podać konkretny test i powiedzieć, co on potwierdzi, a czego nie. Powinien kontrolować stan danych, a nie tylko kod odpowiedzi.

**Błędy świadczące o niezrozumieniu:** „Testy z atrapami dowodzą poprawnej konfiguracji sieci” albo „Wystarczy sprawdzić, że aplikacja się nie wyłączyła”.

</details>

### 17. ★ Czym różni się obraz Dockera od kontenera? Gdzie powinny znajdować się dane, które mają przetrwać usunięcie i ponowne utworzenie kontenera?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

**Obraz Dockera** to przygotowany zestaw plików i ustawień potrzebnych do uruchomienia aplikacji. **Kontener** to konkretna instancja utworzona z tego obrazu. Z jednego obrazu mogę uruchomić kilka kontenerów.

Kontener ma własne miejsce na zapis plików. Plik SQLite zapisany tylko w tym miejscu może przetrwać zatrzymanie i ponowne uruchomienie tego samego kontenera. Zniknie jednak po jego usunięciu.

Jeśli dane mają przetrwać odtworzenie kontenera, katalog z bazą podłączam do **nazwanego wolumenu**. To miejsce przechowywania danych niezależne od konkretnego kontenera. Nowy kontener może podłączyć ten sam wolumen i odczytać plik bazy. Ścieżka bazy musi rzeczywiście wskazywać katalog na tym wolumenie.

W Compose zwykłe `docker compose down` zachowuje nazwane wolumeny. Dodanie `-v` je usuwa. Trwały wolumen nie zastępuje kopii zapasowej.

**Na co zwracać uwagę:** Czy student odróżnia restart kontenera od jego usunięcia i umie wskazać, gdzie faktycznie zapisuje się baza. Powinien znać skutek usunięcia wolumenu.

**Błędy świadczące o niezrozumieniu:** „Każdy zapis zmienia obraz”, „Każdy restart usuwa dane” albo „Wolumen zachowa dane nawet po jego usunięciu”.

</details>

### 18. ★ Dlaczego adres `localhost` działający przed konteneryzacją może przestać działać po przeniesieniu usług do Docker Compose? Jak powinny adresować się kontenery?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

W kontenerze **`localhost` wskazuje ten sam kontener**. Jeśli usługa paczek próbuje połączyć się z `localhost:8761`, szuka Eureki u siebie. Nie trafi w ten sposób do osobnego kontenera Eureki.

W jednej sieci Docker Compose używam nazw usług z konfiguracji i ich portów wewnętrznych. Przykładowo:

- do Eureki: `http://eureka:8761`,
- do Redis: `redis://redis:6379/0`,
- do usługi skrytek: `http://locker-service:8101`.

Przeglądarka na komputerze gospodarza jest w innej sytuacji. Może używać `http://localhost:8080`, jeśli port bramki udostępniono na tym komputerze.

Proces wewnątrz kontenera powinien nasłuchiwać na osiągalnym interfejsie, zwykle `0.0.0.0`. To ustawienie oznacza przyjmowanie połączeń na wszystkich interfejsach IPv4 kontenera; nie jest adresem drugiej usługi. Również adres zgłoszony do Eureki musi być osiągalny dla pozostałych kontenerów.

**Na co zwracać uwagę:** Czy student umie odpowiedzieć „skąd wykonuję połączenie?” i „do czego chcę dotrzeć?”. Powinien rozróżniać adres dla przeglądarki, adres między kontenerami i ustawienie nasłuchu.

**Błędy świadczące o niezrozumieniu:** „`localhost` zawsze wskazuje komputer gospodarza” albo używanie `0.0.0.0` jako adresu innej usługi.

</details>

### 19. Które porty systemu udostępnisz na hoście i dlaczego? Czy mikrousługi muszą publikować porty, aby komunikować się między sobą?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Na komputerze gospodarza zwykle udostępniam port bramki. Klient wysyła do niej żądania, a bramka łączy się z usługami wewnątrz sieci Compose. Każda mikrousługa nie musi więc mieć własnego portu opublikowanego na komputerze. Panele administracyjne mogę udostępnić dodatkowo do lokalnej diagnostyki.

Wpis `127.0.0.1:8080:8080` w sekcji **`ports`** oznacza, że lokalny port 8080 komputera prowadzi do portu 8080 kontenera. Ogólniej po lewej podaję port komputera, a po prawej port kontenera.

**`expose`** opisuje port wewnętrzny i nie tworzy takiego przekierowania na komputer. Nie działa jednak jak zapora. Kontenery w tej samej sieci mogą łączyć się z nasłuchującymi portami także bez wpisu `expose`.

Ograniczenie publikowanych portów zmniejsza liczbę bezpośrednio dostępnych wejść do systemu. Jeśli chcę ograniczyć także połączenia między grupami kontenerów, muszę odpowiednio zaprojektować ich sieci.

**Na co zwracać uwagę:** Czy student odróżnia dostęp z komputera od komunikacji między kontenerami. Powinien rozumieć znaczenie lewej i prawej strony mapowania portu.

**Błędy świadczące o niezrozumieniu:** „Bez `ports` usługi się nie połączą”, „`expose` udostępnia port na komputerze” albo „Brak `expose` blokuje innym kontenerom dostęp”.

</details>

### 20. Kontener bazy lub brokera już działa, ale aplikacja nadal nie może się z nim połączyć. Czym różni się uruchomienie komponentu od jego gotowości do pracy?

<details markdown="block">
<summary>Odpowiedź wzorcowa i wskazówki do oceny</summary>

**Odpowiedź wzorcowa:**

Kontener może już działać, ale aplikacja w środku może nadal się przygotowywać. Na przykład baza uruchomiła proces, lecz jeszcze nie przyjmuje zapytań. Próba połączenia w tej chwili może się nie udać.

**Healthcheck** to okresowe sprawdzenie wybranej funkcji, np. tego, czy baza odpowiada. W Compose mogę ustawić `depends_on` z `condition: service_healthy`, aby usługa wystartowała dopiero po pozytywnym sprawdzeniu jej zależności.

Ważne jest, co sprawdzamy. Samo istnienie procesu daje mniej informacji niż udane zapytanie do bazy. Podobnie prosty `/health` aplikacji może odpowiadać, choć potrzebna jej baza nie działa. Sprawdzenie gotowości powinno odpowiadać na pytanie: „czy można już obsłużyć potrzebne żądanie?”.

Po poprawnym starcie zależność nadal może się zepsuć. Aplikacja musi więc obsługiwać błędy połączeń, ograniczać czas oczekiwania i rozsądnie ponawiać próby. Samo ustawienie kolejności startu nie zapewnia dostępności przez cały czas.

**Na co zwracać uwagę:** Czy student rozumie różnicę między „proces został uruchomiony” a „usługa jest gotowa do pracy”. Powinien też wiedzieć, że późniejsza awaria nadal wymaga obsługi.

**Błędy świadczące o niezrozumieniu:** „Uruchomiony kontener zawsze jest gotowy”, „Każdy healthcheck sprawdza całą aplikację” albo „Samo `depends_on` bez warunku zawsze czeka na gotowość”.

</details>

## Skala oceniania odpowiedzi

| Punkty | Kryterium |
|---|---|
| 0 | Brak wyjaśnienia lub zasadniczo błędny mechanizm. |
| 1 | Rozpoznanie pojęć bez poprawnego opisu przebiegu i skutków. |
| 2 | Poprawne wyjaśnienie mechanizmu i pasujący przykład. |
| 3 | Poprawne wyjaśnienie uzupełnione o trafne przewidywanie skutku awarii, wskazanie ograniczenia lub uzasadnienie decyzji projektowej. |

Maksymalny wynik wynosi **30 punktów dla zestawu 10 pytań podstawowych** albo **60 punktów dla pełnego zestawu 20 pytań**.

## Pytania pogłębiające

- Pokaż to na swoim projekcie.
- Co się stanie, jeśli ten komponent wyłączymy?
- Po czym sprawdzisz, że rzeczywiście tak zadziałało?

Ocenie podlega rozumienie mechanizmu i jego konsekwencji. Brak dokładnej nazwy mechanizmu nie powinien przesłaniać poprawnego wyjaśnienia jego działania.
