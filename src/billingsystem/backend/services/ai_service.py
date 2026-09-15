import base64
from ollama import chat

class AiService:
    def ask(self, prompt: str, image: str | None = None):
       # if image:
        #    print(f"[DEBUG] Rozmiar base64: {len(image)} znaków")
         #   print(f"[DEBUG] Początek: {image[:100]}...")

        message = {
            'role': 'user',
            'content': prompt,
        }
        
        if image:
            message['images'] = [image] 
        
        response = chat(
            model='ornith-1.5:9b',
            messages=[message],
        )
        return response.message.content


if __name__ == "__main__":
    service = AiService()

    path = input("path to image: ")
    prompt = input("prompt: ")

    with open(path, "rb") as image_file:

        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        print(service.ask(prompt, encoded_string))