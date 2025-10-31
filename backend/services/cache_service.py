import json
import hashlib
from fastapi import HTTPException, Depends, Query, status
from typing import Optional

def contacts_cache_key(instance: str, where_dict: Optional[dict]) -> str:
    where_norm = json.dumps(where_dict or {}, sort_keys=True, separators=(",", ":"))
    where_hash = hashlib.sha1(where_norm.encode("utf-8")).hexdigest()
    return f"endpoint:contacts:{instance}:{where_hash}"