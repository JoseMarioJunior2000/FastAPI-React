from fastapi import APIRouter, Depends, status, Query
from src.schemas.institution_schemas import InstitutionCreateModel, InstitutionModel, InstitutionUserCreateModel
from src.services.institution_service import InstitutionService
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from src.core.config import get_settings
from src.utils.email_verify import verify_email
from src.core.dependencies import AccessTokenBearer, get_current_user, RoleChecker, ensure_instance_exists
from src.core.dependencies import rate_limit_dep
from src.services.user_service import UserService
from src.schemas.user_schemas import UserModel, UserCreateModel
from src.utils.password_verify import validate_password_strength, generate_random_password
from src.utils.email_utils import send_welcome_email

institution_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
institution_service = InstitutionService()
role_checker = RoleChecker(['superadmin'])
user_service = UserService()

@institution_router.post('/institutions', response_model=InstitutionModel, status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_checker), Depends(rate_limit_dep)])
async def create_institution(institution_data: InstitutionCreateModel, session: AsyncSession = Depends(get_db)):
    email = verify_email(institution_data.email)
    institution_exists = await institution_service.institution_exist(email=email, session=session)
    if institution_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Institution with email alredy exists")
    new_institution = await institution_service.create_institution(institution_data=institution_data, session=session)
    return new_institution

@institution_router.post('/institutions/new/users', response_model=UserModel, status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_checker), Depends(rate_limit_dep)])
async def create_admin_account(admin_data: InstitutionUserCreateModel, session: AsyncSession = Depends(get_db)):
    email = verify_email(admin_data.email)
    password = generate_random_password(length=16)
    is_valid_password = validate_password_strength(password=password)
    if not is_valid_password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=(
                "Password must contain at least 8 characters, including uppercase, lowercase, number, and special symbol."
            )
        )
    user_exists = await user_service.user_exist(email=email, session=session)
    if user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with email alredy exists")
    user_creation_data = admin_data.model_dump()
    user_creation_data["password"] = password
    user_data_for_service = UserCreateModel(**user_creation_data)
    new_user = await user_service.create_user(user_data=user_data_for_service, session=session)
    await send_welcome_email(
        recipient_email=new_user.email,
        generated_password=password,
        username=new_user.username
    )
    return new_user

@institution_router.get('/institutions',  response_model=list[InstitutionModel], status_code=status.HTTP_200_OK, dependencies=[Depends(role_checker), Depends(rate_limit_dep)],)
async def get_all_institutions(
    session: AsyncSession = Depends(get_db),
    _ = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    try:
        institutions = await institution_service.get_all_institutions(session=session, limit=limit, offset=offset)
        return institutions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao obter instituições {e}")