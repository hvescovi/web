# Cadastro de pessoas e celulares

Aplicação CRUD com API Flask/SQLAlchemy/PostgreSQL e interface Next.js. O backend e o frontend são projetos Vercel separados.

## Requisitos

- Python 3.10+ e [uv](https://docs.astral.sh/uv/)
- Node.js e npm
- PostgreSQL acessível pelo backend

## Backend local

Na raiz deste projeto:

1. Copie `.env.example` para `.env` e ajuste `POSTGRES_URL_NON_POOLING` conforme o seu PostgreSQL. O `postgres.yaml` descreve o banco local padrão.
2. Instale as dependências e inicie a API:

   ```bash
   uv sync
   uv run python -m src.app
   ```

3. Crie as tabelas:

   ```bash
   curl -X POST http://localhost:5000/criar-tabelas
   ```

   A resposta esperada é `{"resultado":"ok","detalhes":{"mensagem":"Tabelas criadas com sucesso."}}`.

A API fica em `http://localhost:5000`. Pessoas aceitam `nome`, `email` e `telefone`; celulares aceitam `numero`, `modelo`, `marca` e `pessoa_id`. Os recursos possuem rotas de coleção e de item (`GET`, `POST`, `PUT` e `DELETE`). `GET /celulares?pessoa_id=<id>` filtra por pessoa. Ao excluir uma pessoa, seus celulares também são excluídos.

## Frontend local

O arquivo `front/.env.local` aponta para a API local por padrão. Para configurar manualmente, defina `NEXT_PUBLIC_API_URL=http://localhost:5000` em `front/.env.local`. Em outro terminal:

```bash
cd front
npm install
npm run dev
```

Acesse `http://localhost:3000`.

## Vercel

- **Backend:** crie um projeto apontando para esta pasta. O `vercel.json` expõe a aplicação Flask em `api/index.py`. Configure `POSTGRES_URL_NON_POOLING` e, opcionalmente, `CORS_ORIGINS` com a origem do frontend.
- **Frontend:** crie outro projeto apontando para a pasta `front` e configure `NEXT_PUBLIC_API_URL` com a URL pública do backend. A URL deve estar disponível durante o build do Next.js.

Use um PostgreSQL gerenciado que aceite conexões a partir das funções serverless. O arquivo `.env` é local e não deve ser enviado ao Git.
