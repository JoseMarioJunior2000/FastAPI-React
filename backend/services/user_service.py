from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from sqlalchemy import select
from schemas.user_schemas import UserCreateModel
from utils.password_verify import generate_password_hash
from sqlalchemy.future import select

class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement=statement)
        user = result.scalars().first()
        return user
    
    async def user_exist(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email=email, session=session)
        return True if user is not None else False
    
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        password = user_data_dict.pop("password")

        new_user = User(
            **user_data_dict,
            password_hash=generate_password_hash(password)
        )

        session.add(new_user)
        await session.commit()
        return new_user
    
    async def get_all_users(self, session: AsyncSession, limit: int = 50, offset: int = 0):
        statement = (
            select(User)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(statement)
        return result.scalars().all()