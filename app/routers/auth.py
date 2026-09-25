# /auth endpoints — register, login, and current-user lookup.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    _sync_admin_role,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.database import get_session
from app.db.models import User
from app.models.schemas import (
    AuthResponse,
    LanguagePreference,
    LoginRequest,
    RegisterRequest,
    UserOut,
)
from app.services.peppercorns import credit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, session: AsyncSession = Depends(get_session)):
    """Creates an account and grants the signup peppercorn bonus."""
    email = request.email.lower()
    existing = await session.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user = User(email=email, hashed_password=hash_password(request.password), peppercorns=0)
    _sync_admin_role(user)
    session.add(user)
    await session.flush()  # assigns user.id

    if settings.signup_bonus > 0:
        await credit(session, user.id, settings.signup_bonus, reason="signup_bonus")

    await session.commit()
    await session.refresh(user)

    return AuthResponse(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, session: AsyncSession = Depends(get_session)):
    email = request.email.lower()
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Same error for unknown email and bad password — don't leak which it was
    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    _sync_admin_role(user)   # ADMIN_EMAILS may have changed since registration
    await session.commit()
    await session.refresh(user)

    return AuthResponse(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user — used by the frontend to restore
    sessions and refresh the peppercorn balance."""
    return UserOut.model_validate(current_user)


@router.patch("/me/language", response_model=UserOut)
async def set_language(
    pref: LanguagePreference,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """The learner picks their language once; every track and mode respects it."""
    current_user.preferred_language = pref.language
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return UserOut.model_validate(current_user)
