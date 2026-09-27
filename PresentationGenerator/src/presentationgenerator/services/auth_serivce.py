
import os
from supabase import create_client, Client
from dotenv import find_dotenv, load_dotenv
import asyncio

load_dotenv(find_dotenv())

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

class AuthService:
    def __init__(self):
        pass

    async def sign_in_annonymously(self):
        supabase: Client = create_client(url, key)

        response = supabase.auth.sign_in_anonymously()

        return response


async def main():
    service = AuthService()

    data = await service.sign_in_annonymously()

    print(data)


if __name__ == "__main__":
    asyncio.run(main())
    

