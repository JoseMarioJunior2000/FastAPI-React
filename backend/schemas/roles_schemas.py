from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from enum import Enum

class Roles(str, Enum):
    user = "user"
    admin = "admin" 