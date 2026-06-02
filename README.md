# ValoraScan

## O que o sistema é

O ValoraScan é um sistema de apoio para compras em supermercados e atacados. Ele foi pensado para ajudar o usuário a controlar a feira, acompanhar o orçamento e organizar produtos antes de chegar ao caixa.

## O que já existe no projeto

### Backend

- API construída em FastAPI
- Autenticação de usuário com JWT
- Cadastro de usuário (`/auth/register`)
- Login (`/auth/login` e `/auth/login-form`)
- Refresh de token (`/auth/refresh`)
- Criação de feira (`/feiras/feira`)
- Listagem básica de feiras (`/feiras/`)
- Banco de dados SQLite local usando SQLAlchemy
- Estrutura de models para usuário, feira, itens de feira e nota fiscal
- Serviços de autenticação e suporte para OCR/imagem no backend

### Frontend planejado

- Interface planejada em React
- Consumo da API do backend via requisições HTTP
- Uso de autenticação com tokens
- Fluxo de feiras, produtos e resumo de compra

## Stack atual

- Python 3.x
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- python-jose / JWT
- python-multipart
- easyocr / OpenCV / Pillow

## Estrutura atual do backend

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       └── feiras.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── dependencies/
│   │   └── auth.py
│   ├── models/
│   │   ├── feira.py
│   │   ├── feira_item.py
│   │   ├── nota_fiscal.py
│   │   ├── nota_fiscal_item.py
│   │   └── usuario.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── feira.py
│   │   ├── feira_item.py
│   │   ├── nota_fiscal.py
│   │   ├── nota_fiscal_item.py
│   │   └── usuario.py
│   └── services/
│       ├── auth_service.py
│       └── ocr_service.py
├── alembic/
├── requirements.txt
└── env/
```

## Como rodar o backend

1. Abra o terminal em `backend/`
2. Ative o ambiente virtual
3. Instale dependências com `pip install -r requirements.txt`
4. Execute `uvicorn app.main:app --reload`

A API roda em `http://127.0.0.1:8000`
