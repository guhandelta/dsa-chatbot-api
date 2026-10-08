# Password hashing + JWT issuance/verification + the get_current_user dependency.
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_session
from app.db.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Resolves the Bearer token to a User row, or raises 401."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = jwt.decode(
            credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id: str | None = payload.get("sub")
    except jwt.PyJWTError:
        raise unauthorized

    if user_id is None:
        raise unauthorized

    user = await session.get(User, user_id)
    if user is None:
        raise unauthorized
    return user


def _sync_admin_role(user: User) -> None:
    """Emails listed in ADMIN_EMAILS are always admins (bootstraps the first
    admin, since there is no one to promote them)."""
    if user.email.lower() in settings.admin_email_list and user.role != "admin":
        user.role = "admin"


async def require_instructor(current_user: User = Depends(get_current_user)) -> User:
    """Training section: instructors and admins only."""
    if current_user.role not in ("instructor", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Training access is limited to instructors and admins.",
        )
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Role management: admins only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_user
