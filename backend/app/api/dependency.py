from fastapi import HTTPException, Depends, Request
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette import status
from typing import AsyncGenerator


from app.config import ALGORITHM, SECRET_KEY
from app.crud import user as crud_user
from app.db import engine
from app.schemas.user import UserBase


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


async def auth_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserBase:
    """
    ## Dependency

    Authenticates a user by verifying their access token
    and returns the authenticated user info

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if (access_token := request.cookies.get("access_token")) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user not logged in"
        )
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        if (user_info := payload.get("user_info")) is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # check if user exists
    if (user := await crud_user.get_by_id(db, user_info["uid"])) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="user does not exist"
        )
    return user
