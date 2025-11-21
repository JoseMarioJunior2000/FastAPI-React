from src.utils.token_auth import create_access_token, decode_token
from fastapi import APIRouter, Depends, status, Request
from src.schemas.user_schemas import UserCreateModel, UserModel, UserLoginModel
from src.services.user_service import UserService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from src.core.config import get_settings
from src.utils.email_verify import verify_email
from src.utils.password_verify import validate_password_strength, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse
from src.core.dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from datetime import datetime
from src.db.redis import add_jti_to_blocklist
from src.core.erros import InvalidToken, InvalidJTI
from src.schemas.roles_schemas import Roles
from src.schemas.emails_schemas import EmailModel
from src.core.mail import mail, create_message
from src.services.cache_service import CacheService
from src.db.redis import redis_client

auth_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
user_service = UserService()
role_checker = RoleChecker(['admin', 'user'])
cache_service = CacheService(redis_client=redis_client)

@auth_router.get('auth/refresh')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp) > datetime.utcnow():
        new_access_token = create_access_token(
            user_data=token_details['user']
        )
        return JSONResponse(content={
            'access_token': new_access_token
        })
    raise InvalidToken()

@auth_router.get('/logout')
async def revooke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details.get("jti")
    if not jti:
        InvalidJTI()
    await add_jti_to_blocklist(jti=jti)
    return JSONResponse({"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK)

@auth_router.get("/me", response_model=UserModel)
@cache_service.cached(timeout=60, key_prefix='me')
async def get_current_user(request: Request, current_user = Depends(get_current_user), _: bool = Depends(role_checker)):
    return current_user

@auth_router.post("/send_mail")
async def send_mail_account(emails: EmailModel):
    recipients_list = emails.addresses 
    subject = emails.subject
    body_content = emails.body
    
    message = create_message(
        recipients=recipients_list,
        subject=subject,
        body=body_content
    )

    await mail.send_message(message=message)
    return {"message": "Email sent successfully"}