from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from src.core.config import get_settings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

config = ConnectionConfig(
    MAIL_USERNAME=get_settings().MAIL_USERNAME,
    MAIL_PASSWORD=get_settings().MAIL_PASSWORD,
    MAIL_PORT=get_settings().MAIL_PORT,
    MAIL_SERVER=get_settings().MAIL_SERVER,
    MAIL_FROM=get_settings().MAIL_FROM,
    MAIL_FROM_NAME=get_settings().MAIL_FROM_NAME,
    MAIL_SSL_TLS=False,
    MAIL_STARTTLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

mail = FastMail(config=config)

def create_message(recipients: list[str], subject: str, body: str):

    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )

    return message