from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.criteria.criteria import Criteria
from app.schemas.criteria.criteria import CriteriaCreateUpdate, CriteriaResponse
from app.services.database import get_db

router = APIRouter(prefix="/criteria", tags=["Criteria"])


# ✅ Créer un critère
@router.post("/", response_model=CriteriaResponse)
def create_criteria(data: CriteriaCreateUpdate, db: Session = Depends(get_db)):

    new_criteria = Criteria(**data.dict())
    db.add(new_criteria)
    db.commit()
    db.refresh(new_criteria)
    return new_criteria


# ✅ Afficher tous les critères
@router.get("/", response_model=List[CriteriaResponse])
def get_all_criteria(db: Session = Depends(get_db)):
    return db.query(Criteria).all()


# ✅ Afficher un critère par ID
@router.get("/{criteria_id}", response_model=CriteriaResponse)
def get_criteria(criteria_id: int, db: Session = Depends(get_db)):
    criteria = db.query(Criteria).filter(Criteria.id == criteria_id).first()
    if not criteria:
        raise HTTPException(status_code=404, detail="Critère introuvable")
    return criteria


# ✅ Mettre à jour un critère
@router.put("/{criteria_id}", response_model=CriteriaResponse)
def update_criteria(
    criteria_id: int, data: CriteriaCreateUpdate, db: Session = Depends(get_db)
):
    criteria = db.query(Criteria).filter(Criteria.id == criteria_id).first()
    if not criteria:
        raise HTTPException(status_code=404, detail="Critère introuvable")

    # Mise à jour des valeurs
    for key, value in data.dict().items():
        setattr(criteria, key, value)

    db.commit()
    db.refresh(criteria)
    return criteria


# ✅ Supprimer un critère
@router.delete("/{criteria_id}")
def delete_criteria(criteria_id: int, db: Session = Depends(get_db)):
    criteria = db.query(Criteria).filter(Criteria.id == criteria_id).first()
    if not criteria:
        raise HTTPException(status_code=404, detail="Critère introuvable")

    db.delete(criteria)
    db.commit()
    return {"message": "Critère supprimé"}
