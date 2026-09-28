import os
from fastapi import HTTPException
from supabase import create_client, Client
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")


def _get_client() -> Client:
    """Returns a Supabase client. Called per-request to stay stateless."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


class AuthService:
    async def sign_up(self, email: str, password: str):
        """
        Registers a new user with email and password via Supabase Auth.
        Returns the new user object on success.
        """
        supabase = _get_client()
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if not response.user:
                raise HTTPException(status_code=400, detail="Sign-up failed. Check your email and password.")
            return response.user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Sign-up error: {str(e)}") from e

    async def sign_in(self, email: str, password: str):
        """
        Signs in a user with email and password.
        Returns the session (including access_token).
        """
        supabase = _get_client()
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if not response.session:
                raise HTTPException(status_code=401, detail="Invalid credentials.")
            return response.session
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Sign-in error: {str(e)}") from e

    async def sign_out(self, token: str):
        """
        Signs out the user by invalidating their JWT access token.
        """
        supabase = _get_client()
        try:
            # Set the session so Supabase knows which user to sign out
            supabase.auth.set_session(access_token=token, refresh_token="")
            supabase.auth.sign_out()
            return {"message": "Signed out successfully."}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Sign-out error: {str(e)}") from e

    async def delete_account(self, token: str):
        """
        Deletes the authenticated user's account permanently.
        Requires the user's valid access token. Uses the Supabase Admin API.
        """
        supabase = _get_client()
        try:
            user_response = supabase.auth.get_user(token)
            if not user_response or not user_response.user:
                raise HTTPException(status_code=401, detail="Invalid token.")

            user_id = user_response.user.id

            service_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
            if not service_key:
                raise HTTPException(
                    status_code=500,
                    detail="Server is not configured for account deletion (missing SUPABASE_SERVICE_KEY)."
                )

            admin_client = create_client(SUPABASE_URL, service_key)
            admin_client.auth.admin.delete_user(user_id)

            return {"message": "Account deleted successfully."}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Delete account error: {str(e)}") from e

    async def sign_in_anonymously(self):
        """Signs in anonymously — no credentials required."""
        supabase = _get_client()
        return supabase.auth.sign_in_anonymously()

    def verify_token(self, token: str):
        """
        Verifies a JWT access token and returns the user.
        Raises HTTP 401 if the token is invalid or expired.
        """
        supabase = _get_client()
        try:
            response = supabase.auth.get_user(token)
            if not response or not response.user:
                raise HTTPException(status_code=401, detail="Invalid token.")
            return response.user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token.") from e
