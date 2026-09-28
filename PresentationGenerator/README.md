# PDF to Presentation Generator

**Turn any PDF file into a ready-to-use HTML presentation — in minutes instead of hours.**

Built as a capstone project for the FlyRank Backend AI Engineering Internship.

---

## What does it do?

You send a PDF file through the API. The system extracts its text, splits it into slides, plans each slide using a local AI model (Bielik — a Polish open-source LLM), and returns a complete browser-ready HTML presentation with 16:9 slide layout and navigation.

A teacher who used to spend 2 hours preparing a presentation from a textbook chapter now gets it done in a few minutes.

---

## Implemented capstone concepts

| # | Concept | Where in the code |
|---|---|---|
| 1 | **API endpoints** | `api/routers/pdf_to_presentation_router.py`, `api/routers/auth_router.py` |
| 2 | **Authentication** | `services/auth_serivce.py` — register, login, logout, delete account (Supabase Auth) |
| 3 | **LLM integration** | `services/ai_service.py` — Ollama + Bielik (local model) |
| 4 | **Rate limiting** *(swap: replaces Background jobs — local generation is fast enough to not require a queue)* | `api/limiter.py` — SlowAPI, 1 req/min per IP |
| 5 | **Database** | *(planned - saving presentations of the users)* |

Total: 4 confirmed + caching in progress = **5 concepts**.

---

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — package manager
- [Ollama](https://ollama.com/) — local LLM runtime
- Supabase account (free tier)

---

## Running the project — step by step

### 1. Clone the repo and navigate to the project folder

```bash
git clone https://github.com/KrzysDev/My-10x-Solution.git
cd My-10x-Solution/PresentationGenerator
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Contents of `.env`:

```env
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_KEY=<your-anon-key>
SUPABASE_SERVICE_KEY=<your-service-role-key>   # required for account deletion
```

You can find your keys in the Supabase dashboard: **Project Settings → API**.

### 3. Install dependencies

```bash
uv sync
```

### 4. Download the AI model (Bielik)

```bash
ollama pull SpeakLeash/bielik-minitron-7B-v3.0-instruct:Q8_0
```

> The model is ~7 GB. Download it once; Ollama caches it locally.

### 5. Start the server

```bash
uv run uvicorn presentationgenerator.main:app --reload
```

API available at: **http://localhost:8000**

Swagger docs: **http://localhost:8000/docs**

---

## 5-minute demo

1. **Register an account:**
   ```
   POST /auth/register
   { "email": "demo@example.com", "password": "password123" }
   ```

2. **Log in and copy the `access_token` from the response:**
   ```
   POST /auth/login
   { "email": "demo@example.com", "password": "password123" }
   ```

3. **Send a PDF with the token:**
   - Open http://localhost:8000/docs
   - Endpoint: `POST /presentation`
   - Query param: `token=<access_token>`
   - Body: upload any `.pdf` file

4. **Receive the presentation:**
   - The JSON response contains an `html` field — save it as an `.html` file and open it in your browser
   - Or use the `slides` field (list of individual slide HTML snippets)

---

## Project structure

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
│   │   ├── prompts.py                 # LLM prompts (Polish → Bielik)
│   │   └── html_program_template.py  # HTML presentation template
│   └── services/
│       ├── auth_serivce.py            # Supabase Auth logic
│       ├── ai_service.py              # Ollama LLM wrapper
│       ├── planning_service.py        # Slide planning via LLM
│       ├── chunking_service.py        # Text → sentence chunks
│       ├── pdf_extraction_service.py  # PDF → text extraction
│       └── presentation_service.py   # Pipeline orchestrator
├── pyproject.toml
└── README.md
```

---

## API endpoints

### Auth (`/auth`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register with email + password |
| `POST` | `/auth/login` | Log in, returns `access_token` |
| `POST` | `/auth/logout` | Log out (invalidates token) |
| `DELETE` | `/auth/account` | Permanently delete the account |
| `GET` | `/auth/anonymous` | Anonymous sign-in (for testing) |
| `POST` | `/auth/verify` | Verify a JWT token |

### Presentations

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/presentation` | Upload a PDF → returns HTML presentation |

---

## Security

- API keys stored only in `.env` — never in code or in the repo
- `.gitignore` excludes `.env`, `*.db`, `.venv/`
- All protected endpoints require a valid Supabase JWT
- Rate limiting: 1 request / minute per IP on the generation endpoint

---

## Future ideas

- Save presentation history to Supabase database per user
- Background job (Celery) for large PDFs
- Export to `.pptx` instead of HTML only
- Cache results based on PDF file hash
- Support multiple LLM providers (OpenAI, Gemini as fallback)

---

*Author: Krzysztof Sokołowski · FlyRank Backend AI Engineering Internship · 2026*
