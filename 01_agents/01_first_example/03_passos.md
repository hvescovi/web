---------------------
A) CRIAÇÃO do backend
---------------------

Executar o que está na especificação do backend (arquivo 01)

----------------------
B) CRIAÇÃO do frontend
----------------------

1) criar um projeto do react/next 

usar comando 
npx create-next-app@latest

nomear a pasta do front-end como "front"

2) Executar o que está na especificação do frontend (arquivo 02)

---------------
C) Configuração de variável de ambiente do backend
----------------

1) use variável de ambiente para armazenar informações de conexão com o postgres.

2) o arquivo YAML nesta pasta contém as configurações do servidor postgres que está ativo

D) Execução do backend
----------------------

executar o backend com este comando: uv run python -m src.app

-----------------------------------
E) Instalação/configuração frontend
-----------------------------------

1) usar variável de ambiente local para localizar o backend

NEXT_PUBLIC_API_URL=http://localhost:5000

F) Criação das tabelas
----------------------

criar as tabelas acionando a rota com este comando: curl -X POST localhost:5000/criar-tabelas

O resultado deverá ser este:

{"detalhes":{"mensagem":"Tabelas criadas com sucesso."},"resultado":"ok"}

G) Execução do frontend

executar e acessar o frontend com este comando:

npm run dev