from fastapi.security import HTTPBearer
from fastapi import Request, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from services.user_service import UserService
from utils.token_auth import decode_token
from db.redis import token_in_blocklist
from models.user import User

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