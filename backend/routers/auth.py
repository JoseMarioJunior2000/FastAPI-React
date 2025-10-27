from utils.token_auth import create_access_token, decode_token
from fastapi import APIRouter, Depends, status
from schemas.user_schemas import UserCreateModel, UserModel, UserLoginModel
from services.user_service import UserService
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from core.config import get_settings
from utils.email_verify import verify_email
from utils.password_verify import validate_password_strength, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse
from core.dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from datetime import datetime
from db.redis import add_jti_to_blocklist

auth_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
user_service = UserService()
role_checker = RoleChecker(['admin', 'user'])

@auth_router.get('/refresh')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp) > datetime.utcnow():
        new_access_token = create_access_token(
            user_data=token_details['user']
        )
        return JSONResponse(content={
            'access_token': new_access_token
        })
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid or expired token')

@auth_router.get('/logout')
async def revooke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details.get("jti")
    if not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token (missing jti/exp)")
    await add_jti_to_blocklist(jti=jti)
    return JSONResponse({"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK)

@auth_router.get("/me", response_model=UserModel)
async def get_current_user(user = Depends(get_current_user), _: bool = Depends(role_checker)):
    return user