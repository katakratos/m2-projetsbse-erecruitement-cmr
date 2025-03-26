from fastapi import FastAPI
from app.routes.user import users, auth

app = FastAPI(title="eRecruitementCMR plateform with FastAPI + poetry")

app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur l’API FastAPI avec SQLite et Poetry"
        # "secret_key": settings.SECRET_KEY,
        # "database_url": settings.DATABASE_URL,
        # "debug_mode": settings.DEBUG
        }
