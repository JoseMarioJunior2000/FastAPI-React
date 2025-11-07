from fastapi import APIRouter, Depends, status
from src.schemas.user_schemas import UserCreateModel, UserModel
from src.services.user_service import UserService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from src.core.config import get_settings
from src.utils.email_verify import verify_email
from src.utils.password_verify import validate_password_strength

signup_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
user_service = UserService()

@signup_router.post('/signup', response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateModel, session: AsyncSession = Depends(get_db)):
    """
    Create user account using email, username, first_name, last_name
    params:
        user_data: UserCreateModel
    """
    email = verify_email(user_data.email)
    is_valid_password = validate_password_strength(user_data.password)
    if not is_valid_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=(
                "Password must contain at least 8 characters, including uppercase, lowercase, number, and special symbol."
            )
        )
    user_exists = await user_service.user_exist(email=email, session=session)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with email alredy exists")
    new_user = await user_service.create_user(user_data=user_data, session=session)
    return new_user