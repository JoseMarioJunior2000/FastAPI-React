from src.utils.token_auth import create_access_token, decode_token, serialize_roles
from fastapi import APIRouter, Depends, status, Response
from src.schemas.user_schemas import UserCreateModel, UserModel, UserLoginModel, UserPublic
from src.services.user_service import UserService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from src.core.config import get_settings
from src.utils.email_verify import verify_email
from src.utils.password_verify import validate_password_strength, verify_password
from datetime import timedelta, datetime, timezone
from fastapi.responses import JSONResponse
from src.core.erros import InvalidCredentials

ACCESS_TTL_MINUTES = 10
REFRESH_TOKEN_EXPIRY = 15
COOKIE_NAME = "refresh_token"
COOKIE_PATH = "/api/v1/auth/refresh"  # caminho dedicado ao refresh
SECURE_COOKIES = False  # True em produção (HTTPS)
SAMESITE = "lax"        # "none" se front/back em domínios diferentes (exige SECURE=True)


login_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
user_service = UserService()

@login_router.post('/login')
async def login_users(login_data: UserLoginModel, response: Response, session: AsyncSession = Depends(get_db)):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email=email, session=session)

    if not user or not verify_password(password=password, hash=user.password_hash):
        raise InvalidCredentials()
    access_token = create_access_token(user_data={
        'email': user.email,
        'user_uid': str(user.id),
        'role': user.role
        }
    )

    refresh_token = create_access_token(user_data={
        'email': user.email,
        'user_uid': str(user.id)
        },
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
    )
    
    refresh_exp = timedelta(days=REFRESH_TOKEN_EXPIRY)
    response.set_cookie(
        key=COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite=SAMESITE,            # "none" se domínios distintos (e secure=True)
        max_age=int(refresh_exp.total_seconds()),
        expires=int((datetime.now(timezone.utc) + refresh_exp).timestamp()),
        path=COOKIE_PATH,             # restringe o envio do cookie
    )

    # Corpo JSON NÃO inclui o refresh
    access_exp = timedelta(minutes=ACCESS_TTL_MINUTES)
    return JSONResponse(
                content={
                    'message': 'Login successful', 
                    'access_token': access_token,
                    'expires_in': int(access_exp.total_seconds()),
                    'user': {
                        'email': user.email,
                        'uid': str(user.id)
                    }
                }
            )