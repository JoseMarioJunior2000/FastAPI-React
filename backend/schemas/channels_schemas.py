from enum import Enum
from pydantic import BaseModel, Field, AnyHttpUrl, constr
import uuid
from datetime import datetime
from schemas.roles_schemas import Roles
from typing import Optional, Literal

E164_REGEX = r"^\+[1-9]\d{1,14}$"          # telefone em E.164
GRAPH_VER_REGEX = r"^v\d+\.\d+$"           # ex.: v20.0, v21.0

class Provider(str, Enum):
    instagram = 'instagram'
    evolution = 'evolution'
    whatsapp = 'whatsapp'
    email = 'email'
    api = 'api'

class EvolutionCreateModel(BaseModel):
    name: str = Field(max_length=50)
    evolution_url: str
    api_key: str

class EvolutionModel(BaseModel):
    id: int
    name: str
    evolution_url: str
    api_key: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime

class WhatsAppCreateModel(BaseModel):
    """
    Usado para criar a integração com a Meta:
    - recebe access_token e verify_token (não retornados no response).
    - endpoint é derivado via phone_number_id + graph_api_version.
    """
    name: str = constr(strip_whitespace=True, max_length=50)
    phone_number: str = constr(regex=E164_REGEX)                       # E.164: +5599999999999
    phone_number_id: str = constr(strip_whitespace=True, min_length=15) # ID usado na rota /messages
    whatsapp_business_account_id: str = constr(strip_whitespace=True, min_length=15)
    access_token: str = constr(strip_whitespace=True, min_length=1)    # será armazenado cifrado
    callback_url: AnyHttpUrl                                     # URL pública HTTPS para webhook
    verify_token: str = constr(min_length=8, max_length=64)            # handshake do webhook
    graph_api_version: str = constr(regex=GRAPH_VER_REGEX) | "v21.0"   # pode ajustar conforme suporte


# --------- OUTPUT (RESPONSE) ---------
class WhatsAppModel(BaseModel):
    """
    Response model da integração já criada e (opcionalmente) verificada.
    - Não expõe access_token nem verify_token.
    - Exibe apenas indicadores de token e endpoint derivado.
    """
    id: int
    name: str
    phone_number: str
    phone_number_id: str
    whatsapp_business_account_id: str
    graph_api_version: str

    # Derivado: https://graph.facebook.com/{graph_api_version}/{phone_number_id}/messages
    derived_endpoint: AnyHttpUrl

    # Segurança (não retorna segredos):
    has_token: bool
    token_last4: Optional[str] = constr(min_length=4, max_length=4) | None  # últimos 4 chars do token, ofuscado

    # Webhook:
    callback_url: AnyHttpUrl
    webhook_status: Literal["UNCONFIGURED", "PENDING", "VERIFIED", "ERROR"] = "UNCONFIGURED"
    webhook_verified_at: Optional[datetime] = None
    webhook_error: Optional[str] = None

    created_at: datetime
    updated_at: datetime