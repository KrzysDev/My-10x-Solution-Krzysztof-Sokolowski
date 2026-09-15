from pydantic import BaseModel

class SignInRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LogoutRequest(BaseModel):
    access_token: str

class DeleteAccountRequest(BaseModel):
    access_token: str