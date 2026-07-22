from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("valora")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes.auth import auth_router
from app.api.routes.feiras import feiras_router
from app.api.routes.feira_itens import feira_itens_router
from app.api.routes.usuarios import usuarios_router
from app.api.routes.relatorios import relatorios_router
from app.api.routes.ocr import ocr_router
from app.api.routes.notas import notas_router
from app.api.routes.perfil import perfil_router
from app.api.routes.nfce import nfce_router
from app.api.routes.health import health_router

app.include_router(auth_router)
app.include_router(feiras_router)
app.include_router(feira_itens_router)
app.include_router(usuarios_router)
app.include_router(relatorios_router)
app.include_router(ocr_router)
app.include_router(notas_router)
app.include_router(perfil_router)
app.include_router(nfce_router)
app.include_router(health_router)

logger.info("ValoraScan API iniciada")

# uvicorn app.main:app --reload --host 0.0.0.0
# uvicorn app.main:app --reload --reload-dir app --host 0.0.0.0
