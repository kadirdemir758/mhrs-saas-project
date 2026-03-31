from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, UserProfileOut
from security.auth import get_current_user, hash_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserProfileOut, summary="Kullanıcının kendi profil bilgilerini getirir")
def get_user_profile(current_user: User = Depends(get_current_user)):
    # Geçici Çözüm: Şifreli TC çözme işlemi yerine sahte bir TC atıyoruz.
    current_user.tc_no = "123********"
    return current_user

@router.patch("/me", response_model=UserProfileOut, summary="Giriş yapan kullanıcının bilgilerini günceller")
def update_user_profile(
    payload: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if payload.name is not None:
        current_user.name = payload.name
        
    if payload.email is not None and payload.email != current_user.email:
        # Check if email is available
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu e-posta adresi sistemde zaten kayıtlı.")
        current_user.email = payload.email
        
    if payload.phone is not None:
        current_user.phone = payload.phone
        
    if payload.new_password:
        current_user.hashed_password = hash_password(payload.new_password)
        
    db.commit()
    db.refresh(current_user)
    
    return current_user
