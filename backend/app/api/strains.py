from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.strain import Strain
from typing import List

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_strains(db: Session = Depends(get_db)):
    strains = db.query(Strain).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "species": s.species,
            "difficulty": s.difficulty,
            "colonization_days": s.colonization_days
        } for s in strains
    ]