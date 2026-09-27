from fastapi import FastAPI
from presentationgenerator.api.routers.pdf_to_presentation_router import router as presentation_router

app = FastAPI(
    title="PDF to HTML Presentation Generator",
    summary="This API is built for anyone who wants to convert PDF into a presentation. Its ideal tool for teachers and students and anyone else who would want to make a presentation from some kind of book or pdf file.",
    version="0.0.1",
)

app.include_router(presentation_router)

@app.get("/", tags=["root"])
def root():
    return {
        "something something i will add later lorem ipsum lorem ipsum"
    }