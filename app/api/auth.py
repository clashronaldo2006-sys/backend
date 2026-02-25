from fastapi import APIRouter, Depends, HTTPException, status
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db, redis_client
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenPair
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post('/login', response_model=TokenPair)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    await redis_client.setex(f'refresh:{refresh_token}', 60 * 60 * 24 * 7, str(user.id))
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post('/refresh', response_model=TokenPair)
async def refresh_tokens(payload: RefreshRequest) -> TokenPair:
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get('type') != 'refresh':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token type')
        subject = decoded.get('sub')
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token') from exc

    exists = await redis_client.get(f'refresh:{payload.refresh_token}')
    if exists is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token revoked or expired')

    await redis_client.delete(f'refresh:{payload.refresh_token}')
    access_token = create_access_token(subject)
    new_refresh = create_refresh_token(subject)
    await redis_client.setex(f'refresh:{new_refresh}', 60 * 60 * 24 * 7, subject)
    return TokenPair(access_token=access_token, refresh_token=new_refresh)
