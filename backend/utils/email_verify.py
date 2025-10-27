from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException, status


def verify_email(email: str) -> str:
    """
    Valida e normaliza um endereço de e-mail.
    Lança HTTPException se o e-mail for inválido.
    Retorna o e-mail normalizado se for válido.
    """
    try:
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address. Please check the format (example@domain.com)."
        )