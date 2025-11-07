from passlib.context import CryptContext
from password_validator import PasswordValidator

password_schema = PasswordValidator()

password_schema \
    .min(8) \
    .max(64) \
    .has().uppercase() \
    .has().lowercase() \
    .has().digits() \
    .has().symbols() \
    .no().spaces()

password_context = CryptContext(schemes=["argon2"], deprecated="auto")

def generate_password_hash(pasword: str) -> str:
    hash = password_context.hash(pasword)
    return hash

def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash=hash)

def validate_password_strength(password: str) -> bool:
    """
    Verifica se a senha atende aos requisitos mínimos de segurança.
    Retorna True se for válida, False caso contrário.
    """
    return password_schema.validate(password)