from fastapi import FastAPI, APIRouter, status, HTTPException
from typing import List
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