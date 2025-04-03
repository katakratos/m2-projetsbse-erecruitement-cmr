from fastapi import FastAPI
from app.routes.jobs import jobs
from app.routes.user import users, auth

from app.routes.ahpag import ag, ag_with_pygad, ahpAg

from app.routes.criteria import criteria

from app.services.database import init_db


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
    return {
        "message": "Bienvenue sur l’API FastAPI avec SQLite et Poetry"
        
        }
