from models.user import User
from uuid import UUID
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

ROLE_RANK = {"user": 0, "staff": 1, "admin": 2, "superadmin": 3}

def prevent_self_deletion(current_user: User, user_uid: UUID):
    if current_user.id == user_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "You cannot delete your own account",
                "error_code": "self_delete_forbidden",
            },
        )
    
def can_delete_user(current_user: User, user_to_deleted: User):
    user_role = ROLE_RANK.get(current_user.role, -1)
    user_to_deleted_role = ROLE_RANK.get(user_to_deleted.role, -1)
    if user_to_deleted_role >= user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "You cannot delete another admin",
                "error_code": "admin_delete_admin_forbidden",
            },
        )