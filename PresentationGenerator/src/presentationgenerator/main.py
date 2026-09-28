from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from presentationgenerator.api.limiter import limiter
from presentationgenerator.api.routers.pdf_to_presentation_router import router as presentation_router
from presentationgenerator.api.routers.auth_router import router as auth_router


app = FastAPI(
    title="PDF to HTML Presentation Generator",
    summary="This API is built for anyone who wants to convert PDF into a presentation. Its ideal tool for teachers and students and anyone else who would want to make a presentation from some kind of book or pdf file.",
    version="0.0.1",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(presentation_router)
app.include_router(auth_router)


@app.get("/", tags=["root"])
def root():
    return {
        "message": "Presentation Generator API is running"
    }