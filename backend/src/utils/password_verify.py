from passlib.context import CryptContext
from password_validator import PasswordValidator
import secrets
import string

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

def generate_random_password(length: int) -> str:
    """
    Gera uma senha aleatória e criptograficamente segura.

    Args:
        length (int): O tamanho desejado para a senha. Padrão é 12.

    Returns:
        str: A senha gerada.
    """
    # 1. Define os caracteres a serem usados: letras (maiúsculas e minúsculas), dígitos e pontuação.
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # 2. Usa secrets.choice() para selecionar caracteres de forma segura.
    #    secrets.SystemRandom é usado internamente, garantindo aleatoriedade forte.
    password = ''.join(secrets.choice(characters) for i in range(length))
    
    # 3. Garante que a senha tenha pelo menos um tipo de caractere de cada categoria
    #    (opcional, mas recomendado para senhas fortes)
    
    # Se a senha não tiver uma letra minúscula, maiúscula e um dígito, 
    # ela é regenerada. Isso garante a complexidade mínima.
    while (not any(c.islower() for c in password) or
           not any(c.isupper() for c in password) or
           not any(c.isdigit() for c in password)):
        
        password = ''.join(secrets.choice(characters) for i in range(length))

    return password