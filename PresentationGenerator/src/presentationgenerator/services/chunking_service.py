import re
from presentationgenerator.models.schemas import TextChunk


class ChunkingService:
    def __init__(self):
        pass

    def chunk_text(self, text: str, chunk_size: int = 10) -> list[TextChunk]:
        """
        Splits text into sentence-based chunks and wraps them in TextChunk models.
        """
        pattern = r'[A-ZĄĆĘŁŃÓŚŹŻ][^.]*\.' 
        matches = re.findall(pattern, text)

        chunks: list[TextChunk] = []
        counter = 1

        for i in range(0, len(matches), chunk_size):
            chunks.append(TextChunk(
                id=counter,
                content=matches[i:i + chunk_size]
            ))
            counter += 1

        return chunks


if __name__ == "__main__":
    service = ChunkingService()
    result = service.chunk_text("First sentence. Second sentence. Third sentence.")
    print(result)
