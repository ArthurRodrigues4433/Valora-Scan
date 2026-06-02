from fastapi import FastAPI

app = FastAPI()

from app.api.routes.auth import auth_router
from app.api.routes.feiras import feiras_router
from app.api.routes.feira_itens import feira_itens_router

app.include_router(auth_router)
app.include_router(feiras_router)
app.include_router(feira_itens_router)

# uvicorn app.main:app --reload
