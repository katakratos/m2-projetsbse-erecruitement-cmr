from pydantic import BaseModel


# 🔹 Schéma pour création et mise à jour
class CriteriaCreateUpdate(BaseModel):
    name: str
   
    job_id: int

# 🔹 Schéma pour affichage (réponse)
class CriteriaResponse(CriteriaCreateUpdate):
    id: int
    job_id: int


    class Config:
        from_attributes = True  # ✅ Permet la conversion automatique SQLAlchemy → Pydantic
