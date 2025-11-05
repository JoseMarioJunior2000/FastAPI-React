from fastapi import APIRouter, Depends, status, Query
from schemas.institution_schemas import InstitutionCreateModel, InstitutionModel
from services.institution_service import InstitutionService
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from core.config import get_settings
from utils.email_verify import verify_email
from core.dependencies import AccessTokenBearer, get_current_user, RoleChecker, ensure_instance_exists
from core.dependencies import rate_limit_dep

institution_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
institution_service = InstitutionService()
role_checker = RoleChecker(['superadmin'])

@institution_router.post('/institutions', response_model=InstitutionModel, status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_checker), Depends(rate_limit_dep)])
async def create_institution(institution_data: InstitutionCreateModel, session: AsyncSession = Depends(get_db)):
    email = verify_email(institution_data.email)
    institution_exists = await institution_service.institution_exist(email=email, session=session)
    if institution_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Institution with email alredy exists")
    new_institution = await institution_service.create_institution(institution_data=institution_data, session=session)
    return new_institution

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