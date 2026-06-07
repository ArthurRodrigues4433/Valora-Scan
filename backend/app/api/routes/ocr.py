from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.database import pegar_session
from app.dependencies.auth import verify_token
from app.schemas.ocr import OCRResponse
from app.services.ocr_service import processar_imagem_ocr  # Mudar import

ocr_router = APIRouter(
    prefix="/ocr", tags=["ocr"], dependencies=[Depends(verify_token)]
)


@ocr_router.post("/etiqueta", response_model=OCRResponse)
async def ler_etiqueta(
    file: UploadFile = File(...), session: Session = Depends(pegar_session)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")

    conteudo = await file.read()
    resultado = await processar_imagem_ocr(conteudo)  # Chamar função correta
    return resultado