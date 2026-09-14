from rich.console import Console
from billingsystem.backend.services.supabase_service import SupabaseService
from fastapi import HTTPException

console = Console()

class AuthService:
    def __init__(self, supabase_service: SupabaseService):
        self.supabase = supabase_service.get_client()
        self.user_id = None

    def login(self, email: str, password: str) -> str:
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if response.user:
                self.user_id = response.user.id
                return self.user_id
        except Exception as e:
            print("Exception in login: ", e)
            raise HTTPException(status_code=401, detail=f"Passoword or email are incorrect.")


    def sign_up(self, email: str, password: str) -> str:
        try:
            response = self.supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )
            if response.user:
                self.user_id = response.user.id
                return self.user_id
        except:
            raise HTTPException(status_code=500, detail="something went wrong with the sign up")
        
