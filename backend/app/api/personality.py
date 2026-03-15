from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models
from ..api import deps
from ..services import personality as personality_service

router = APIRouter(prefix="/personality", tags=["personality"])


@router.post("/", response_model=schemas.PersonalityOut)
def create_or_update_personality(
    personality_in: schemas.PersonalityCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Принимает ответы на вопросы, вычисляет психотип и сохраняет результат.
    Если запись уже существует, обновляет ее.
    """

    ptype = personality_service.calculate_personality_type(personality_in.answers)

    existing = db.query(models.Personality).filter(
        models.Personality.user_id == current_user.id
    ).first()

    if existing:
        existing.type = ptype
        existing.answers = [ans.dict() for ans in personality_in.answers]
        db.commit()
        db.refresh(existing)
        return existing
    else:
        personality = models.Personality(
            user_id=current_user.id,
            type=ptype,
            answers=[ans.dict() for ans in personality_in.answers]
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
    """
    Возвращает текущий психотип пользователя.
    """
    personality = db.query(models.Personality).filter(
        models.Personality.user_id == current_user.id
    ).first()
    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")
    return personality    

