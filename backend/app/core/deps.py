"""
Dependencies for FastAPI endpoints
"""
from typing import Generator, Optional, List, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.database import SessionLocal, async_session
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ==================== SYNC DB DEPENDENCY ====================
def get_db() -> Generator:
    """Get synchronous database session (for sync endpoints)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== ASYNC DB DEPENDENCY ====================
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get asynchronous database session (for async endpoints)"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# ==================== CURRENT USER SYNC ====================
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user (sync version for sync endpoints)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[security.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    if not user.attivo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


# ==================== CURRENT USER ASYNC ====================
async def get_current_user_async(
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user (async version for async endpoints)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[security.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).filter(User.id == int(user_id)))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    
    if not user.attivo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.attivo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_user_with_role(required_role: str):
    """Get current user with specific role"""
    def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.ruolo != required_role and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{required_role}' required"
            )
        return current_user
    return role_checker


def require_roles(allowed_roles: List[UserRole]):
    """
    Dependency to check if user has one of the allowed roles.
    
    Usage:
        @router.get("/", dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))])
    
    Or as parameter:
        def my_endpoint(current_user: User = Depends(require_roles([UserRole.ADMIN]))):
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.ruolo not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    return role_checker
