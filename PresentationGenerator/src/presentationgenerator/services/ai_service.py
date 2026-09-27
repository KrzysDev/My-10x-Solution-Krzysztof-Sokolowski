
from ollama import chat
from ollama import ChatResponse

class AiService:
    def __init__(self, model: str = "SpeakLeash/bielik-minitron-7B-v3.0-instruct:Q8_0"):
        self.MODEL = model


    def ask(self, prompt: str):
        response: ChatResponse = chat(
        model=self.MODEL,
        messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ],
        )
        return response.message.content



if __name__ == "__main__":
    service = AiService()

    print(service.ask("dlaczego niebo jest niebieskie?"))

