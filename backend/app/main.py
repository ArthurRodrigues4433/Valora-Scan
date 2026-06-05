from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL do Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes.auth import auth_router
from app.api.routes.feiras import feiras_router
from app.api.routes.feira_itens import feira_itens_router
from app.api.routes.usuarios import usuarios_router
from app.api.routes.relatorios import relatorios_router

app.include_router(auth_router)
app.include_router(feiras_router)
app.include_router(feira_itens_router)
app.include_router(usuarios_router)
app.include_router(relatorios_router)

# uvicorn app.main:app --reload
