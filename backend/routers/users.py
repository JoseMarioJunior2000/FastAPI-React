from utils.token_auth import create_access_token, decode_token
from fastapi import APIRouter, Depends, status, Query, Body
from schemas.user_schemas import UserModel, UserProfileChange
from services.user_service import UserService
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from core.config import get_settings
from utils.email_verify import verify_email
from utils.password_verify import validate_password_strength, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse
from core.dependencies import AccessTokenBearer, get_current_user, RoleChecker
from typing import List

user_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
user_service = UserService()
role_checker = RoleChecker(['admin'])

@user_router.get('/users',  response_model=list[UserModel], status_code=status.HTTP_200_OK, dependencies=[Depends(role_checker)],)
async def get_all_users(
    session: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    try:
        users = await user_service.get_all_users(session=session, limit=limit, offset=offset)
        return users
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao obter usuários")
    
@user_router.patch('/profile', response_model=UserModel, status_code=status.HTTP_200_OK)
async def change_user_profile(
    payload: UserProfileChange = Body(...),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    service: UserService = Depends(UserService),
):
    updated = await service.update_profile(current_user=current_user, payload=payload, session=session)
    return updated
    