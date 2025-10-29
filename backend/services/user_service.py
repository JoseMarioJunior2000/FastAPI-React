from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from sqlalchemy import select, update
from schemas.user_schemas import UserCreateModel, UserModel, UserProfileChange
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
    
    async def update_profile(self, current_user: User, payload: UserProfileChange, session: AsyncSession) -> UserModel:
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            return UserModel.model_validate(current_user, from_attributes=True)
        statement = update(User).where(User.id == current_user.id).values(**data).returning(User)
        result = await session.execute(statement=statement)
        updated_entity = result.scalar_one()
        await session.commit()
        return UserModel.model_validate(updated_entity, from_attributes=True)