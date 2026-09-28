# My 10x Solution — Krzysztof Sokołowski

## 1. Jaki problem rozwiązuję?

Nauczyciel, który chce przygotować prezentację na lekcję na podstawie rozdziału podręcznika lub artykułu naukowego, spędza na tym od 1,5 do 3 godzin — czyta tekst, wybiera kluczowe informacje, projektuje slajdy i formatuje treść. To czas, którego nauczycielom brakuje najbardziej.

To samo dotyczy uczniów i studentów, którzy uczą się z PDF-ów: żeby zrobić powtórkę w formie prezentacji, muszą ręcznie przepisać i skrócić materiał.

**Moje 10x claim:** przygotowanie prezentacji ze stron materiału, które zajmuje 2 godziny, zajmuje teraz kilka minut — jest ponad 20x szybsze.

---

## 2. Jak działa moje rozwiązanie?

### Idea

Użytkownik wysyła dowolny plik PDF przez API. System automatycznie:
1. Wyciąga tekst z PDF
2. Dzieli tekst na semantyczne chunki (grupy zdań)
3. Dla każdego chunka generuje plan slajdu (tytuł, kategoria, punkty kluczowe) przy pomocy lokalnego modelu LLM
4. Generuje gotowy HTML slajdu na podstawie planu
5. Zwraca kompletną, przeglądarkową prezentację HTML z nawigacją

Do generowania treści używam **Bielika** — polskiego, otwartego modelu językowego (SpeakLeash/bielik-minitron-7B-v3.0-instruct), który działa lokalnie przez Ollama. Dzięki temu system jest w pełni darmowy i nie wymaga konta w żadnym zewnętrznym API AI.

### Stack technologiczny

- **FastAPI** — framework HTTP API
- **Supabase** — autentykacja użytkowników (Supabase Auth) i PostgreSQL
- **Ollama + Bielik** — lokalny model LLM do planowania i generowania slajdów
- **pypdf** — ekstrakcja tekstu z PDF
- **SlowAPI** — rate limiting
- **uv** — zarządzanie zależnościami Python

---

## 3. Zaimplementowane koncepty

| # | Koncept | Gdzie w kodzie | Opis |
|---|---|---|---|
| 1 | **API endpoints** | `api/routers/pdf_to_presentation_router.py` `api/routers/auth_router.py` | HTTP API z poprawnymi kodami statusu i walidacją Pydantic. Endpoint `POST /presentation` przyjmuje plik PDF i zwraca JSON z HTML prezentacją. |
| 2 | **Authentication** | `services/auth_serivce.py` | Supabase Auth — rejestracja emailem, logowanie, wylogowanie, usuwanie konta. Chroniony endpoint `/presentation` wymaga ważnego JWT. |
| 3 | **LLM integration** | `services/ai_service.py` `services/planning_service.py` `services/presentation_service.py` | Dwa osobne wołania LLM per slajd: najpierw planowanie (bullet points), potem generowanie HTML. Model: Bielik 7B przez Ollama. |
| 4 | **Rate limiting** *(swap)* | `api/limiter.py` | SlowAPI — limit 1 request/minutę per IP na endpoint generowania prezentacji. Zwraca 429 z nagłówkiem Retry-After. **Swap zamiast Background jobs** — generowanie odbywa się lokalnie i jest wystarczająco szybkie, by nie blokować serwera. |
| 5 | **Containerized stack** *(swap)* | `docker-compose.yml` *(planowane)* | Cały system startuje przez `docker compose up`. **Swap zamiast Caching** — ze względu na priorytet uruchamialności przez osobę z zewnątrz. |

> Swap #1 (Rate limiting zamiast Background jobs): generowanie prezentacji działa lokalnie przez Ollama i nie jest zależne od zewnętrznych serwisów z limitami — synchroniczne przetwarzanie jest wystarczające dla typowego użycia.

> Swap #2 (Containerized stack zamiast Caching): caching jest zaplanowany jako future improvement; Dockeryzacja jest wymagana dla M4 (runnable by a stranger) i ma priorytet.

---

## 4. Jak uruchomić

### Wymagania

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/) z modelem Bielik
- Konto Supabase (darmowy tier)

### Kroki

```bash
# 1. Sklonuj repo
git clone https://github.com/KrzysDev/My-10x-Solution.git
cd My-10x-Solution/PresentationGenerator

# 2. Uzupełnij zmienne środowiskowe
cp .env.example .env
# Wpisz SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY

# 3. Zainstaluj zależności
uv sync

# 4. Pobierz model AI (jednorazowo, ~7 GB)
ollama pull SpeakLeash/bielik-minitron-7B-v3.0-instruct:Q8_0

# 5. Uruchom serwer
uv run uvicorn presentationgenerator.main:app --reload
```

API: http://localhost:8000 · Swagger docs: http://localhost:8000/docs

### Demo path (5 minut)

1. `POST /auth/register` — utwórz konto
2. `POST /auth/login` — zaloguj się, skopiuj `access_token`
3. Otwórz http://localhost:8000/docs, endpoint `POST /presentation`, podaj `token=<access_token>` i wyślij plik PDF
4. W odpowiedzi JSON znajdź pole `html` — zapisz je do pliku `.html` i otwórz w przeglądarce

---

*Krzysztof Sokołowski · FlyRank Backend AI Engineering Internship · 2026*
