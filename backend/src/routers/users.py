from src.utils.token_auth import create_access_token, decode_token
from fastapi import APIRouter, Depends, status, Query, Body, Response, Request
from src.schemas.user_schemas import UserModel, UserProfileChange
from src.services.user_service import UserService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from src.core.config import get_settings
from src.utils.email_verify import verify_email
from src.utils.password_verify import validate_password_strength, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse
from uuid import UUID
from src.models.user import User
from src.utils.prevent_deletion import prevent_self_deletion
from src.core.dependencies import rate_limit_dep, get_current_user, RoleChecker
from src.core.erros import UserNotFound
from src.services.cache_service import CacheService
from src.db.redis import redis_client

user_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
user_service = UserService()
role_checker = RoleChecker(['admin'])
cache_service = CacheService(redis_client=redis_client)

@user_router.get('/users',  response_model=list[UserModel], status_code=status.HTTP_200_OK, dependencies=[Depends(role_checker), Depends(rate_limit_dep)],)
@cache_service.cached(timeout=60, key_prefix='users')
async def get_all_users(
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    try:
        users = await user_service.get_all_users(current_user=current_user, session=session, limit=limit, offset=offset)
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

@user_router.delete(
    "/users/{user_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_checker)]
)
async def delete_user(
    user_uid: UUID, 
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Response:
    prevent_self_deletion(current_user=current_user, user_uid=user_uid)
    user_to_delete = await user_service.delete_user(current_user=current_user, user_uid=user_uid, session=session)
    if not user_to_delete:
        raise UserNotFound()
    return Response(status_code=status.HTTP_204_NO_CONTENT)