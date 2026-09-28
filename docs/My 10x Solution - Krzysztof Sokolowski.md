# My 10x Solution — Krzysztof Sokołowski

## 1. What problem am I solving?

A teacher who wants to prepare a presentation for a class based on a textbook chapter or a research article spends between 1.5 and 3 hours doing so — reading the text, selecting key information, designing slides, and formatting the content. This is the time teachers lack the most.

The same applies to students who study from PDFs: to create a revision presentation, they have to manually rewrite and condense the material.

**My 10x claim:** preparing a presentation from pages of study material that used to take 2 hours now takes a few minutes — it is more than 20× faster.

---

## 2. How does my solution work?

### The idea

The user sends any PDF file through the API. The system automatically:
1. Extracts text from the PDF
2. Splits the text into semantic chunks (groups of sentences)
3. For each chunk, generates a slide plan (title, category, key bullet points) using a local LLM
4. Generates a ready HTML slide from the plan
5. Returns a complete, browser-ready HTML presentation with navigation

For content generation I use **Bielik** — an open-source Polish language model (SpeakLeash/bielik-minitron-7B-v3.0-instruct) running locally via Ollama. This makes the system completely free and requires no external AI API account.

### Tech stack

- **FastAPI** — HTTP API framework
- **Supabase** — user authentication (Supabase Auth) and PostgreSQL
- **Ollama + Bielik** — local LLM for slide planning and generation
- **pypdf** — PDF text extraction
- **SlowAPI** — rate limiting
- **uv** — Python dependency management

---

## 3. Implemented concepts

| # | Concept | Where in the code | Description |
|---|---|---|---|
| 1 | **API endpoints** | `api/routers/pdf_to_presentation_router.py` `api/routers/auth_router.py` `api/routers/saved_presentations_router.py` | HTTP API with correct status codes, validation, and options for JSON response or direct HTML file download. |
| 2 | **Database** | `db/create_presentations_table.sql` `services/presentation_storage_service.py` `api/routers/saved_presentations_router.py` | Supabase PostgreSQL persistence with Row-Level Security (RLS). Saved presentations survive server restarts and are scoped per user. |
| 3 | **Authentication** | `services/auth_serivce.py` | Supabase Auth — register by email, login, logout, delete account. Protected endpoints require a valid JWT. |
| 4 | **LLM integration** | `services/ai_service.py` `services/planning_service.py` `services/presentation_service.py` | Two separate LLM calls per slide: first planning (bullet points), then HTML generation. Model: Bielik 7B via Ollama. |
| 5 | **Rate limiting** *(swap)* | `api/limiter.py` | SlowAPI — limit of 1 request/minute per IP on generation endpoints. Returns 429 with a Retry-After header. **Swap for Background jobs** — generation runs locally and is fast enough not to block the server for typical single-request use. |

> Swap #1 (Rate limiting instead of Background jobs): presentation generation runs locally via Ollama and does not depend on external services with API limits — synchronous processing is sufficient for typical usage.

---

## 4. How to run it

### Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/) with the Bielik model
- Supabase account (free tier)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/KrzysDev/My-10x-Solution.git
cd My-10x-Solution/PresentationGenerator

# 2. Fill in environment variables
cp .env.example .env
# Add SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY

# 3. Install dependencies
uv sync

# 4. Download the AI model (one-time, ~7 GB)
ollama pull SpeakLeash/bielik-minitron-7B-v3.0-instruct:Q8_0

# 5. Start the server
uv run uvicorn presentationgenerator.main:app --reload
```

API: http://localhost:8000 · Swagger docs: http://localhost:8000/docs

### Demo path (5 minutes)

1. `POST /auth/register` — create an account
2. `POST /auth/login` — log in, copy the `access_token`
3. Open http://localhost:8000/docs, go to `POST /presentation`, pass `token=<access_token>` as a query param and upload a PDF file
4. In the JSON response find the `html` field — save it to an `.html` file and open it in your browser

---

*Krzysztof Sokołowski · FlyRank Backend AI Engineering Internship · 2026*
