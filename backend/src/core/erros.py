from typing import Any, Callable, Optional, Dict
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

# --- Exceções ---
class BooklyException(Exception):
    """Base para erros Bookly"""
    pass

class InvalidToken(BooklyException): ...
class RevokedToken(BooklyException): ...
class AccessTokenRequired(BooklyException): ...
class RefreshTokenRequired(BooklyException): ...
class UserAlreadyExists(BooklyException): ...
class InvalidCredentials(BooklyException): ...
class InsufficientPermission(BooklyException): ...
class UserNotFound(BooklyException): ...
class InvalidJTI(BooklyException): ...
class UserDeleteConflictError(BooklyException): ...
class InvalidTokenError(BooklyException): ...
class AccountNotVerified(BooklyException):
    """Account not yet verified"""
    pass

def create_exception_handler(
    status_code: int,
    initial_detail: Any,
    headers: Optional[Dict[str, str]] = None,
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: Exception):
        return JSONResponse(content=initial_detail, status_code=status_code, headers=headers)
    return exception_handler

def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={"message": "User with email already exists", "error_code": "user_exists"},
        ),
    )
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={"message": "User not found", "error_code": "user_not_found"},
        ),
    )
    app.add_exception_handler(
        UserDeleteConflictError,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={"message": "User cannot be deleted due to related resources", "error_code": "user_delete_conflict"},
        ),
    )
    app.add_exception_handler(
        InvalidJTI,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Invalid token", "error_code": "jti/exp_not_found"},
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Invalid Email Or Password", "error_code": "invalid_email_or_password"},
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    app.add_exception_handler(
        InvalidTokenError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Invalid authentication token", "resolution": "Please get new token", "error_code": "invalid_token"},
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Token is invalid Or expired", "resolution": "Please get new token", "error_code": "invalid_token"},
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Token is invalid or has been revoked", "resolution": "Please get new token", "error_code": "token_revoked"},
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Please provide a valid access token", "resolution": "Please get an access token", "error_code": "access_token_required"},
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Please provide a valid refresh token", "resolution": "Please get a refresh token", "error_code": "refresh_token_required"},
            headers={"WWW-Authenticate": "Bearer"},
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={"message": "You do not have enough permissions to perform this action", "error_code": "insufficient_permissions"},
        ),
    )
    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={"message": "Account Not verified", "error_code": "account_not_verified", "resolution":"Please check your email for verification details"},
        ),
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            content={"message": "Oops! Something went wrong", "error_code": "server_error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            content={"message": "Database error", "error_code": "database_error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )