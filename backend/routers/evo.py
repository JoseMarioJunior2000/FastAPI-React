from utils.token_auth import create_access_token, decode_token
from fastapi import APIRouter, Depends, status, Query, File, UploadFile, Form
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
from core.dependencies import AccessTokenBearer, get_current_user, RoleChecker, ensure_instance_exists
from typing import List, Optional, Literal
import json
from schemas.evolution_schemas import (
    EvoInstancesOut, EvoGroupsOut, EvoContactsOut, EvoMessagesOut,
    EvoInstance, EvoGroup, EvoContact, EvoMessage,
)
from services.evolution_service import EvolutionService
from utils.file_utils import is_upload_too_large
from fastapi_cache.decorator import cache
from db.redis import redis_client
from services.cache_service import contacts_cache_key
from fastapi.encoders import jsonable_encoder
from models.message import MessageMedia

CACHE_TTL_SECONDS = 60

evo_router = APIRouter(prefix=f"{get_settings().API_PREFIX}/{get_settings().API_VERSION}")
role_checker = RoleChecker(['admin'])

@evo_router.get("/inboxes", response_model=List[EvoInstance], status_code=status.HTTP_200_OK, dependencies=[Depends(role_checker)])
async def evo_instances(
    evo: EvolutionService = Depends(EvolutionService)
):
    return await evo.fetch_instances()

@evo_router.get("/contacts", response_model=EvoContactsOut, status_code=status.HTTP_200_OK)
async def evo_contacts(
    instance: str = Depends(ensure_instance_exists),
    where: Optional[str] = Query(None, description='JSON de filtros, ex.: {"pushName": {"$like": "%Maria%"}}'),
    evo: EvolutionService = Depends(EvolutionService),
    token_details: dict = Depends(AccessTokenBearer()),
):
    try:
        where_dict = json.loads(where) if where else None
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Parâmetro 'where' precisa ser um JSON válido")

    cache_key = contacts_cache_key(instance, where_dict)

    cached = await redis_client.get(cache_key)
    if cached:
        if isinstance(cached, (bytes, bytearray)):
            cached = cached.decode("utf-8")
        items = json.loads(cached)
        print("há cache")
        return EvoContactsOut(items=items)
    print("não há cache")
    contacts = await evo.find_contacts(where=where_dict, instance=instance)
    items_serializable = jsonable_encoder(contacts)
    try:
        await redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(items_serializable, separators=(",", ":")))
    except Exception as e:
        print(f"Redis setex falhou: {e}")

    return EvoContactsOut(items=contacts)

@evo_router.get("/groups", response_model=EvoGroupsOut, status_code=status.HTTP_200_OK)
async def evo_groups(
    instance: str = Depends(ensure_instance_exists),
    evo: EvolutionService = Depends(EvolutionService),
    token_details: dict = Depends(AccessTokenBearer())
):
    groups = await evo.find_groups(get_participants=False, instance=instance)
    return EvoGroupsOut(items=groups)

@evo_router.post("/file")
async def upload_file(file: UploadFile = File(...), 
    media_type: Literal["image", "document"] = Form(...),
    session: AsyncSession = Depends(get_db)
):
    if await is_upload_too_large(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo excede o limite de 10 MB."
        )
    media_bytes = await file.read()
    entity = MessageMedia(
        media_name=file.filename,
        media_type=media_type,
        media_data=media_bytes
    )
    try:
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
    except Exception as e:
        await session.rollback()
        raise HTTPException(detail=e)
    return {"filename": file.filename, "content_type": file.content_type}