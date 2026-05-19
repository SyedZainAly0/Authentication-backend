from alembic.op import f
from fastapi import APIRouter, Depends, HTTPException, Response, Request, Cookie, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserLogout
from app.models.user import User
from app.utils.hashing import hash_password, verify_password
from app.utils.token import create_access_token, create_refresh_token, verify_refresh_token
from app.dependencies.auth import get_current_user
import os
from app.utils.response import success_response, error_response
from app.email.email_token import create_email_verification_token, verify_email_verification_token
from app.email.email_template import send_verification_email
from fastapi.responses import RedirectResponse



router = APIRouter(prefix="/auth", tags=["Auth"])

# ── Register ──────────────────────────────────────────────
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password),
        is_active=False
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    token = create_email_verification_token(new_user.email)

    send_verification_email(new_user.email, token)

    return success_response(
        message="Registration successful. Please verify your email.",
        data={
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username
        }
    )

# ── Login ─────────────────────────────────────────────────
@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    if not db_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email first")

    token_data = {
        "sub": str(db_user.id),
        "username": db_user.username,
        "is_active": db_user.is_active
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=30 * 60        
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60 
    )

    return success_response(
        message="Login successful",
        data={
            "id": db_user.id,
            "email": db_user.email,
            "username": db_user.username,
            "is_active": db_user.is_active,
        }
    )

@router.post("/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):

    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    user_id = verify_refresh_token(token)

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    token_data = {
        "sub": str(db_user.id),
        "username": db_user.username,
        "is_active": db_user.is_active
    }
    
    new_access_token = create_access_token(token_data)
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        max_age=30 * 60        
    )

    return success_response(
        message="Token refreshed successfully",
        data={
            "id": db_user.id,
            "username": db_user.username,
        }
    )

@router.post("/logout")
def logout(
    user: UserLogout, response: Response, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()
    db_id = db.query(User.id).filter(User.id == user.id).first()
    if not db_user or not db_id:
        return error_response(
            message="User not found"
        )
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return success_response(
        message="User logged out successfully",
        data={
            "id": db_user.id,
            "username": db_user.username,
            "is_active": False,
        }
    )
   
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):

    email = verify_email_verification_token(token)

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    db.commit()

    return success_response(
        message="Email verified successfully"
    )
    