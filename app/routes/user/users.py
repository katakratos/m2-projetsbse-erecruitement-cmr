from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user.user import User
from app.schemas.user.user import UserCreate, UserResponse, UserUpdate
from app.services.database import get_db
from app.services.utils import hash_password

router = APIRouter(prefix="/Recruiters", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Vérifie si l'email existe déjà
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Hache le mot de passe
    hashed_password = hash_password(user.password)

    # Crée l'utilisateur dans la base de données
    db_user = User(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Retourne l'utilisateur sans son mot de passe
    return UserResponse(
        id=db_user.id, email=db_user.email
    )  # Grâce à `response_model=UserResponse`, FastAPI formatera la réponse selon ce modèle.


@router.get("/all", response_model=list[UserResponse])
def get_all_user(db: Session = Depends(get_db)):
    recruiters = db.query(User).all()
    if not recruiters:
        raise HTTPException(status_code=404, detail="Aucun recruiter trouvé")
    return recruiters


@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return UserResponse(id=db_user.id, email=db_user.email)


@router.put("/{email}", response_model=UserResponse)
def update_user(email: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Mise à jour du mot de passe (ou d'autres champs)
    if user_update.password:
        db_user.password = user_update.password  # Hash le mot de passe ici !

    db.commit()
    db.refresh(db_user)

    return UserResponse(id=db_user.id, email=db_user.email)
