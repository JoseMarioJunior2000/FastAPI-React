import json
import hashlib
import functools
import inspect
from typing import Optional, Callable, Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis

class CacheService:
    def __init__(self, redis_client: Redis, default_timeout: int = 60):
        print("[CacheService.__init__] Iniciando CacheService")
        print("[CacheService.__init__] redis_client:", redis_client)
        print("[CacheService.__init__] default_timeout:", default_timeout)

        self.redis_client = redis_client
        self.default_timeout = default_timeout

    def _build_base_key(
        self,
        request: Optional[Request],
        function: Callable,
    ) -> str:
        """
        Base da chave: path + query params (se tiver Request)
        ou nome da função (fallback).
        """
        print("\n[CacheService._build_base_key] Chamado")
        print("[CacheService._build_base_key] function.__name__:", function.__name__)
        print("[CacheService._build_base_key] request presente?:", request is not None)

        if request is not None:
            qp = "&".join(
                f"{k}={v}" for k, v in sorted(request.query_params.items())
            )
            print("[CacheService._build_base_key] query_params raw:", dict(request.query_params))
            print("[CacheService._build_base_key] query_params string:", qp)

            base = request.url.path
            print("[CacheService._build_base_key] request.url.path:", base)

            if qp:
                base = f"{base}?{qp}"
                print("[CacheService._build_base_key] base com query params:", base)
        else:
            base = function.__name__
            print("[CacheService._build_base_key] Sem request, usando nome da função como base:", base)

        print("[CacheService._build_base_key] base final:", base)
        return base

    def _extract_current_user(self, args, kwargs) -> Any:
        """
        Tenta achar o current_user nos kwargs/args.
        """
        print("\n[CacheService._extract_current_user] Chamado")
        print("[CacheService._extract_current_user] kwargs keys:", list(kwargs.keys()))
        print("[CacheService._extract_current_user] qntd args:", len(args))

        if "current_user" in kwargs:
            print("[CacheService._extract_current_user] current_user encontrado em kwargs")
            return kwargs["current_user"]

        for idx, arg in enumerate(args):
            print(f"[CacheService._extract_current_user] analisando arg[{idx}]:", type(arg))
            if hasattr(arg, "id"):
                print(f"[CacheService._extract_current_user] arg[{idx}] possui atributo 'id', retornando como current_user")
                return arg

        print("[CacheService._extract_current_user] Nenhum current_user encontrado")
        return None

    def cached(
        self,
        timeout: Optional[int] = None,
        key_prefix: str = "view",
    ) -> Callable:
        print("\n[CacheService.cached] Decorator criado com:")
        print("[CacheService.cached] timeout param:", timeout)
        print("[CacheService.cached] key_prefix:", key_prefix)

        def decorator(function: Callable) -> Callable:
            is_async = inspect.iscoroutinefunction(function)
            print("\n[CacheService.cached.decorator] Registrando função no cache:")
            print("[CacheService.cached.decorator] function.__name__:", function.__name__)
            print("[CacheService.cached.decorator] is_async?:", is_async)

            @functools.wraps(function)
            async def async_wrapper(*args, **kwargs) -> Any:
                print("\n[CacheService.async_wrapper] >>> Início (async)")
                print("[CacheService.async_wrapper] function:", function.__name__)
                print("[CacheService.async_wrapper] args len:", len(args))
                print("[CacheService.async_wrapper] kwargs keys:", list(kwargs.keys()))

                # Request
                request: Optional[Request] = kwargs.get("request")
                if request is None:
                    print("[CacheService.async_wrapper] 'request' não encontrado em kwargs, procurando em args...")
                    for idx, arg in enumerate(args):
                        print(f"[CacheService.async_wrapper] analisando arg[{idx}]:", type(arg))
                        if isinstance(arg, Request):
                            print(f"[CacheService.async_wrapper] Request encontrado em arg[{idx}]")
                            request = arg
                            break
                else:
                    print("[CacheService.async_wrapper] Request encontrado em kwargs")

                # current_user (já resolvido pelo FastAPI via Depends)
                current_user = self._extract_current_user(args, kwargs)
                if current_user is not None:
                    user_id_value = getattr(current_user, "id", None)
                    print("[CacheService.async_wrapper] current_user encontrado, id:", user_id_value)
                else:
                    user_id_value = None
                    print("[CacheService.async_wrapper] current_user NÃO encontrado")

                base_key = self._build_base_key(request, function)

                if user_id_value is not None:
                    cache_key = f"{key_prefix}:user:{user_id_value}:{base_key}"
                else:
                    cache_key = f"{key_prefix}:{base_key}"

                print("[CacheService.async_wrapper] cache_key construída:", cache_key)

                # GET do Redis
                print("[CacheService.async_wrapper] Chamando Redis.get(...)")
                cached = await self.redis_client.get(cache_key)
                print("[CacheService.async_wrapper] Resultado Redis.get:", type(cached), cached)

                if cached is not None:
                    if isinstance(cached, (bytes, bytearray)):
                        print("[CacheService.async_wrapper] cached é bytes, fazendo decode UTF-8")
                        cached = cached.decode("utf-8")

                    try:
                        data = json.loads(cached)
                        print("[CacheService.async_wrapper] JSON carregado com sucesso")
                        print("[CacheService.async_wrapper] >>> HÁ cache para:", cache_key)
                        return data
                    except json.JSONDecodeError as e:
                        print("[CacheService.async_wrapper] ERRO ao decodificar JSON do cache:", e)
                        print("[CacheService.async_wrapper] Ignorando cache corrompido e seguindo...")

                # miss de cache
                print("[CacheService.async_wrapper] >>> NÃO há cache para:", cache_key)
                print("[CacheService.async_wrapper] Chamando função original:", function.__name__)
                result = await function(*args, **kwargs)
                print("[CacheService.async_wrapper] Função original retornou tipo:", type(result))

                serializable = jsonable_encoder(result)
                print("[CacheService.async_wrapper] Resultado após jsonable_encoder, tipo:", type(serializable))

                payload = json.dumps(serializable)
                print("[CacheService.async_wrapper] Payload JSON gerado (len):", len(payload))

                ttl = timeout or self.default_timeout
                print("[CacheService.async_wrapper] TTL utilizado:", ttl)

                print("[CacheService.async_wrapper] Chamando Redis.setex(...)")
                await self.redis_client.setex(cache_key, ttl, payload)
                print("[CacheService.async_wrapper] Valor salvo no Redis com sucesso")

                print("[CacheService.async_wrapper] >>> Fim (async), retornando resultado original")
                return result

            @functools.wraps(function)
            def sync_wrapper(*args, **kwargs) -> Any:
                print("\n[CacheService.sync_wrapper] >>> Início (sync)")
                print("[CacheService.sync_wrapper] function:", function.__name__)
                print("[CacheService.sync_wrapper] args len:", len(args))
                print("[CacheService.sync_wrapper] kwargs keys:", list(kwargs.keys()))

                request: Optional[Request] = kwargs.get("request")
                if request is None:
                    print("[CacheService.sync_wrapper] 'request' não encontrado em kwargs, procurando em args...")
                    for idx, arg in enumerate(args):
                        print(f"[CacheService.sync_wrapper] analisando arg[{idx}]:", type(arg))
                        if isinstance(arg, Request):
                            print(f"[CacheService.sync_wrapper] Request encontrado em arg[{idx}]")
                            request = arg
                            break
                else:
                    print("[CacheService.sync_wrapper] Request encontrado em kwargs")

                current_user = self._extract_current_user(args, kwargs)
                if current_user is not None:
                    user_id_value = getattr(current_user, "id", None)
                    print("[CacheService.sync_wrapper] current_user encontrado, id:", user_id_value)
                else:
                    user_id_value = None
                    print("[CacheService.sync_wrapper] current_user NÃO encontrado")

                base_key = self._build_base_key(request, function)

                if user_id_value is not None:
                    cache_key = f"{key_prefix}:user:{user_id_value}:{base_key}"
                else:
                    cache_key = f"{key_prefix}:{base_key}"

                print("[CacheService.sync_wrapper] cache_key construída:", cache_key)

                print("[CacheService.sync_wrapper] Chamando Redis.get(...) (sync)")
                cached = self.redis_client.get(cache_key)
                print("[CacheService.sync_wrapper] Resultado Redis.get:", type(cached), cached)

                if cached is not None:
                    if isinstance(cached, (bytes, bytearray)):
                        print("[CacheService.sync_wrapper] cached é bytes, fazendo decode UTF-8")
                        cached = cached.decode("utf-8")

                    try:
                        data = json.loads(cached)
                        print("[CacheService.sync_wrapper] JSON carregado com sucesso")
                        print("[CacheService.sync_wrapper] >>> HÁ cache para:", cache_key)
                        return data
                    except json.JSONDecodeError as e:
                        print("[CacheService.sync_wrapper] ERRO ao decodificar JSON do cache:", e)
                        print("[CacheService.sync_wrapper] Ignorando cache corrompido e seguindo...")

                print("[CacheService.sync_wrapper] >>> NÃO há cache para:", cache_key)
                print("[CacheService.sync_wrapper] Chamando função original:", function.__name__)
                result = function(*args, **kwargs)
                print("[CacheService.sync_wrapper] Função original retornou tipo:", type(result))

                serializable = jsonable_encoder(result)
                print("[CacheService.sync_wrapper] Resultado após jsonable_encoder, tipo:", type(serializable))

                payload = json.dumps(serializable)
                print("[CacheService.sync_wrapper] Payload JSON gerado (len):", len(payload))

                ttl = timeout or self.default_timeout
                print("[CacheService.sync_wrapper] TTL utilizado:", ttl)

                print("[CacheService.sync_wrapper] Chamando Redis.setex(...) (sync)")
                self.redis_client.setex(cache_key, ttl, payload)
                print("[CacheService.sync_wrapper] Valor salvo no Redis com sucesso")

                print("[CacheService.sync_wrapper] >>> Fim (sync), retornando resultado original")
                return result

            # Loga qual wrapper será usado
            if is_async:
                print("[CacheService.cached.decorator] Retornando async_wrapper para função:", function.__name__)
                return async_wrapper
            else:
                print("[CacheService.cached.decorator] Retornando sync_wrapper para função:", function.__name__)
                return sync_wrapper

        return decorator


def contacts_cache_key(instance: str, where_dict: Optional[dict]) -> str:
    print("\n[contacts_cache_key] Chamado")
    print("[contacts_cache_key] instance:", instance)
    print("[contacts_cache_key] where_dict:", where_dict)

    where_norm = json.dumps(where_dict or {}, sort_keys=True, separators=(",", ":"))
    print("[contacts_cache_key] where_norm:", where_norm)

    where_hash = hashlib.sha1(where_norm.encode("utf-8")).hexdigest()
    print("[contacts_cache_key] where_hash:", where_hash)

    final_key = f"endpoint:contacts:{instance}:{where_hash}"
    print("[contacts_cache_key] final_key:", final_key)

    return final_key