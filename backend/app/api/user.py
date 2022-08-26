from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status
from typing import Any, Dict

from app.api.dependency import get_db, auth_user
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud import user as crud_user
from app.schemas.user import UserBase, UserLogin, UserInfo
from app.security import create_access_token, get_hash


router = APIRouter()


@router.post("/register", response_model=UserBase, response_model_exclude_unset=True)
async def register(
        cred: UserLogin,
        db: AsyncSession = Depends(get_db)
) -> UserBase:
    """
    ## API Register

    Registers a new user into the system by storing their email &
    master password (hash) in the database

    Master password is first hashed once at the API then again in the
    db using pgcrypto.

    """

    password_hash = get_hash(cred.master_pwd)  # hash once in the server
    # try:  # hash of the hash stored in db
    user = await crud_user.get_by_email(db, cred.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email already exists"
        )
    result: UserBase = await crud_user.create(db, cred.email, password_hash)
    return result


@router.post("/login", response_model=UserBase, response_model_exclude_unset=True)
async def login(
        cred: UserLogin,
        response: Response,
        db: AsyncSession = Depends(get_db)
) -> UserBase:
    """
    ## API Login

    post user email & password to log in.

    Master password is hashed once in the server using bcrypt then
    hashed and checked at db using pgcrypto extension.

    generates an access token upon login and sets response cookie

    """
    user_email = cred.email
    user_password = cred.master_pwd

    password_hash = get_hash(user_password)

    # check if user with this email exists
    if (await crud_user.get_by_email(db, user_email)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="email not found"
        )

    # authentication check
    if (user := await crud_user.get(db, user_email, password_hash)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="invalid email/password"
        )

    # generate payload and access token
    time_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"user_info": user.dict(exclude_unset=True)}

    access_token = create_access_token(data=payload, expires_delta=time_expires)

    # set cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=time_expires.total_seconds(),
        expires=time_expires.total_seconds(),
        samesite="lax",
        secure=False,
    )
    return user


@router.get("/user", response_model=UserInfo)
async def get_user_info(
        user: UserBase = Depends(auth_user),
) -> UserInfo:
    """
    ## API Get User

    Retrieve the currently logged-in user information

    """
    return UserInfo(**user.dict(exclude={"master_pwd"}))


@router.delete("/user")
async def delete_user(
        user: UserBase = Depends(auth_user),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    deletes the currently logged in user

    """
    return await crud_user.delete(db, user.uid)
