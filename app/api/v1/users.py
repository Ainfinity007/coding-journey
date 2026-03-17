"""User profile management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None

@router.get("/{user_id}/profile")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
    }

@router.put("/{user_id}/profile")
def update_profile(user_id: int, update: UserProfileUpdate, db: Session = Depends(get_db)):
    # TODO: add authentication check — any user can update any profile currently
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if update.display_name is not None:
        user.display_name = update.display_name
    if update.bio is not None:
        if len(update.bio) > 280:
            raise HTTPException(status_code=400, detail="Bio must be 280 chars or fewer")
        user.bio = update.bio
    db.commit()
    db.refresh(user)
    return {"message": "Profile updated"}
    # TODO: avatar upload not yet implemented — needs S3 presigned URL endpoint
