import io
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from presentationgenerator.services.presentation_service import PresentationService
from presentationgenerator.models.schemas import PresentationResult
from presentationgenerator.api.limiter import limiter
from presentationgenerator.services.auth_serivce import AuthService

router = APIRouter()

service = PresentationService()
auth = AuthService()


def _validate_pdf(file: UploadFile, pdf_bytes: bytes) -> None:
    """Shared validation logic for both endpoints."""
    if file.filename and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must have a .pdf extension.")
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded PDF file is empty.")
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        if len(reader.pages) == 0:
            raise HTTPException(status_code=400, detail="PDF file contains no pages.")
    except PdfReadError:
        raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file.")


@router.post("/presentation", response_model=PresentationResult, tags=["presentation"])
@limiter.limit("1/minute")
async def presentation(
    request: Request,
    token=Depends(auth.verify_token),
    file: UploadFile = File(...),
    chunk_size: int = 10,
):
    """
    Receives an uploaded PDF file and returns a full presentation as JSON.
    The `html` field contains the complete HTML string of the presentation.
    Protected by JWT token (query param `token`) and rate limited to 1 req/min per IP.
    """
    pdf_bytes = await file.read()
    _validate_pdf(file, pdf_bytes)

    topic = Path(file.filename).stem.replace("_", " ").replace("-", " ").title() if file.filename else "Presentation"

    try:
        result = service.create_from_pdf(pdf_bytes=pdf_bytes, topic=topic, chunk_size=chunk_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(e)}")


@router.post("/presentation/download", tags=["presentation"])
@limiter.limit("1/minute")
async def presentation_download(
    request: Request,
    token=Depends(auth.verify_token),
    file: UploadFile = File(...),
    chunk_size: int = 10,
):
    """
    Receives an uploaded PDF file and returns the generated presentation
    as a **downloadable HTML file** (`Content-Disposition: attachment`).

    The browser will prompt to save the file. The filename is derived
    from the original PDF name (e.g. `my_notes.pdf` → `my_notes_presentation.html`).

    Protected by JWT token (query param `token`) and rate limited to 1 req/min per IP.
    """
    pdf_bytes = await file.read()
    _validate_pdf(file, pdf_bytes)

    stem = Path(file.filename).stem if file.filename else "presentation"
    topic = stem.replace("_", " ").replace("-", " ").title()
    download_filename = f"{stem}_presentation.html"

    try:
        result = service.create_from_pdf(pdf_bytes=pdf_bytes, topic=topic, chunk_size=chunk_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(e)}")

    html_bytes = result.html.encode("utf-8")

    return StreamingResponse(
        content=io.BytesIO(html_bytes),
        media_type="text/html; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{download_filename}"',
            "Content-Length": str(len(html_bytes)),
            "X-Slides-Count": str(result.slides_count),
            "X-Topic": topic,
        },
    )