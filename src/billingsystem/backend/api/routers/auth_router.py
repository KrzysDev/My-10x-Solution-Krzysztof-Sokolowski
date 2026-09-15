from fastapi import APIRouter
from billingsystem.backend.services.auth_service import AuthService
from billingsystem.backend.models.auth_router_schemas import (
    SignInRequest,
    LoginRequest,
    LogoutRequest,
    DeleteAccountRequest,
)
from billingsystem.backend.services.supabase_service import SupabaseService


router = APIRouter()

supabase_service = SupabaseService()
auth_service = AuthService(supabase_service)


@router.post("/auth/sign_in")
def sign_up(request: SignInRequest):
    return auth_service.sign_up(
        email=request.email,
        password=request.password
    )


@router.post("/auth/log_in")
def log_in(request: LoginRequest):
    return auth_service.login(
        email=request.email,
        password=request.password
    )


@router.post("/auth/logout")
def logout(request: LogoutRequest):
    return auth_service.logout(access_token=request.access_token)


@router.delete("/auth/delete_account")
def delete_account(request: DeleteAccountRequest):
    return auth_service.delete_account(access_token=request.access_token)