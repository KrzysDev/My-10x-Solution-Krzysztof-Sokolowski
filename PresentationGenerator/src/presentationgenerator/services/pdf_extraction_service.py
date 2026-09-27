
import textract
import os
import tempfile

from tkinter import filedialog as fd

from presentationgenerator.services.chunking_service import ChunkingService

class PDFExtractionService:
    def __init__(self):
        pass

    def extract_from_bytes(self, pdf_bytes: bytes) -> str:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        try:
            text = textract.process(tmp_path)
            return text.decode("utf-8")
        finally:
            os.remove(tmp_path)


def main():
    path_to_pdf = fd.askopenfilename(defaultextension="*.pdf")

    service = PDFExtractionService()

    with open(path_to_pdf, "rb") as f:
        bytes = f.read()

        text = service.extract_from_bytes(bytes)
        chunking_service = ChunkingService()

        chunks = chunking_service.chunk_text(text)

        print(chunks)

        print("=============Chunk size==============")

        print(len(chunks))


if __name__ == "__main__":
    main()


