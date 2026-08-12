from datetime import datetime, timedelta
import re
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.database.database import get_db
from app.models.farm import Farm
from app.models.organization import Organization, OrganizationMember
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole
from app.schemas.user import (
    ForgotPasswordRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter()

REFRESH_TOKEN_LIFETIME = timedelta(days=30)


def _new_refresh_token(user_id: int) -> tuple[RefreshToken, str]:
    value = secrets.token_urlsafe(32)
    now = datetime.utcnow()
    return (
        RefreshToken(
            user_id=user_id,
            token=value,
            expires_at=now + REFRESH_TOKEN_LIFETIME,
            created_at=now,
        ),
        value,
    )


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Public registration must not allow callers to grant themselves ADMIN.
    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=UserRole.FARM_MANAGER,
    )
    db.add(user)
    db.flush()

    slug_base = re.sub(r"[^a-z0-9]+", "-", user_in.farm_name.lower()).strip("-")
    slug_base = slug_base or "farm"
    slug = slug_base
    if db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{slug_base}-{secrets.token_hex(3)}"

    organization = Organization(
        name=user_in.farm_name,
        slug=slug,
        owner_id=user.id,
        created_at=datetime.utcnow(),
    )
    db.add(organization)
    db.flush()
    db.add_all([
        OrganizationMember(
            organization_id=organization.id,
            user_id=user.id,
            role="OWNER",
            joined_at=datetime.utcnow(),
        ),
        Farm(
            name=user_in.farm_name,
            owner_id=user.id,
            organization_id=organization.id,
        ),
    ])
    user.current_organization_id = organization.id
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role,
            "organization_id": user.current_organization_id,
        }
    )
    refresh_record, refresh_value = _new_refresh_token(user.id)
    db.add(refresh_record)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_value,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).update(
        {"is_revoked": True}
    )
    db.commit()
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        # The email delivery integration should send the reset URL. Returning it
        # here would reveal whether an account exists.

    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.password_reset_token == request.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token expired")

    user.password_hash = get_password_hash(request.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).update(
        {"is_revoked": True}
    )
    db.commit()

    return {
        "message": "Password reset successful. You can now login with your new password."
    }


@router.post("/send-verification-email")
def send_verification_email(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.email_verified:
        return {"message": "Email already verified"}

    token = secrets.token_urlsafe(32)
    current_user.email_verification_token = token
    current_user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
    db.commit()

    return {
        "message": "Verification email sent",
        "verification_url": f"/verify-email?token={token}",
    }


@router.post("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email_verification_token == token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    if (
        user.email_verification_expires
        and user.email_verification_expires < datetime.utcnow()
    ):
        raise HTTPException(status_code=400, detail="Verification token expired")

    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None
    db.commit()
    return {"message": "Email verified successfully"}


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_profile(
    name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if name:
        current_user.name = name
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/avatar")
def upload_avatar(
    avatar_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.avatar_url = avatar_url
    db.commit()
    return {"message": "Avatar updated", "avatar_url": avatar_url}


@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 8 characters",
        )

    current_user.password_hash = get_password_hash(new_password)
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).update(
        {"is_revoked": True}
    )
    db.commit()
    return {"message": "Password changed successfully"}


@router.post("/refresh-token", response_model=Token)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_record = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token,
        RefreshToken.is_revoked.is_(False),
        RefreshToken.expires_at > datetime.utcnow(),
    ).first()

    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    token_record.is_revoked = True
    new_refresh_record, new_refresh_value = _new_refresh_token(user.id)
    db.add(new_refresh_record)
    db.commit()

    return {
        "access_token": create_access_token(
            {
                "sub": str(user.id),
                "role": user.role,
                "organization_id": user.current_organization_id,
            }
        ),
        "refresh_token": new_refresh_value,
        "token_type": "bearer",
    }


@router.post("/logout-all")
def logout_all_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).update(
        {"is_revoked": True}
    )
    db.commit()
    return {"message": "All sessions logged out"}
