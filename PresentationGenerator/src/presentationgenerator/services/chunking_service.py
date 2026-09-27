
import re

class ChunkingService:
    def __init__(self):
        pass

    def chunk_text(self, text: str, chunk_size: int = 10):
        pattern = r'[A-ZĄĆĘŁŃÓŚŹŻ][^.]*\.' 
        matches = re.findall(pattern, text)

        chunks = []

        counter = 1

        for i in range(0, len(matches), chunk_size):
            chunks.append({
                "id" : counter,
                "content" : matches[i:i + chunk_size]
            })

            counter += 1


        return chunks
    




if __name__ == "__main__":
    service = ChunkingService()

    print(service.chunk_text("Something something something. Something something something."))

