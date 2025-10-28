from fastapi import FastAPI, APIRouter, status, HTTPException
from typing import List
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

class AllRoutersConfiguration:
    def __init__(self, app: FastAPI, routers: List[APIRouter]):
        """
        Classe responsável por registrar todos os routers da aplicação no FastAPI.

        :param app: Instância principal do FastAPI
        :param routers: Lista de objetos APIRouter a serem incluídos
        """
        self.app = app
        self.routers = routers
        self._register_routers()
        self._log_all_routes()

    def _register_routers(self) -> None:
        """Registra todos os routers fornecidos na aplicação FastAPI."""
        try:
            for router in self.routers:
                self.app.include_router(router)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao registrar routers: {str(e)}"
            )
        
    def _log_all_routes(self) -> None:
        """Exibe no terminal todas as rotas registradas na aplicação."""
        for route in self.app.routes:
            methods = ", ".join(route.methods)
            logger.info(f"✅ Rota registrada:  {methods:15s} {route.path}")