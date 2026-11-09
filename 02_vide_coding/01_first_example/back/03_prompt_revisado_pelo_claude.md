Crie um backend em Python com as seguintes especificações:

### Tecnologias

1. Flask, com `flask-cors` habilitado para um frontend React/Next.
2. Banco Postgres, acessado com SQLAlchemy 2.x (sintaxe moderna: `DeclarativeBase`, `Mapped`, `mapped_column`, consultas com `select()`) e o driver `psycopg` (v3).
3. A variável de ambiente `POSTGRES_URL_NON_POOLING` conterá a URL de conexão. Se ela começar com `postgres://` ou `postgresql://`, converta para `postgresql+psycopg://`.
4. Gerenciador de pacotes `uv` (use `pyproject.toml`).
5. Sem autenticação.
6. a variável de ambiente do Postgres deve ser lida a partir de um arquivo .env
7. crie um arquivo .gitignore apropriado

### Modelos (arquivo `modelos.py`)

- `Pessoa`: id, nome, email (único), telefone.
- `Celular`: id, numero (texto), modelo, marca, pessoa (chave estrangeira obrigatória para `Pessoa`).
- Uma pessoa pode ter vários celulares. Ao excluir uma pessoa, exclua também seus celulares (cascade).

### Arquitetura

- `configuracoes.py`: cria a app Flask, o engine, a sessão e a `Base` do SQLAlchemy, e concentra as importações e configurações.
- `modelos.py`: classes persistentes.
- `servicos.py`: lógica de negócio, usando apenas os modelos.
- `rotas.py`: rotas Flask, usando apenas os serviços.
- Os arquivos devem ficar dentro de uma pasta "src"

### Operações

- Para `Pessoa` e `Celular`: inserir, listar, editar e excluir (`POST`, `GET`, `PUT`, `DELETE`, em `/pessoas` e `/celulares`).
- Uma rota `POST /criar-tabelas` para criar as tabelas.

### Formato das respostas

- Sempre JSON com `"resultado"` (`"ok"` ou `"erro"`) e `"detalhes"` (dados da operação ou mensagem de erro).
- Use códigos HTTP apropriados (200/201, 400, 404, 500).

### Implantação e documentação

- Hospedagem na Vercel (ambiente serverless): inclua o ponto de entrada exposto como `app` e o `vercel.json` necessário.
- Crie um `README.md` explicando como executar localmente (instalar com `uv`, definir a variável de ambiente, iniciar o servidor).
