from fastapi import APIRouter, Depends
from presentationgenerator.models.schemas import EmailPasswordRequest, TokenRequest

from presentationgenerator.services.auth_serivce import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

service = AuthService()



@router.post("/register", summary="Register a new account with email and password")
async def register(body: EmailPasswordRequest):
    """Creates a new user account. Returns the created user object."""
    return await service.sign_up(email=body.email, password=body.password)


@router.post("/login", summary="Log in with email and password")
async def login(body: EmailPasswordRequest):
    """
    Authenticates a user and returns a session with an access_token.
    Pass this token in the Authorization header as: Bearer <access_token>
    """
    return await service.sign_in(email=body.email, password=body.password)


@router.post("/logout", summary="Log out — invalidate the current session token")
async def logout(body: TokenRequest):
    """Invalidates the provided JWT access token."""
    return await service.sign_out(token=body.token)


@router.delete("/account", summary="Permanently delete the authenticated user's account")
async def delete_account(body: TokenRequest):
    """
    Deletes the account associated with the provided access token.
    This action is irreversible.
    """
    return await service.delete_account(token=body.token)


@router.get("/anonymous", summary="Sign in anonymously (no credentials required)")
async def sign_in_anonymously():
    """Creates an anonymous session. Kept for quick testing."""
    return await service.sign_in_anonymously()


@router.post("/verify", summary="Verify a JWT token")
async def verify_token(body: TokenRequest):
    """Returns user data if the token is valid, 401 otherwise."""
    return service.verify_token(body.token)
