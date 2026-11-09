# Festa IFC

Aplicação web para organizar a festa do IFC Campus Blumenau. Permite cadastrar
alimentos e preços de venda, relacionar ingredientes aos alimentos, registrar
doações e fornecedores e organizar as pessoas que vão trabalhar no evento.
Os insumos são tratados como doações; o sistema não calcula custos de compra.

## Requisitos

- Python 3.11 ou superior
- [uv](https://docs.astral.sh/uv/)

## Executar localmente

Na pasta do projeto:

```bash
uv sync
uv run streamlit run src/party_organizer/app.py
```

Sem configuração adicional, a aplicação cria `party_organizer.db` em SQLite
na pasta de execução. Para rodar os testes:

```bash
uv run pytest
```

## Banco de dados

O SQLite é o padrão para desenvolvimento e testes locais. Para usar MySQL,
defina `DATABASE_URL` com uma URL SQLAlchemy e instale as dependências com
`uv sync`:

```bash
export DATABASE_URL="mysql+pymysql://usuario:senha@localhost:3306/festa_ifc"
uv run streamlit run src/party_organizer/app.py
```

Crie previamente o banco MySQL e use credenciais com permissão para criar e
alterar tabelas. Se a senha contiver caracteres especiais, codifique-os para
URL. Para o Streamlit Community Cloud, configure `DATABASE_URL` em **App
settings → Secrets**:

```toml
DATABASE_URL = "mysql+pymysql://usuario:senha@host:3306/festa_ifc"
```

## Cadastros

- **Alimentos:** nome, descrição e preço de venda.
- **Ingredientes:** nome, unidade e observações.
- **Fornecedores:** contato e dados de comunicação.
- **Doações:** fornecedor, ingrediente, quantidade e data da doação.
- **Alimentos e ingredientes:** ingredientes e quantidades previstos para cada
  alimento.
- **Equipe:** pessoas voluntárias, classificadas como estudante, responsável
  por estudante ou servidor.

Cada cadastro tem operações para criar, consultar, atualizar e excluir.
Relações vinculadas são excluídas junto com o alimento, ingrediente ou
fornecedor correspondente.
