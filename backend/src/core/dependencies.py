from fastapi.security import HTTPBearer
from fastapi import Request, status, Depends, Query
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.services.user_service import UserService
from src.utils.token_auth import decode_token
from src.db.redis import token_in_blocklist, redis_client
from src.models.user import User
from src.services.evolution_service import EvolutionService
from src.core.config import get_settings
import time
from redis.asyncio import Redis
from fastapi.responses import JSONResponse
from uuid import UUID
from src.db.redis import redis_client
from src.core.config import get_settings
from src.core.middleware import RateLimiter
from src.core.erros import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    AccountNotVerified,
    InvalidJTI,
    UserNotFound
)

rate_limiter = RateLimiter(redis_client=redis_client)
user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Dict[str, Any]:
        creds: HTTPAuthorizationCredentials = await super().__call__(request)
        token = creds.credentials

        token_data = decode_token(token=token)
        if not isinstance(token_data, dict):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        jti = token_data.get("jti")
        if not jti:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token (missing jti)")

        if await token_in_blocklist(jti=jti):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data: Dict[str, Any]) -> None:
        raise NotImplementedError("Override in subclass")

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: Dict[str, Any]) -> None:
        if token_data.get("refresh") is True:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please, provide an access token")

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: Dict[str, Any]) -> None:
        if token_data.get("refresh") is not True:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please, provide a refresh token")
        
async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_db)):
    user_email = token_details['user']['email']
    user = await user_service.get_user_by_email(email=user_email, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

def get_evolution_service() -> EvolutionService:
    settings = get_settings()
    return EvolutionService(
        server_url=settings.EVO_SERVER_URL,
        api_key=settings.EVO_API_KEY,
        timeout=30.0,
    )

async def ensure_instance_exists(
    instance: str = Query(..., description="Nome da instância"),
    evo: EvolutionService = Depends(EvolutionService),
) -> str:
    instances = await evo.fetch_instances()
    names = {i.name for i in instances if i.name}
    if instance not in names:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instância '{instance}' não encontrada"
        )
    return instance

async def rate_limit_dep(
    request: Request,
    token_data: dict = Depends(AccessTokenBearer()),
):
    user = token_data.get("user") or {}
    user_uid = user.get("user_uid")
    if not user_uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token")
    key = f"rl:user:{user_uid}"
    allowed = await rate_limiter.allow_request(key)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Limite de requisições excedido")