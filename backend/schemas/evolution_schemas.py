from typing import Optional, List, Any
from pydantic import BaseModel, AnyHttpUrl

class EvoInstance(BaseModel):
    name: Optional[str] = None
    profilePicUrl: Optional[AnyHttpUrl] = None
    ownerJid: Optional[str] = None

class EvoGroup(BaseModel):
    subject: Optional[str] = None
    pictureUrl: Optional[AnyHttpUrl] = None
    size: Optional[int] = None
    restrict: Optional[bool] = None
    announce: Optional[bool] = None
    isCommunity: Optional[bool] = None
    isCommunityAnnounce: Optional[bool] = None

class EvoContact(BaseModel):
    id: Optional[str] = None
    pushName: Optional[str] = None
    remoteJid: Optional[str] = None

class EvoMessage(BaseModel):
    key: Optional[dict] = None
    message: Optional[dict] = None
    messageTimestamp: Optional[int] = None

# Envelopes (opcional – úteis se quiser metadados depois)
class EvoInstancesOut(BaseModel):
    items: List[EvoInstance]

class EvoGroupsOut(BaseModel):
    items: List[EvoGroup]

class EvoContactsOut(BaseModel):
    items: List[EvoContact]

class EvoMessagesOut(BaseModel):
    items: List[EvoMessage]
