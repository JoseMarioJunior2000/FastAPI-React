from sqlalchemy.ext.asyncio import AsyncSession
from src.models.institution import Institution
from sqlalchemy import select, update
from src.schemas.user_schemas import UserCreateModel, UserModel, UserProfileChange
from src.schemas.institution_schemas import InstitutionCreateModel
from src.utils.password_verify import generate_password_hash
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import HTTPException
from fastapi import status
from src.utils.prevent_deletion import can_delete_user
from typing import Optional

class InstitutionService:
    async def get_institution_by_email(self, email: str, session: AsyncSession):
        statement = select(Institution).where(Institution.email == email)
        result = await session.execute(statement=statement)
        institution = result.scalars().first()
        return institution
    
    async def institution_exist(self, email: str, session: AsyncSession):
        institution = await self.get_institution_by_email(email=email, session=session)
        return True if institution is not None else False
    
    async def create_institution(self, institution_data: InstitutionCreateModel, session: AsyncSession):
        institution_data = institution_data.model_dump()
        new_institution = Institution(**institution_data)
        session.add(new_institution)
        await session.commit()
        return new_institution
    
    async def get_all_institutions(self, session: AsyncSession, limit: int = 50, offset: int = 0):
        statement = (
            select(Institution)
            .order_by(Institution.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(statement)
        return result.scalars().all()
    
    """
    async def get_user_for_update(self, user_uid: str, session: AsyncSession) -> Optional[User]:
        statement = (select(User).where(User.id == user_uid).with_for_update())
        result = await session.execute(statement=statement)
        return result.scalars().first() 
    
    async def get_user(self, user_uid: str, session: AsyncSession):
        statement = select(User).where(User.id == user_uid)
        result = await session.execute(statement=statement)
        user = result.scalars().first()

        return user if user is not None else None
    
    async def update_profile(self, current_user: User, payload: UserProfileChange, session: AsyncSession) -> UserModel:
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not data:
            return UserModel.model_validate(current_user, from_attributes=True)
        statement = update(User).where(User.id == current_user.id).values(**data).returning(User)
        result = await session.execute(statement=statement)
        updated_entity = result.scalar_one()
        await session.commit()
        return UserModel.model_validate(updated_entity, from_attributes=True)
    
    async def delete_user(self, current_user: User, user_uid: str, session: AsyncSession):
        user_to_deleted = await self.get_user_for_update(user_uid=user_uid, session=session)
        if not user_to_deleted:
            return False
        can_delete_user(current_user=current_user, user_to_deleted=user_to_deleted)
        try:
            await session.delete(user_to_deleted)
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "User cannot be deleted due to related resources",
                    "error_code": "user_delete_conflict",
                },
            )
    """