from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from .. import schemas, models
from ..api import deps
from ..services import analytics

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/", response_model=List[schemas.InsightOut])
def get_insights(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
):
    """
    Получить список инсайтов пользователя (по умолчанию последние 50).
    Можно отфильтровать только непрочитанные (unread_only=true).
    """
    query = db.query(models.Insight).filter(models.Insight.user_id == current_user.id)
    if unread_only:
        query = query.filter(models.Insight.is_read == False)
    insights = query.order_by(models.Insight.created_at.desc()).offset(skip).limit(limit).all()
    return insights


@router.post("/generate", response_model=List[schemas.InsightOut])
def generate_insights(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Принудительно сгенерировать новые инсайты (обычно вызывается фоном,
    но можно и вручную для теста).
    """
    new = analytics.generate_all_insights(db, current_user.id)
    return new


@router.patch("/{insight_id}/read", response_model=schemas.InsightOut)
def mark_insight_read(
    insight_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Отметить инсайт как прочитанный.
    """
    insight = db.query(models.Insight).filter(
        models.Insight.id == insight_id,
        models.Insight.user_id == current_user.id
    ).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    insight.is_read = True
    db.commit()
    db.refresh(insight)
    return insight


@router.delete("/{insight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_insight(
    insight_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Удалить инсайт (если он больше не нужен).
    """
    insight = db.query(models.Insight).filter(
        models.Insight.id == insight_id,
        models.Insight.user_id == current_user.id
    ).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    db.delete(insight)
    db.commit()
    return None