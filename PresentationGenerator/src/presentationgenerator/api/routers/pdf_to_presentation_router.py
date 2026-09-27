import io
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from presentationgenerator.services.presentation_service import PresentationService
from presentationgenerator.models.schemas import PresentationResult
from presentationgenerator.api.limiter import limiter

router = APIRouter()

service = PresentationService()


@router.post("/presentation", response_model=PresentationResult, tags=["presentation"])
@limiter.limit("5/minute")
async def presentation(
    request: Request,
    file: UploadFile = File(...),
    chunk_size: int = 10
):
    """
    Receives an uploaded PDF file, validates it, and generates a full presentation.
    Rate limited to 5 requests per minute per IP.
    """
    if file.filename and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must have a .pdf extension.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded PDF file is empty.")

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        if len(reader.pages) == 0:
            raise HTTPException(status_code=400, detail="PDF file contains no pages.")
    except PdfReadError:
        raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file.")

    topic = Path(file.filename).stem.replace("_", " ").replace("-", " ").title() if file.filename else "Prezentacja"

    try:
        result = service.create_from_pdf(
            pdf_bytes=pdf_bytes,
            topic=topic,
            chunk_size=chunk_size
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(e)}")