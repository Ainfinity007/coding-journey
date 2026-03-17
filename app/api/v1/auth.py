"""Authentication endpoints: login, logout, refresh."""
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.core.security import verify_password, create_access_token, create_refresh_token
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    # TODO: store refresh token in DB and set as HttpOnly cookie
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="strict")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
def refresh(refresh_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    # TODO: implement proper refresh token rotation
    # Currently does NOT rotate tokens — security gap
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    from app.core.security import decode_token
    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        new_access_token = create_access_token({"sub": user_id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}
