from billingsystem.backend.services.supabase_service import SupabaseService
from fastapi import HTTPException


class AuthService:
    def __init__(self, supabase_service: SupabaseService):
        self.supabase = supabase_service.get_client()

    def _build_session_response(self, response) -> dict:
        if not response.user or not response.session:
            raise HTTPException(
                status_code=401,
                detail="Failed to create a session (email confirmation may be required)."
            )

        return {
            "user": {
                "id": response.user.id,
                "email": response.user.email,
            },
            "session": {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_at": response.session.expires_at,
                "expires_in": response.session.expires_in,
                "token_type": response.session.token_type,
            },
        }

    def login(self, email: str, password: str) -> dict:
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return self._build_session_response(response)
        except HTTPException:
            raise
        except Exception as e:
            print("Exception in login: ", e)
            raise HTTPException(status_code=401, detail="Incorrect password or email.")

    def sign_up(self, email: str, password: str) -> dict:
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            return self._build_session_response(response)
        except HTTPException:
            raise
        except Exception as e:
            print("Exception in sign_up: ", e)
            raise HTTPException(status_code=500, detail="Something went wrong during sign-up.")

    def logout(self, access_token: str) -> dict:
        try:
            self.supabase.auth.admin.sign_out(access_token)
            return {"detail": "Logged out successfully."}
        except Exception as e:
            print("Exception in logout: ", e)
            raise HTTPException(status_code=400, detail="Failed to log out.")

    def delete_account(self, access_token: str) -> dict:
        try:
            user_response = self.supabase.auth.get_user(access_token)
            if not user_response or not user_response.user:
                raise HTTPException(status_code=401, detail="Invalid or expired token.")

            user_id = user_response.user.id
            self.supabase.auth.admin.delete_user(user_id)
            return {"detail": "Account has been deleted."}
        except HTTPException:
            raise
        except Exception as e:
            print("Exception type:", type(e))
            print("Exception args:", e.args)
            print("Exception repr:", repr(e))
            # AuthApiError z gotrue ma zwykle .status i .message
            print("status:", getattr(e, "status", None))
            print("message:", getattr(e, "message", None))
            raise HTTPException(status_code=400, detail="Failed to delete account.")