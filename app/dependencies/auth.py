from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.token import verify_token
from app.core.database import get_db
from app.models.user import User

def get_current_user(
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    payload = verify_token(access_token)
    user_id = payload.get("sub")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not db_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    return db_user