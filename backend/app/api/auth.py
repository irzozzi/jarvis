from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from .. import models, schemas
from ..core.database import SessionLocal
from ..core.security import (
    verify_password, get_password_hash, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
)
from ..services.refresh_token_service import create_refresh_token, get_refresh_token, revoke_refresh_token
from ..services.email_service import send_verification_email, send_password_reset_email
import secrets

from ..api import deps

router = APIRouter(prefix="/auth", tags=["authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.UserOut)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user_data.password)
    verification_token = secrets.token_urlsafe(32)
    new_user = models.User(
        email=user_data.email,
        hashed_password=hashed_password,
        verification_token=verification_token,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    send_verification_email(new_user.email, verification_token)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(db, user.id, REFRESH_TOKEN_EXPIRE_DAYS)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/login-json", response_model=schemas.Token)
def login_json(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(db, user.id, REFRESH_TOKEN_EXPIRE_DAYS)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(request: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    token_record = get_refresh_token(db, request.refresh_token)
    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    revoke_refresh_token(db, request.refresh_token)
    access_token = create_access_token(data={"sub": str(token_record.user_id)})
    new_refresh_token = create_refresh_token(db, token_record.user_id, REFRESH_TOKEN_EXPIRE_DAYS)
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    if user.is_verified:
        return {"message": "Email already verified"}
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return {"message": "If your email is registered, you will receive a reset link"}
    token = secrets.token_urlsafe(32)
    user.reset_password_token = token
    user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    send_password_reset_email(email, token)
    return {"message": "Password reset link sent to your email"}

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.reset_password_token == token,
        models.User.reset_password_expires > datetime.utcnow()
    ).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.hashed_password = get_password_hash(new_password)
    user.reset_password_token = None
    user.reset_password_expires = None
    db.commit()
    return {"message": "Password reset successfully"}

@router.post("/change-password", response_model=dict)
def change_password(
    data: schemas.PasswordChange = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    # Перезагружаем пользователя в текущей сессии
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid old password")
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if data.old_password == data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from old password")

    user.hashed_password = get_password_hash(data.new_password)
    db.query(models.RefreshToken).filter(models.RefreshToken.user_id == user.id).update({"revoked": True})
    db.commit()
    return {"message": "Password changed successfully"}