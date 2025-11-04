from enum import Enum

class Roles(str, Enum):
    user = "user"
    admin = "admin" 
    superadmin = "superadmin"