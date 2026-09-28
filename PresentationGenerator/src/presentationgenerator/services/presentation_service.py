"""
PresentationService orchestrates document extraction, text chunking,
slide planning, HTML generation, and final presentation rendering.
"""

import re
from typing import Optional
from presentationgenerator.models.schemas import TextChunk, Plan, PresentationResult
from presentationgenerator.models.prompts import CREATING_PRESENTATION_PROMPT
from presentationgenerator.models.html_program_template import render_presentation_html
from presentationgenerator.services.pdf_extraction_service import PDFExtractionService
from presentationgenerator.services.chunking_service import ChunkingService
from presentationgenerator.services.planning_service import PlanningService
from presentationgenerator.services.ai_service import AiService


class PresentationService:
    def __init__(
        self,
        pdf_service: Optional[PDFExtractionService] = None,
        chunking_service: Optional[ChunkingService] = None,
        planning_service: Optional[PlanningService] = None,
        ai_service: Optional[AiService] = None,
    ):
        """
        Initializes the PresentationService with its required sub-services.
        """
        self.pdf_service = pdf_service or PDFExtractionService()
        self.chunking_service = chunking_service or ChunkingService()
        self.planning_service = planning_service or PlanningService(ai_service=ai_service)
        self.ai_service = ai_service or self.planning_service.ai_service

    def _clean_html_response(self, raw_response: str) -> str:
        """
        Extracts clean HTML code from model output, stripping markdown code blocks
        or commentary.
        """
        # Look for ```html ... ``` or ``` ... ``` code blocks
        code_block_match = re.search(r"```(?:html)?\s*([\s\S]*?)\s*```", raw_response, re.IGNORECASE)
        if code_block_match:
            html = code_block_match.group(1).strip()
        else:
            # Fallback: extract substring between first <div and last </div>
            div_match = re.search(r"(<div[\s\S]*</div>)", raw_response, re.IGNORECASE)
            if div_match:
                html = div_match.group(1).strip()
            else:
                html = raw_response.strip()

        # Ensure container class exists
        if "slide-container" not in html:
            html = f'<div class="slide-container"><div class="slide-body">{html}</div></div>'

        return html

    def generate_slide_html(
        self,
        plan: Plan,
        slide_number: int,
        total_slides: int,
        topic: str = "Presentation"
    ) -> str:
        """
        Generates a single HTML slide based on a slide plan.

        :param plan: Plan instance describing the slide structure.
        :param slide_number: Current slide 1-based index.
        :param total_slides: Total number of slides.
        :param topic: Main subject or topic of the presentation.
        :return: Cleaned HTML slide snippet.
        """
        prompt = CREATING_PRESENTATION_PROMPT.format(
            plan_text=plan.content,
            slide_number=slide_number,
            total_slides=total_slides,
            presentation_topic=topic
        )

        raw_response = self.ai_service.ask(prompt)
        return self._clean_html_response(raw_response)

    def _create_from_text(
        self,
        text: str,
        topic: str = "Presentation",
    ) -> PresentationResult:
        """
        Generates a full presentation directly from plain text.

        :param text: Source document text.
        :param topic: Presentation title or topic.
        :param chunk_size: Number of sentences per slide chunk.
        :return: PresentationResult containing final HTML and metadata.
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")

        chunks = self.chunking_service.chunk_text(text)

        # Fallback if no sentence boundaries matched
        if not chunks:
            chunks = [TextChunk(id=1, content=text.strip())]

        total_slides = len(chunks)
        slides_html: list[str] = []

        print(f"detected: {len(chunks)}....")

        for idx, chunk in enumerate(chunks, start=1):
            # 1. Generate plan for the chunk
            plan = self.planning_service.plan(chunk)

            print(f"creating.....{idx}/{len(chunks)}")

            # 2. Generate HTML slide from the plan
            slide_html = self.generate_slide_html(
                plan=plan,
                slide_number=idx,
                total_slides=total_slides,
                topic=topic
            )
            slides_html.append(slide_html)

        # 3. Inject all slides into the PowerPoint HTML viewer
        final_html = render_presentation_html(slides_html)

        return PresentationResult(
            html=final_html,
            slides_count=total_slides,
            topic=topic,
            slides=slides_html
        )

    def create_from_pdf(
        self,
        pdf_bytes: bytes,
        topic: str = "Presentation",
        chunk_size: int = 10
    ) -> PresentationResult:
        """
        Generates a full presentation from PDF bytes.

        :param pdf_bytes: Raw bytes of the uploaded PDF file.
        :param topic: Presentation title or topic.
        :param chunk_size: Number of sentences per slide chunk.
        :return: PresentationResult containing final HTML and metadata.
        """
        extracted_text = self.pdf_service.extract_from_bytes(pdf_bytes)
        return self._create_from_text(
            text=extracted_text,
            topic=topic
        )


if __name__ == "__main__":
    import os
    import sys
    import webbrowser
    import tkinter as tk
    from tkinter import filedialog as fd
    from pathlib import Path

    # Ensure project src directory is in sys.path when running script directly
    src_dir = str(Path(__file__).resolve().parent.parent.parent)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    # Initialize tkinter root and hide default window
    root = tk.Tk()
    root.withdraw()

    print("Please select a PDF file in the dialog window...")
    path_to_pdf = fd.askopenfilename(
        title="Select a PDF file for presentation generation",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )

    if not path_to_pdf:
        print("No PDF file selected. Operation cancelled.")
        sys.exit(0)

    pdf_file_path = Path(path_to_pdf)
    topic = pdf_file_path.stem.replace("_", " ").replace("-", " ").title()

    print(f"Selected file: {pdf_file_path.name}")
    print(f"Detected topic: {topic}")
    print("Reading PDF file bytes...")

    with open(path_to_pdf, "rb") as f:
        pdf_bytes = f.read()

    # Initialize full real pipeline
    service = PresentationService()

    print("Starting presentation generation pipeline (Extracting -> Chunking -> Planning -> Slide Generation)...")
    result = service.create_from_pdf(
        pdf_bytes=pdf_bytes,
        topic=topic,
        chunk_size=10
    )

    output_file = pdf_file_path.with_name(f"{pdf_file_path.stem}_presentation.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.html)

    print("\n==========================================")
    print(" Presentation generated successfully!")
    print(f" Total slides: {result.slides_count}")
    print(f" Saved presentation to: {output_file.resolve()}")
    print("==========================================\n")

    webbrowser.open(f"file://{output_file.resolve()}")
