from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "something something i will add later lorem ipsum lorem ipsum"
    }