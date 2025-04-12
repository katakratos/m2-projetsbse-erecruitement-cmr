from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.ahpag import ag, ag_with_pygad, ahpAg
from app.routes.criteria import criteria
from app.routes.jobs import jobs
from app.routes.user import auth, users
from app.services.database import init_db

app = FastAPI()

#  Ajout du middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # <-- ou ["*"] si tu veux tout autoriser (non recommandé en prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI(title="eRecruitementCMR plateform with FastAPI ")

# Initialisation asynchrone recommandée

init_db()

app.include_router(users.router)
app.include_router(auth.router)

app.include_router(jobs.router)

app.include_router(criteria.router)

app.include_router(ahpAg.router)
app.include_router(ag_with_pygad.router)
app.include_router(ag.router)


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l’API FastAPI avec SQLite et Poetry"}
