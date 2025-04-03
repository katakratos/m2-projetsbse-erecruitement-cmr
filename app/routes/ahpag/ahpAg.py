import json
from fastapi import APIRouter, HTTPException, Depends, logger
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

import os
from app.services.database import get_db
from app.models.candidates.candidat import Candidate

from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/ahp-genetic", tags=["AHP-Method"])

# 📌 Définition du modèle Pydantic pour recevoir la matrice AHP
class MatrixInput(BaseModel):
    preference_matrix: List[float]

# 📌 Définition du chemin du fichier CSV contenant les scores des candidats
CANDIDATES_FILE_PATH = "./app/routes/ahpag/candidates.csv"  

# 🔥 Fonction pour appliquer l'AHP
def ahp_method(preference_matrix, candidates_scores):

    matrix = np.array(preference_matrix).reshape(7,7)

    # ✅ Vérification de la cohérence avec l'Indice de Cohérence (CI) et le Ratio de Cohérence (CR)
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    max_eigenvalue = np.max(eigenvalues)  # Plus grande valeur propre
    n = matrix.shape[0]
    CI = (max_eigenvalue - n) / (n - 1)

    # Valeurs RI (Random Index) standards pour différentes tailles de matrice
    RIValues = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
    RI = RIValues.get(n, 1.32)  # On prend 1.32 si la matrice est de 7x7

    CR = CI / RI if RI else 0  # Ratio de cohérence
    if CR > 0.1:
        raise ValueError(f"Matrice incohérente (CR = {CR:.2f} > 0.1). Révisez votre matrice.")

    # ✅ Calcul des poids avec la méthode des valeurs propres
    weights = eigenvectors[:, np.argmax(eigenvalues)].real  # Vecteur propre correspondant à max eigenvalue
    weights /= weights.sum()  # Normalisation

# Sauvegarde des poids en JSON
    os.makedirs("data", exist_ok=True)  # Assure que le dossier existe
    with open("data/weights.json", "w") as f:
        json.dump(weights.tolist(), f)  # Conversion en liste Python

    # ✅ Calcul du score final des candidats avec sélection des colonnes correctes
    criteria_columns = candidates_scores.columns[1:8]  # 🔥 Vérifie que ce sont bien les critères
    candidates_scores["final_score"] = candidates_scores[criteria_columns].dot(weights)

    # ✅ Trier les 30 meilleurs candidats et ajouter leur classement
    top_50 = candidates_scores.nlargest(50, "final_score")
    top_50 = top_50.sort_values(by="final_score", ascending=False)
    top_50["ahp_rank"] = range(1, len(top_50) + 1)

    # ✅ Sauvegarde en JSON
    top_50.to_json("data/top_30_candidates.json", orient="records")

    return top_50

# 🚀 Endpoint pour exécuter AHP en lisant le fichier local
@router.post("/ahp/")
async def process_ahp(data: MatrixInput, db: Session = Depends(get_db)):
    preference_matrix = data.preference_matrix
    if len(preference_matrix) != 49:
        raise HTTPException(status_code=400, detail="Il faut exactement 49 valeurs.")

    # 📌 Vérifier si le fichier existe
    if not os.path.exists(CANDIDATES_FILE_PATH):
        raise HTTPException(status_code=500, detail="Le fichier des scores des candidats est introuvable.")

    try:
        # 📌 Lire les scores des candidats depuis le fichier CSV
        candidates_scores = pd.read_csv(CANDIDATES_FILE_PATH)

        # 📌 Appliquer l'AHP
        top_50 = ahp_method(preference_matrix, candidates_scores)

        # 📌 Ajouter la colonne du classement AHP avant d'enregistrer
        top_50 = top_50.sort_values(by="final_score", ascending=False)
        top_50["ahp_rank"] = range(1, len(top_50) + 1)

        # 📌 Enregistrer les 30 meilleurs candidats en base de données
        for i, row in top_50.iterrows():
            candidate = Candidate(
            name=row["name"],
            final_score=row["final_score"],
            ahp_rank=row["ahp_rank"]  # 🔥 Ajoute le classement AHP ici
    )
            db.add(candidate)

        return {"message": "AHP terminé", "top_30": top_50.to_dict(orient="records")}
   
   
    except pd.errors.EmptyDataError:
        raise HTTPException(400, "Le fichier CSV est vide")
    except pd.errors.ParserError:
        raise HTTPException(400, "Format CSV invalide")
    except ValueError as ve:
        logger.error("Erreur de valeur: %s", str(ve))
        raise HTTPException(400, str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


