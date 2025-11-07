from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import get_settings
from src.routers.institution import institution_router
from src.routers.register import signup_router
from src.routers.login import login_router
from src.routers.users import user_router
from src.routers.auth import auth_router
from src.routers.evo import evo_router
import uvicorn
from src.routers.config import AllRoutersConfiguration
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.db.database import engine
import logging
import structlog
from src.core.erros import register_all_errors

logging.basicConfig(level=logging.ERROR, format="%(message)s")
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(file_handler)

structlog.configure(
    processors=[structlog.processors.JSONRenderer()],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Wazzy Platform")
    
    yield
    await engine.dispose()

    logger.info("Shutting down Wazzy Platform")

app = FastAPI(
    title="Wazzy",
    version="0.1.0",
    debug=get_settings().DEBUG,
    lifespan=lifespan
)

AllRoutersConfiguration(
    app=app,
    routers=[
        institution_router,
        signup_router,
        login_router,
        user_router,
        auth_router,
        evo_router
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_all_errors(app=app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
