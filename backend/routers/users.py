from utils.token_auth import create_access_token, decode_token
from fastapi import APIRouter, Depends, status
from schemas.user_schemas import UserCreateModel, UserModel, UserLoginModel, User
from services.user_service import UserService
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from core.config import get_settings
from utils.email_verify import verify_email
from utils.password_verify import validate_password_strength, verify_password
from datetime import timedelta
from fastapi.responses import JSONResponse
from core.dependencies import AccessTokenBearer
from typing import List
from services.evolution import fetch_instances

REFRESH_TOKEN_EXPIRY = 2

home_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
user_service = UserService()

@home_router.get('/users')
async def get_all_users(
    session: AsyncSession = Depends(get_db),
    token_data: dict = Depends(AccessTokenBearer())  # <- garante blacklist
):
    users = await fetch_instances()
    return users