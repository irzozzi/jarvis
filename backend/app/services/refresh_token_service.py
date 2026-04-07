from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
import secrets
from .. import models

def create_refresh_token(db: Session, user_id: UUID, expires_days: int = 30) -> str:
    token_str = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=expires_days)
    refresh_token = models.RefreshToken(
        user_id=user_id,
        token=token_str,
        expires_at=expires_at,
        revoked=False
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return token_str

def get_refresh_token(db: Session, token_str: str):
    return db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token_str,
        models.RefreshToken.revoked == False,
        models.RefreshToken.expires_at > datetime.utcnow()
    ).first()

def revoke_refresh_token(db: Session, token_str: str) -> None:
    token = db.query(models.RefreshToken).filter(models.RefreshToken.token == token_str).first()
    if token:
        token.revoked = True
        db.commit()