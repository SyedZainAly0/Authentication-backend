from fastapi import FastAPI
from app.routes import auth

app = FastAPI(title="Auth Backend")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Auth API is running"}
