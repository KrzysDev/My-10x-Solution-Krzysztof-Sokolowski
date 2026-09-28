"""
Service responsible for generating slide plans from text chunks.
"""

from typing import Optional
from presentationgenerator.models.schemas import TextChunk, Plan
from presentationgenerator.models.prompts import PLANNING_PROMPT
from presentationgenerator.services.ai_service import AiService


class PlanningService:
    def __init__(self, ai_service: Optional[AiService] = None):
        """
        Initializes PlanningService with an AiService instance.
        """
        self.ai_service = ai_service or AiService()

    def plan(self, chunk: TextChunk) -> Plan:
        """
        Generates a bullet-point slide plan for the given TextChunk.

        :param chunk: TextChunk containing the extracted text.
        :return: Plan instance with the plan text in its content attribute.
        """
        chunk_text = chunk.text
        prompt = PLANNING_PROMPT.format(chunk_text=chunk_text)
        
        response_text = self.ai_service.ask(prompt)
        
        return Plan(content=response_text.strip())


if __name__ == "__main__":
    test_chunk = TextChunk(
        id=1,
        content=[
            "Sztuczna inteligencja zmienia oblicze nowoczesnej edukacji.",
            "Nauczyciele mogą wykorzystywać modele językowe do szybkiego tworzenia materiałów.",
            "Lokalne modele gwarantują pełne bezpieczeństwo danych uczniów."
        ]
    )

    service = PlanningService()
    plan_result = service.plan(test_chunk)
    print("--- Generated Plan ---")
    print(plan_result.content)
