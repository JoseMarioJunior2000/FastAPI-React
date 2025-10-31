import os
import httpx
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable
from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError
from core.config import get_settings
from schemas.evolution_schemas import EvoInstance, EvoGroup, EvoContact, EvoMessage
from db.redis import redis_client

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)
settings = get_settings()

class EvolutionService:
    def __init__(self, timeout: float = 30.0) -> None:
        settings = get_settings()
        self.server_url = settings.EVO_SERVER_URL
        self.api_key = settings.EVO_API_KEY
        self.timeout = timeout

        if not self.server_url or not self.api_key:
            raise RuntimeError("EvolutionService: EVO_SERVER_URL ou EVO_API_KEY não configurados.")

    def _headers(self) -> Dict[str, str]:
        return {"apikey": self.api_key, "Content-Type": "application/json"}

    def _make_url(self, path: str) -> str:
        return f"{self.server_url.rstrip('/')}/{path.lstrip('/')}"

    async def _request(self, method: str, url: str, *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.request(
                    method=method,
                    url=url,
                    headers=self._headers(),
                    params=params,
                    json=json,
                )
            resp.raise_for_status()
            data = resp.json()
            return data if data is not None else []
        
        except httpx.HTTPStatusError as e:
            detail = {"message": "Erro na Evolution API", "body": e.response.text}
            logger.error("HTTP %s em %s %s: %s", e.response.status_code, method, url, e.response.text)
            raise HTTPException(status_code=e.response.status_code, detail=detail)
        
        except httpx.RequestError as e:
            logger.error("Falha de rede Evolution (%s %s): %s", method, url, e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"message": "Falha de conexão ao Evolution", "error": str(e)},
            )
        
        except Exception as e:
            logger.exception("Erro inesperado Evolution (%s %s): %s", method, url, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Erro inesperado ao chamar Evolution", "error": str(e)},
            )

    # ---------- Métodos públicos (URLs dinâmicas por instance) ----------

    async def fetch_instances(self) -> List[EvoInstance]:
        url = self._make_url("/instance/fetchInstances")
        raw = await self._request("GET", url)
        return self._validate_list(raw, EvoInstance)

    async def find_contacts(self, where: Optional[Dict[str, Any]] = None, instance: Optional[str] = None) -> List[EvoContact]:
        inst = instance
        if not instance:
            raise ValueError("instance é obrigatório em find_contacts()")
        url = self._make_url(f"/chat/findContacts/{inst}")
        payload = {"where": where or {}}
        raw = await self._request("POST", url, json=payload)
        return self._validate_list(raw, EvoContact)

    async def find_groups(self, get_participants: bool = False, instance: Optional[str] = None) -> List[EvoGroup]:
        inst = instance
        url = self._make_url(f"/group/fetchAllGroups/{inst}")
        params = {"getParticipants": "true" if get_participants else "false"}
        raw = await self._request("GET", url, params=params)

        items = []
        if isinstance(raw, list):
            for g in raw:
                if isinstance(g, dict):
                    items.append({
                        "subject": g.get("subject"),
                        "pictureUrl": g.get("pictureUrl"),
                        "size": g.get("size"),
                        "restrict": g.get("restrict"),
                        "announce": g.get("announce"),
                        "isCommunity": g.get("isCommunity"),
                        "isCommunityAnnounce": g.get("isCommunityAnnounce"),
                    })
        return self._validate_list(items, EvoGroup)

    async def get_conversation(self, remotejid: str, instance: Optional[str] = None) -> List[EvoMessage]:
        inst = instance
        url = self._make_url(f"/chat/findMessages/{inst}")
        payload = {"where": {"key": {"remoteJid": remotejid}}}
        raw = await self._request("POST", url, json=payload)

        items = []
        if isinstance(raw, list):
            for m in raw:
                if isinstance(m, dict):
                    items.append({
                        "key": m.get("key"),
                        "message": m.get("message"),
                        "messageTimestamp": m.get("messageTimestamp"),
                    })
        return self._validate_list(items, EvoMessage)

    # ---------- Utils ----------

    def _validate_list(self, data: List[dict], model: Type[T]) -> List[T]:
        try:
            return [model.model_validate(i) for i in data]
        except ValidationError as ve:
            logger.error("Erro de validação Evolution (%s): %s", model.__name__, ve)
            # 502 para indicar que a origem retornou algo fora do contrato
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"message": "Resposta inválida da Evolution", "errors": ve.errors()},
            )
