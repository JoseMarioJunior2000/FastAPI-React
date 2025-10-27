import os
import asyncio
import httpx
import json
import logging

logger = logging.getLogger(__name__)

EVO_SERVER_URL = os.getenv("EVO_SERVER_URL", "https://atd.evo.helperhub.ai")
EVO_INSTANCE   = os.getenv("EVO_INSTANCE", "HH")
EVO_API_KEY    = os.getenv("EVO_API_KEY", "evo_auth_api_key")

HEADERS = {
    "apikey": EVO_API_KEY,
    "Content-Type": "application/json",
}

FIND_INSTANCES_URL = f"{EVO_SERVER_URL}/instance/fetchInstances"
FIND_CONTACTS_URL = f"{EVO_SERVER_URL}/chat/findContacts/{EVO_INSTANCE}"
FIND_MESSAGES_URL = f"{EVO_SERVER_URL}/chat/findMessages/{EVO_INSTANCE}"
FIND_GROUPS_URL = f"{EVO_SERVER_URL}/group/fetchAllGroups/{EVO_INSTANCE}"

async def fetch_instances():
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(FIND_INSTANCES_URL, headers=HEADERS)
            response.raise_for_status()
            return response.json() or []
    except httpx.HTTPStatusError as e:
        # Erros HTTP explícitos (ex: 400, 401, 500)
        logger.error(f"Erro HTTP {e.response.status_code} ao buscar instâncias: {e.response.text}")
        return []
    
    except httpx.RequestError as e:
        # Falhas de rede (timeout, DNS, conexão recusada, etc.)
        logger.error(f"Falha de conexão ao Evolution: {e}")
        return []
    
    except Exception as e:
        # Qualquer outro erro inesperado
        logger.exception(f"Erro inesperado em fetch_instances: {e}")
        return []


async def find_contacts(where: dict = None):
    """Busca contatos da Evolution de forma assíncrona."""
    payload = {"where": where or {}}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(FIND_CONTACTS_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            return response.json() or []
    except httpx.HTTPStatusError as e:
        # Erros HTTP explícitos (ex: 400, 401, 500)
        logger.error(f"Erro HTTP {e.response.status_code} ao buscar contatos: {e.response.text}")
        return []
    
    except httpx.RequestError as e:
        # Falhas de rede (timeout, DNS, conexão recusada, etc.)
        logger.error(f"Falha de conexão ao Evolution: {e}")
        return []
    
    except Exception as e:
        # Qualquer outro erro inesperado
        logger.exception(f"Erro inesperado em find_contacts: {e}")
        return []
    
async def find_groups(get_participants: bool = False):
    """Busca grupos na Evolution de forma assíncrona."""
    params = {"getParticipants": "true" if get_participants else "false"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(FIND_GROUPS_URL, headers=HEADERS, params=params)
            resp.raise_for_status()
            return resp.json() or []
    except httpx.HTTPStatusError as e:
        logger.error(
            "Erro HTTP %s ao buscar grupos: %s (params=%s)",
            e.response.status_code, e.response.text, params
        )
        return []
    except httpx.RequestError as e:
        logger.error("Falha de conexão ao Evolution: %s", e)
        return []
    except Exception as e:
        logger.exception("Erro inesperado em find_groups: %s", e)
        return []

async def get_contact_jid(data_dict: dict):
    """Apenas imprime os dados."""
    #print(json.dumps(data_dict, indent=2, ensure_ascii=False))
    #for i in data_dict:
        #print(i['remoteJid'])
        #print(i['pushName'])
    return "558181447501@s.whatsapp.net"

async def get_conversation(remotejid: str):
    payload = { "where": { "key": { "remoteJid": remotejid } } }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(FIND_MESSAGES_URL, json=payload, headers=HEADERS)
            response.raise_for_status()
            return response.json() or []
    except httpx.HTTPStatusError as e:
        # Erros HTTP explícitos (ex: 400, 401, 500)
        logger.error(f"Erro HTTP {e.response.status_code} ao buscar conversa: {e.response.text}")
        return []
    
    except httpx.RequestError as e:
        # Falhas de rede (timeout, DNS, conexão recusada, etc.)
        logger.error(f"Falha de conexão ao Evolution: {e}")
        return []
    
    except Exception as e:
        # Qualquer outro erro inesperado
        logger.exception(f"Erro inesperado em get_conversation: {e}")
        return []
    
def parse_instances(instances_data: list[dict]) -> list[dict]:
    """Extrai apenas os campos principais das instâncias."""
    if not isinstance(instances_data, list):
        return []

    return [
        {
            "name": i.get("name"),
            "profilePicUrl": i.get("profilePicUrl"),
            "number": i.get("number"),
        }
        for i in instances_data
        if isinstance(i, dict)
    ]

def parse_groups(groups_data: list[dict]) -> list[dict]:
    """
    Extrai e normaliza campos principais dos grupos retornados pela Evolution.
    Campos: subject, pictureUrl, size, restrict, announce, isCommunity, isCommunityAnnounce
    """
    if not isinstance(groups_data, list):
        return []

    return [
        {
            "subject": g.get("subject"),
            "pictureUrl": g.get("pictureUrl"),
            "size": g.get("size"),
            "restrict": g.get("restrict"),
            "announce": g.get("announce"),
            "isCommunity": g.get("isCommunity"),
            "isCommunityAnnounce": g.get("isCommunityAnnounce"),
        }
        for g in groups_data
        if isinstance(g, dict)
    ]

async def main():
    # Faz a chamada e processa o resultado
    instances = await fetch_instances()
    groups = await find_groups()
    #contacts_data = await find_contacts()
    #contatc_jid = await get_contact_jid(contacts_data)
    #conversation = await get_conversation(contatc_jid)
    print(groups)

    print("Requisição concluída com sucesso!\n")

if __name__ == "__main__":
    asyncio.run(main())