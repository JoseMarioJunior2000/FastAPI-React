from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import get_settings
from routers.register import signup_router
from routers.login import login_router
from routers.users import user_router
from routers.auth import auth_router
from routers.evo import evo_router
import uvicorn
from routers.config import AllRoutersConfiguration

app = FastAPI(
    title="Wazzy",
    version="0.1.0",
    debug=get_settings().DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AllRoutersConfiguration(
    app=app,
    routers=[
        signup_router,
        login_router,
        user_router,
        auth_router,
        evo_router
    ]
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
