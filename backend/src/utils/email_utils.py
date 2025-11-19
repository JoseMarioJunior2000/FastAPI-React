import httpx
from src.core.config import get_settings

SEND_MAIL_ENDPOINT = f"http://localhost:{get_settings().BACKEND_PORT }/api/v1/send_mail"

async def send_welcome_email(recipient_email: str, generated_password: str, username: str) -> None:
    """
    Envia um e-mail de boas-vindas contendo a senha gerada.

    Args:
        recipient_email: O endereço de e-mail do novo usuário.
        generated_password: A senha aleatória gerada para o usuário.
        username: O nome do novo usuário.
    """
    
    email_data = {
        "addresses": [recipient_email],
        "subject": "Sua Conta foi Criada - Senha Temporária",
        "body": (
            f"Olá, {username}!<br><br>"
            "Sua conta foi criada com sucesso.<br>"
            f"Seu nome de usuário (e-mail) é: <b>{recipient_email}</b><br>"
            f"Sua senha temporária é: <b>{generated_password}</b><br><br>"
            "Recomendamos que você altere sua senha imediatamente após o primeiro login."
        ),
        "is_html": True
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SEND_MAIL_ENDPOINT,
                json=email_data,
                timeout=10
            )

        response.raise_for_status()
        print(f"INFO: E-mail enviado com sucesso para {recipient_email}")

    except httpx.HTTPStatusError as e:
        print(f"ERROR: Falha ao enviar e-mail. Status: {e.response.status_code}. Detalhe: {e.response.text}")
    except httpx.RequestError as e:
        print(f"ERROR: Falha na requisição HTTP para o serviço de e-mail: {e}")