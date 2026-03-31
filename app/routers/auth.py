"""
MHRS SaaS — Authentication Router
Handles user registration, email verification, and login.
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    LoginRequest,
    TokenResponse,
    UserOut,
)
from security.auth import hash_password, verify_password, create_access_token, get_current_user
from security.encryption_utils import encrypt_field
from app.utils.email_sender import send_verification_code, send_password_reset_code
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new patient account",
    description=(
        "Creates a new user account. TC number is encrypted before storage. "
        "A 6-digit verification code is sent via email (async via RabbitMQ)."
    ),
)
def register(payload: RegisterRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Check duplicates
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # 2. Encrypt TC number (sensitive PII)
    encrypted_tc = encrypt_field(payload.tc_no).encode('utf-8')
    if db.query(User).filter(User.tc_no_encrypted == encrypted_tc).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this TC number already exists.",
        )

    # 3. Generate verification code
    code = User.generate_verification_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    # 4. Create user record
    user = User(
        tc_no_encrypted=encrypted_tc,
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password).encode('utf-8'),
        verification_code=code,
        verification_expires_at=expires,
        is_verified=True,
        role="patient",
    )
    
    # Geliştirici Hilesi (Terminal Log)
    print(f"!!! DİKKAT DOĞRULAMA KODU: {payload.email} için kod: {code} !!!")
    db.add(user)
    db.commit()
    db.refresh(user)

    # 5. E-posta doğrulama kodunu asenkron olarak arka planda gönder
    background_tasks.add_task(send_verification_code, user.email, str(code))

    return RegisterResponse(
        message="Registration successful. Please check your email for the verification code.",
        email=payload.email,
    )


@router.post(
    "/verify",
    summary="Verify email using 6-digit code",
)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    user: User = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email is already verified.")
    if user.verification_code != payload.code:
        raise HTTPException(status_code=400, detail="Invalid verification code.")
    if user.verification_expires_at and user.verification_expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Verification code has expired. Please register again.")

    user.is_verified = True
    user.verification_code = None
    user.verification_expires_at = None
    db.commit()

    return {"message": "Email verified successfully. You can now log in."}


@router.post(
    "/forgot-password",
    summary="Request a password reset code",
)
def forgot_password(
    payload: ForgotPasswordRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    user: User = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Avoid leaking user existence, just return success
        return {"message": "Şifre sıfırlama talebiniz alındı. Eğer kayıtlıysanız size bir e-posta göndereceğiz."}
    
    code = User.generate_verification_code()
    user.reset_code = code
    db.commit()
    
    background_tasks.add_task(send_password_reset_code, user.email, str(code))
    
    return {"message": "Şifre sıfırlama talebiniz alındı. Eğer kayıtlıysanız size bir e-posta göndereceğiz."}


@router.post(
    "/reset-password",
    summary="Verify reset code and set new password",
)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user: User = db.query(User).filter(User.email == payload.email).first()
    
    if not user or user.reset_code != payload.reset_code:
        raise HTTPException(status_code=400, detail="Geçersiz e-posta veya sıfırlama kodu.")
        
    user.hashed_password = hash_password(payload.new_password).encode('utf-8')
    user.reset_code = None
    db.commit()
    
    return {"message": "Şifreniz başarıyla güncellenmiştir. Artık yeni şifrenizle giriş yapabilirsiniz."}


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get JWT access token",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user: User = db.query(User).filter(
        User.email == payload.email,
        User.is_active == True,
    ).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    # if not user.is_verified:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Please verify your email before logging in.",
    #     )

    token = create_access_token(data={"sub": user.email, "role": user.role, "uid": user.id})
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
