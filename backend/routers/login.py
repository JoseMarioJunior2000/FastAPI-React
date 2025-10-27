from utils.token_auth import create_access_token, decode_token, serialize_roles
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

REFRESH_TOKEN_EXPIRY = 2

login_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
user_service = UserService()

@login_router.post('/login')
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_db)):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email=email, session=session)
    if user is not None:
        password_valid = verify_password(password=password, hash=user.password_hash)
        if password_valid:
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
            return JSONResponse(
                content={
                    'message': 'Login successful', 
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'email': user.email,
                        'uid': str(user.id)
                    }
                }
            )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid Email or Password"
    )
