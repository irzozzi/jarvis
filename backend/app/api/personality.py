from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from .. import schemas, models
from ..api import deps
from ..services import personality_service
from ..services.personality_questions import QUESTIONS

router = APIRouter(prefix="/personality", tags=["personality"])


@router.get("/questions", response_model=List[schemas.QuestionOut])
def get_questions():
    """
    Возвращает список вопросов для определения личности (OCEAN).
    """
    return [{"id": q["id"], "text": q["text"]} for q in QUESTIONS]


@router.post("/", response_model=schemas.PersonalityOut)
def create_or_update_personality(
    personality_in: schemas.PersonalityCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    answers_list = [ans.dict() for ans in personality_in.answers]
    scores = personality_service.calculate_ocean_scores(answers_list)

    existing = db.query(models.Personality).filter(
        models.Personality.user_id == current_user.id
    ).first()

    if existing:
        existing.answers = answers_list
        existing.openness = scores["openness"]
        existing.conscientiousness = scores["conscientiousness"]
        existing.extraversion = scores["extraversion"]
        existing.agreeableness = scores["agreeableness"]
        existing.neuroticism = scores["neuroticism"]
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        personality = models.Personality(
            user_id=current_user.id,
            answers=answers_list,
            openness=scores["openness"],
            conscientiousness=scores["conscientiousness"],
            extraversion=scores["extraversion"],
            agreeableness=scores["agreeableness"],
            neuroticism=scores["neuroticism"]
        )
        db.add(personality)
        db.commit()
        db.refresh(personality)
        return personality


@router.get("/", response_model=schemas.PersonalityOut)
def get_personality(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    personality = db.query(models.Personality).filter(
        models.Personality.user_id == current_user.id
    ).first()
    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")
    return personality