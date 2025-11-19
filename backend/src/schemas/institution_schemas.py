from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from src.schemas.roles_schemas import Roles
from typing import Optional
from typing_extensions import Annotated
from pydantic.types import StringConstraints

E164_REGEX = r"^\+[1-9]\d{1,14}$"

# ----- Atalhos de tipos (Pydantic v2) -----
Str50      = Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
E164       = Annotated[str, StringConstraints(pattern=E164_REGEX)]

class InstitutionCreateModel(BaseModel):
    name: Str50
    email: str = Field(max_length=40)
    phone: E164
    address: str
    cnpj: str

class InstitutionModel(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    phone: str
    address: str
    cnpj: str
    created_at: datetime
    updated_at: datetime

class InstitutionUserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=100)
    email: str = Field(max_length=40)
    role: Roles = Field(default=Roles.admin)
    institution_id: uuid.UUID
