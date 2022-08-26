from pydantic import EmailStr
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import CRUDBase
from app.models import User
from app.schemas.user import UserBase


class CRUDUsers(CRUDBase[UserBase]):
    schema = UserBase

    async def get_by_id(self, db: AsyncSession, uid: str) -> UserBase:
        """
        ### used internally via API dependencies

        Fetches user information from the `User` table by
        querying by their id (uuid primary key)

        """
        return self._process_model(
            (await db.execute(select(User).where(User.uid == uid))).scalars().first()
        )

    async def get_by_email(self, db: AsyncSession, email: EmailStr) -> UserBase:

        """
        ### Only used internally via API dependencies

        Fetches user information from the `User` table by querying
        by their registered email address.

        """
        return self._process_model(
            (await db.execute(select(User).where(User.email == email))).scalars().first()
        )

    async def get(self, db: AsyncSession, email: str, password_hash: str) -> UserBase:

        """
        Fetches user information from the `User` table by querying
        against email address and verifying the password.

        python bcrypt module is used to verify the supplied password
        with the stored hash.

        """
        return self._process_model(
            (await db.execute(select(User).where(User.email == email, User.master_pwd == password_hash)))
            .scalars().first()
        )

    async def create(
        self,
        db: AsyncSession,
        email: str, 
        password_hash: str
    ) -> UserBase:

        """
        Inserts a newly registered user's email and their hashed
        master password in the `Users` table.

        Uses `crypt()` function with salt to generate and store 
        hashes of passwords.
        `Blowfish (bf)` hashing with 8 iterations is used.

        """
        model = User(email=email, master_pwd=password_hash)

        db.add(model)
        await db.commit()
        await db.refresh(model)

        return self.schema(uid=str(model.uid), email=email)

    async def delete(self, db: AsyncSession, uid: str) -> str:

        """
        Deletes an existing user by `uid`
        Cascade deletes all passwords associated with it.

        """
        await db.execute(delete(User).where(User.uid == uid))
        await db.commit()
        return uid

    def _process_model(self, model: User) -> UserBase:
        return self.schema(uid=str(model.uid), email=model.email) if model else None


user = CRUDUsers(UserBase)
