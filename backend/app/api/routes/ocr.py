from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.database import pegar_session
from app.dependencies.auth import verify_token
from app.schemas.ocr import OCRResponse
from app.services.ocr_service import processar_imagem_ocr  # Mudar import

ocr_router = APIRouter(
    prefix="/ocr", tags=["ocr"], dependencies=[Depends(verify_token)]
)

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB


@ocr_router.post("/etiqueta", response_model=OCRResponse)
async def ler_etiqueta(
    file: UploadFile = File(...), session: Session = Depends(pegar_session)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. Tamanho máximo permitido: {MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
        )

    resultado = await processar_imagem_ocr(contents)
    return resultado