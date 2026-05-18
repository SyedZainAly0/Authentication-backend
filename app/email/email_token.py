from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.core.config import settings

def create_email_verification_token(email: str):

    payload = {
        "sub": email,
        "type": "email_verification",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

# verification email function : 

def verify_email_verification_token(token: str):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired verification token"
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "email_verification":
            raise credentials_exception

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

        return email

    except JWTError:
        raise credentials_exception
