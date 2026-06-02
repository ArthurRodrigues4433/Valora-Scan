# ValoraScan

## Visão do projeto

ValoraScan é um backend para um sistema de gestão de feiras de supermercado e atacado. O foco é permitir que o usuário organize uma feira, adicione produtos por etiqueta de mercado, calcule automaticamente os preços e valores totais, e finalize a feira com segurança.

O backend foi construído em FastAPI com SQLAlchemy e JWT para autenticação.

---

## Fluxo principal do sistema

### 1. Criação da feira

- `POST /feiras/feira`
- Campos esperados: `nome`, `orcamento`
- Cria uma `Feira` com:
  - `id`
  - `nome`
  - `orcamento`
  - `usuario_id` (do token autenticado)
  - `status = em_andamento`
  - `valor_previsto = 0`

### 2. Adição de itens na feira

- `POST /feiras/feira/{feira_id}/itens`
- Cada item pertence à feira via `feira_id`
- O backend calcula automaticamente:
  - `preco_escolhido`
  - `subtotal = preco_escolhido * quantidade`
- O item é salvo em `FeiraItem`
- O sistema deve recalcular `Feira.valor_previsto` sempre que um item for criado, editado ou removido

### 3. Visualização

- `GET /feiras/feira/{feira_id}`
- `GET /feiras/feira/{feira_id}/itens`

### 4. Finalização da feira

- `POST /feiras/feira/{feira_id}/finalizar`
- Atualiza `status` para `finalizada`
- Garante que `valor_previsto` esteja atualizado
- Deve bloquear alterações de itens e feira após finalização

---

## Planejamento de OCR por foto

### Objetivo

Permitir que o usuário envie uma foto da etiqueta do produto e o backend leia automaticamente:

- `nome_produto`
- `preco_varejo`
- `preco_atacado`
- `quantidade_minima_atacado`

### Fluxo de OCR

1. Usuário tira foto da etiqueta
2. Frontend envia imagem para o backend
3. Backend processa a imagem com OCR
4. Backend extrai texto e converte para dados estruturados
5. Usuário informa a quantidade desejada
6. Backend decide o preço correto:
   - se `quantidade >= quantidade_minima_atacado`, usar `preco_atacado`
   - caso contrário, usar `preco_varejo`
7. Backend calcula `subtotal`
8. Item é salvo em `FeiraItem`
9. `Feira.valor_previsto` é atualizado

### Resultado esperado do OCR

```json
{
  "nome_produto": "Arroz Kika 5kg",
  "preco_varejo": 32.99,
  "preco_atacado": 27.99,
  "quantidade_minima_atacado": 3
}
```

---

## Estrutura de dados

### Modelo `Feira`

Campos principais:

- `id`
- `nome`
- `orcamento`
- `valor_previsto`
- `status`
- `usuario_id`
- `created_at`
- `updated_at`

### Modelo `FeiraItem`

Campos principais:

- `id`
- `nome`
- `categoria`
- `preco_varejo`
- `preco_atacado`
- `qtd_minima_atacado`
- `quantidade`
- `preco_escolhido`
- `subtotal`
- `unidade_medida`
- `imagem_url`
- `ocr_texto`
- `created_at`
- `feira_id`

### Modelo `Usuario`

- `id`
- `nome`
- `email`
- `senha`
- `ativo`
- `admin`

### Modelos de nota fiscal

- `NotaFiscal`
- `NotaFiscalItem`

Essas tabelas existem no banco e foram criadas pela migração inicial.

---

## Rotas esperadas

### Autenticação

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/login-form`
- `GET /auth/refresh`

### Feira

- `POST /feiras/feira`
- `GET /feiras/`
- `GET /feiras/feira/{feira_id}`
- `POST /feiras/feira/{feira_id}/finalizar`

### Itens de feira

- `POST /feiras/feira/{feira_id}/itens`
- `PATCH /feiras/feira/{feira_id}/itens/{item_id}`
- `DELETE /feiras/feira/{feira_id}/itens/{item_id}`
- `GET /feiras/feira/{feira_id}/itens`

### OCR

- `POST /ocr/etiqueta`
  - recebe imagem
  - retorna dados extraídos
  - opcionalmente cria item diretamente

---

## Organização do backend

### `app/api/routes/`

- Define endpoints HTTP
- Deve ser responsável por receber requests e devolver respostas
- Deve chamar serviços para regras de negócio

### `app/services/`

- Contém regras de negócio e processamento
- Exemplo:
  - `auth_service.py`
  - `ocr_service.py`
  - `feira_service.py` (recomendado)
  - `feira_item_service.py` (recomendado)

### `app/models/`

- Define os modelos SQLAlchemy
- Cada tabela do banco corresponde a um modelo

### `app/schemas/`

- Define DTOs e validação com Pydantic
- Usa para entrada e saída de dados

### `app/dependencies/`

- Contém dependências FastAPI, como autenticação JWT e injeção de sessão de DB

---

## Pontos importantes

- O backend deve calcular preços, não o frontend
- `Feira.valor_previsto` é derivado dos `subtotal` dos itens
- `status = finalizada` deve bloquear alterações
- `feira_id` deve ser passado pela URL para tornar os endpoints RESTful
- `usuario_id` deve vir do token, não do corpo do request
- O histórico de OCR pode ser guardado em `FeiraItem.imagem_url` e `FeiraItem.ocr_texto`

---

## Como rodar o backend

1. Abra o terminal em `backend/`
2. Ative o ambiente virtual
3. Instale dependências com:

   ```bash
   pip install -r requirements.txt
   ```

4. Rode a aplicação:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Acesse a API em `http://127.0.0.1:8000`

---

## Como testar o fluxo

1. Registrar usuário em `/auth/register`
2. Fazer login em `/auth/login` ou `/auth/login-form`
3. Criar feira em `/feiras/feira`
4. Adicionar item em `/feiras/feira/{feira_id}/itens`
5. Editar/remover item conforme necessário
6. Finalizar feira em `/feiras/feira/{feira_id}/finalizar`

---

## Próximos passos de desenvolvimento

- Criar `app/api/routes/feira_itens.py`
- Implementar `ocr_service.py`
- Criar rota de upload de imagem e parser OCR
- Implementar serviço de recálculo de `valor_previsto`
- Proteger edição de itens quando a feira estiver finalizada
- Adicionar testes funcionais para o fluxo completo
