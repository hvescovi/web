from unittest.mock import patch

import pytest

from src.configuracoes import create_app
from src.rotas import registrar_rotas


@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    registrar_rotas(app)
    return app.test_client()


def test_criar_tabelas_responde_no_formato_especificado(client):
    with patch("src.rotas.servicos.criar_tabelas") as criar:
        response = client.post("/criar-tabelas")

    assert response.status_code == 200
    assert response.get_json() == {
        "resultado": "ok",
        "detalhes": {"mensagem": "Tabelas criadas com sucesso."},
    }
    criar.assert_called_once_with()


def test_criar_pessoa_retorna_201(client):
    pessoa = {"id": 8, "nome": "Ana", "email": "ana@example.test", "telefone": None}
    with patch("src.rotas.servicos.criar_pessoa", return_value=pessoa) as criar:
        response = client.post(
            "/pessoas",
            json={"nome": "Ana", "email": "ana@example.test"},
        )

    assert response.status_code == 201
    assert response.get_json() == {"resultado": "ok", "detalhes": pessoa}
    criar.assert_called_once_with({"nome": "Ana", "email": "ana@example.test"})


def test_json_invalido_retorna_400_em_json(client):
    response = client.post("/pessoas", data="{", content_type="application/json")

    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["resultado"] == "erro"


def test_pessoa_inexistente_retorna_404(client):
    with patch("src.rotas.servicos.obter_pessoa", side_effect=LookupError("Pessoa não encontrada.")):
        response = client.get("/pessoas/999")

    assert response.status_code == 404
    assert response.get_json() == {
        "resultado": "erro",
        "detalhes": "Pessoa não encontrada.",
    }
