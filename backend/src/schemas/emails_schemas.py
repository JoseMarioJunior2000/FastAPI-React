from pydantic import BaseModel, EmailStr
from typing import List, Optional

class EmailModel(BaseModel):
    addresses: List[EmailStr]
    subject: str
    body: str
    # Opcional, se o seu serviço precisar saber se o corpo é HTML
    is_html: Optional[bool] = True