from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from uuid import UUID


class UserInfo(BaseModel):
    uid: UUID
    email: EmailStr

    @classmethod
    @validator("uid")
    def uuid_pk_validator(cls, v):
        if v.version is None:
            raise ValueError("Invalid UUID")
        return str(v)


class UserBase(UserInfo):
    uid: str
    master_pwd: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    master_pwd: str = Field(..., min_length=1)
