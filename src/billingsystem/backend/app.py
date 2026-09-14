
from fastapi import FastAPI

from billingsystem.backend.api.routers.auth_router import router as auth_router

app = FastAPI()

app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "name" : "Arve - API used by Billing app for freelancers",
        "status" : "healthy",
        "version" : "0.1"
    }

