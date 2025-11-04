from enum import Enum
from typing import Optional, Literal
from typing_extensions import Annotated
from pydantic import BaseModel, Field, AnyHttpUrl
from pydantic.types import StringConstraints
from datetime import datetime

# ----- Constantes de validação -----
E164_REGEX = r"^\+[1-9]\d{1,14}$"
GRAPH_VER_REGEX = r"^v\d+\.\d+$"

# ----- Atalhos de tipos (Pydantic v2) -----
Str50      = Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
StrMin1    = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
StrMin15   = Annotated[str, StringConstraints(strip_whitespace=True, min_length=15)]
E164       = Annotated[str, StringConstraints(pattern=E164_REGEX)]
GraphVer   = Annotated[str, StringConstraints(pattern=GRAPH_VER_REGEX)]
Token8_64  = Annotated[str, StringConstraints(min_length=8, max_length=64)]
Token4     = Annotated[str, StringConstraints(min_length=4, max_length=4)]

# ----- Enums -----
class Provider(str, Enum):
    instagram = "instagram"
    evolution = "evolution"
    whatsapp  = "whatsapp"
    email     = "email"
    api       = "api"

# ----- Evolution -----
class EvolutionCreateModel(BaseModel):
    name: Str50
    evolution_url: str
    api_key: str

class EvolutionModel(BaseModel):
    id: int
    name: str
    evolution_url: str
    api_key: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime

# ----- WhatsApp / Meta -----
class WhatsAppCreateModel(BaseModel):
    """
    Entrada para criar integração com a Meta.
    access_token e verify_token são recebidos mas não devem ser retornados.
    O endpoint derivado usa phone_number_id + graph_api_version.
    """
    name: Str50
    phone_number: E164
    phone_number_id: StrMin15
    whatsapp_business_account_id: StrMin15
    access_token: StrMin1
    callback_url: AnyHttpUrl
    verify_token: Token8_64
    graph_api_version: GraphVer = "v21.0"

class WhatsAppModel(BaseModel):
    """
    Saída da integração criada (sem expor segredos).
    """
    id: int
    name: str
    phone_number: str
    phone_number_id: str
    whatsapp_business_account_id: str
    graph_api_version: str
    derived_endpoint: AnyHttpUrl
    has_token: bool
    token_last4: Optional[Token4] = None
    callback_url: AnyHttpUrl
    webhook_status: Literal["UNCONFIGURED", "PENDING", "VERIFIED", "ERROR"] = "UNCONFIGURED"
    webhook_verified_at: Optional[datetime] = None
    webhook_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None

    created_at: datetime
    updated_at: datetime