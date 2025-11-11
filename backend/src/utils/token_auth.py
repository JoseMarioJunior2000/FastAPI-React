from datetime import datetime, timedelta
import jwt
import uuid
from src.core.config import get_settings
import logging
from fastapi.exceptions import HTTPException
from fastapi import status
import logging
from src.core.erros import InvalidToken, InvalidTokenError

ACCESS_TOKEN_EXPIRY = 900

def serialize_roles(roles):
    return [role.name for role in roles] if roles else []

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {}
    payload['user'] = user_data
    payload['exp'] = datetime.utcnow() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh
    token = jwt.encode(payload=payload, key=get_settings().JWT_SECRET, algorithm=get_settings().JWT_ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=get_settings().JWT_SECRET,
            algorithms=[get_settings().JWT_ALGORITHM]
        )
        return token_data
    except jwt.ExpiredSignatureError:
        raise InvalidToken()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()
    except jwt.PyJWKError as e:
        logging.exception(e)
        return None
