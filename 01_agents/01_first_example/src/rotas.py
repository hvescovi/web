import logging
from typing import Any, Callable

from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from . import servicos

logger = logging.getLogger(__name__)


def _resposta(detalhes: Any, status: int = 200):
    return jsonify({"resultado": "ok", "detalhes": detalhes}), status


def _erro(mensagem: str, status: int):
    return jsonify({"resultado": "erro", "detalhes": mensagem}), status


def _dados_requisicao() -> dict[str, Any]:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("O corpo da requisição deve ser um objeto JSON.")
    return data


def _executar(operacao: Callable[[], Any], status: int = 200):
    try:
        return _resposta(operacao(), status)
    except ValueError as error:
        return _erro(str(error), 400)
    except LookupError as error:
        return _erro(str(error), 404)
    except SQLAlchemyError:
        logger.exception("Falha ao acessar o banco de dados.")
        return _erro("Erro ao acessar o banco de dados.", 500)
    except Exception:
        logger.exception("Erro inesperado ao processar a requisição.")
        return _erro("Erro interno do servidor.", 500)


def registrar_rotas(app: Flask) -> None:
    @app.post("/criar-tabelas")
    def criar_tabelas():
        def operacao():
            servicos.criar_tabelas()
            return {"mensagem": "Tabelas criadas com sucesso."}

        return _executar(operacao)

    @app.route("/pessoas", methods=["GET", "POST"])
    def pessoas():
        if request.method == "GET":
            return _executar(servicos.listar_pessoas)
        return _executar(lambda: servicos.criar_pessoa(_dados_requisicao()), 201)

    @app.route("/pessoas/<int:pessoa_id>", methods=["GET", "PUT", "DELETE"])
    def pessoa(pessoa_id: int):
        if request.method == "GET":
            return _executar(lambda: servicos.obter_pessoa(pessoa_id))
        if request.method == "PUT":
            return _executar(lambda: servicos.atualizar_pessoa(pessoa_id, _dados_requisicao()))

        def excluir():
            servicos.excluir_pessoa(pessoa_id)
            return {"mensagem": "Pessoa excluída com sucesso."}

        return _executar(excluir)

    @app.route("/celulares", methods=["GET", "POST"])
    def celulares():
        if request.method == "GET":
            pessoa_id_arg = request.args.get("pessoa_id")
            if pessoa_id_arg is None:
                return _executar(servicos.listar_celulares)
            try:
                pessoa_id = int(pessoa_id_arg)
            except ValueError:
                return _erro("O parâmetro 'pessoa_id' deve ser um número válido.", 400)
            return _executar(lambda: servicos.listar_celulares(pessoa_id))
        return _executar(lambda: servicos.criar_celular(_dados_requisicao()), 201)

    @app.route("/celulares/<int:celular_id>", methods=["GET", "PUT", "DELETE"])
    def celular(celular_id: int):
        if request.method == "GET":
            return _executar(lambda: servicos.obter_celular(celular_id))
        if request.method == "PUT":
            return _executar(lambda: servicos.atualizar_celular(celular_id, _dados_requisicao()))

        def excluir():
            servicos.excluir_celular(celular_id)
            return {"mensagem": "Celular excluído com sucesso."}

        return _executar(excluir)

    @app.errorhandler(HTTPException)
    def tratar_http_error(error: HTTPException):
        return _erro(error.description, error.code or 500)
