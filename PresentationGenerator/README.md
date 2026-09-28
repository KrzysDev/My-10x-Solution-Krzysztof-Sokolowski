# PDF to Presentation Generator

**Zamień dowolny plik PDF w gotową, HTML-ową prezentację — w minuty zamiast godzin.**

Projekt wykonany jako capstone stażu FlyRank Backend AI Engineering.

---

## Co to robi?

Wysyłasz plik PDF przez API. System wyciąga z niego tekst, dzieli go na slajdy, planuje każdy slajd przy pomocy lokalnego modelu AI (Bielik — polskie LLM), a na końcu zwraca gotową prezentację w formacie HTML z podziałem 16:9.

Nauczyciel zamiast 2 godzin pracy ma prezentację w kilka minut.

---

## Zaimplementowane koncepty capstone

| # | Koncept | Gdzie w kodzie |
|---|---|---|
| 1 | **API endpoints** | `api/routers/pdf_to_presentation_router.py`, `api/routers/auth_router.py` |
| 2 | **Authentication** | `services/auth_serivce.py` — rejestracja, logowanie, wylogowanie, usuwanie konta (Supabase Auth) |
| 3 | **LLM integration** | `services/ai_service.py` — Ollama + Bielik (lokalny model) |
| 4 | **Rate limiting** *(swap: zastępuje Background jobs — generowanie jest lokalnie szybkie i nie wymaga kolejki)* | `api/limiter.py` — SlowAPI, 1 req/min per IP |
| 5 | **Caching** | *(planowane — hash MD5 PDF → wynik)* |

Łącznie: 4 pewne + caching w toku = **5 konceptów**.

---

## Wymagania

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — package manager
- [Ollama](https://ollama.com/) — lokalny LLM runtime
- Konto Supabase (darmowy tier)

---

## Uruchomienie — krok po kroku

### 1. Sklonuj repo i przejdź do folderu projektu

```bash
git clone https://github.com/KrzysDev/My-10x-Solution.git
cd My-10x-Solution/PresentationGenerator
```

### 2. Skonfiguruj zmienne środowiskowe

Skopiuj plik `.env.example` do `.env` i uzupełnij wartości:

```bash
cp .env.example .env
```

Zawartość `.env`:

```env
SUPABASE_URL=https://<twoj-projekt>.supabase.co
SUPABASE_KEY=<twoj-anon-key>
SUPABASE_SERVICE_KEY=<twoj-service-role-key>   # potrzebny do usuwania kont
```

Klucze znajdziesz w panelu Supabase: **Project Settings → API**.

### 3. Zainstaluj zależności

```bash
uv sync
```

### 4. Pobierz model AI (Bielik)

```bash
ollama pull SpeakLeash/bielik-minitron-7B-v3.0-instruct:Q8_0
```

> Model waży ~7 GB. Pobierz go raz; Ollama cachuje go lokalnie.

### 5. Uruchom serwer

```bash
uv run uvicorn presentationgenerator.main:app --reload
```

API jest dostępne pod: **http://localhost:8000**

Dokumentacja Swagger: **http://localhost:8000/docs**

---

## 5-minutowe demo

1. **Zarejestruj konto:**
   ```
   POST /auth/register
   { "email": "demo@example.com", "password": "haslo123" }
   ```

2. **Zaloguj się i skopiuj `access_token` z odpowiedzi:**
   ```
   POST /auth/login
   { "email": "demo@example.com", "password": "haslo123" }
   ```

3. **Wyślij PDF z tokenem:**
   - Otwórz http://localhost:8000/docs
   - Endpoint: `POST /presentation`
   - Query param: `token=<access_token>`
   - Body: wyślij dowolny plik `.pdf`

4. **Odbierz prezentację:**
   - Odpowiedź zawiera pole `html` — wklej je do pliku `.html` i otwórz w przeglądarce
   - Lub użyj pola `slides` (lista slajdów osobno)

---

## Struktura projektu

```
PresentationGenerator/
├── src/presentationgenerator/
│   ├── main.py                        # FastAPI app entry point
│   ├── api/
│   │   ├── limiter.py                 # SlowAPI rate limiter
│   │   └── routers/
│   │       ├── auth_router.py         # /auth/* endpoints
│   │       └── pdf_to_presentation_router.py  # /presentation endpoint
│   ├── models/
│   │   ├── schemas.py                 # Pydantic models
│   │   ├── prompts.py                 # LLM prompts (PL → Bielik)
│   │   └── html_program_template.py  # HTML presentation template
│   └── services/
│       ├── auth_serivce.py            # Supabase Auth logic
│       ├── ai_service.py              # Ollama LLM wrapper
│       ├── planning_service.py        # Slide planning via LLM
│       ├── chunking_service.py        # Text → sentence chunks
│       ├── pdf_extraction_service.py  # PDF → text
│       └── presentation_service.py   # Orchestrator
├── pyproject.toml
└── README.md
```

---

## Endpointy API

### Auth (`/auth`)

| Metoda | Endpoint | Opis |
|---|---|---|
| `POST` | `/auth/register` | Rejestracja email + hasło |
| `POST` | `/auth/login` | Logowanie, zwraca `access_token` |
| `POST` | `/auth/logout` | Wylogowanie (unieważnia token) |
| `DELETE` | `/auth/account` | Trwałe usunięcie konta |
| `GET` | `/auth/anonymous` | Logowanie anonimowe (do testów) |
| `POST` | `/auth/verify` | Weryfikacja tokenu JWT |

### Prezentacje

| Metoda | Endpoint | Opis |
|---|---|---|
| `POST` | `/presentation` | Upload PDF → zwraca prezentację HTML |

---

## Bezpieczeństwo

- Klucze API wyłącznie w `.env` — nigdy w kodzie ani w repo
- `.gitignore` wyklucza `.env`, `*.db`, `.venv/`
- Wszystkie chronione endpointy wymagają ważnego JWT z Supabase
- Rate limiting: 1 request / minutę na IP (endpoint generowania)

---

## Pomysły na przyszłość

- Zapis historii prezentacji w bazie Supabase per użytkownik
- Background job (Celery) dla długich PDF-ów
- Eksport do `.pptx` zamiast tylko HTML
- Cache wyników na podstawie hash pliku PDF
- Obsługa wielu modeli LLM (OpenAI, Gemini jako fallback)

---

*Autor: Krzysztof Sokołowski · FlyRank Backend AI Engineering Internship · 2026*
