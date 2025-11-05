from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from schemas.roles_schemas import Roles
from typing import Optional

class User(BaseModel):
    username: str = Field(max_length=100)
    email: str = Field(max_length=40)
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=100)
    email: str = Field(max_length=40)
    password: str = Field(min_length=8)
    role: Roles = Field(default=Roles.user)
    institution_id: uuid.UUID

class UserModel(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime
    role: str
    institution_id: uuid.UUID

class UserLoginModel(BaseModel):
    email: str
    password: str = Field(exclude=True)

class UserProfileChange(BaseModel):
    first_name: Optional[str] = Field(None, max_length=25)
    last_name:  Optional[str] = Field(None, max_length=25)
    username:   Optional[str] = Field(None, max_length=100)