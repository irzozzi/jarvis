from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from ..import schemas, models
from ..api import deps
from ..services.geocoding import reverse_geocode

router = APIRouter(prefix="/context", tags=["context"])

@router.post("/", response_model=schemas.ContextOut)
async def create_context(
    context_in: schemas.ContextCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Сохраняет контекстные данные (геолокация, активность) от пользователя.
    Если переданы координаты, пытается определить тип места через геокодинг.
    """

    timestamp = context_in.timestamp or datetime.utcnow()

    location_type = None
    if context_in.latitude and context_in.longitude:
        location_type = await reverse_geocode(context_in.latitude, context_in.longitude)

    context = models.Context(
        user_id=current_user.id,
        timestamp=timestamp,
        latitude=context_in.latitude,
        longitude=context_in.longitude,
        location_type=location_type,
        activity=context_in.activity,
        raw_data=context_in.raw_data
    )
    db.add(context)
    db.commit()
    db.refresh(context)
    return context