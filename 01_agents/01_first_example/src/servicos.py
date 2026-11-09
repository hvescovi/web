from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .configuracoes import Base, SessionLocal, engine
from .modelos import Celular, Pessoa


def _texto(data: dict[str, Any], campo: str, *, obrigatorio: bool = True) -> str | None:
    valor = data.get(campo)
    if valor is None or not str(valor).strip():
        if obrigatorio:
            raise ValueError(f"O campo '{campo}' é obrigatório.")
        return None
    return str(valor).strip()


def _pessoa_dict(pessoa: Pessoa) -> dict[str, Any]:
    return {
        "id": pessoa.id,
        "nome": pessoa.nome,
        "email": pessoa.email,
        "telefone": pessoa.telefone,
    }


def _celular_dict(celular: Celular) -> dict[str, Any]:
    return {
        "id": celular.id,
        "numero": celular.numero,
        "modelo": celular.modelo,
        "marca": celular.marca,
        "pessoa_id": celular.pessoa_id,
        "pessoa_nome": celular.pessoa.nome,
    }


def _salvar(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise ValueError(
            "Não foi possível salvar. Verifique se o e-mail já está cadastrado "
            "e se a pessoa informada existe."
        ) from error


def criar_tabelas() -> None:
    Base.metadata.create_all(bind=engine)


def listar_pessoas() -> list[dict[str, Any]]:
    with SessionLocal() as session:
        pessoas = session.scalars(select(Pessoa).order_by(Pessoa.nome)).all()
        return [_pessoa_dict(pessoa) for pessoa in pessoas]


def obter_pessoa(pessoa_id: int) -> dict[str, Any]:
    with SessionLocal() as session:
        pessoa = session.get(Pessoa, pessoa_id)
        if pessoa is None:
            raise LookupError("Pessoa não encontrada.")
        return _pessoa_dict(pessoa)


def criar_pessoa(data: dict[str, Any]) -> dict[str, Any]:
    pessoa = Pessoa(
        nome=_texto(data, "nome"),
        email=_texto(data, "email"),
        telefone=_texto(data, "telefone", obrigatorio=False),
    )
    with SessionLocal() as session:
        session.add(pessoa)
        _salvar(session)
        return _pessoa_dict(pessoa)


def atualizar_pessoa(pessoa_id: int, data: dict[str, Any]) -> dict[str, Any]:
    with SessionLocal() as session:
        pessoa = session.get(Pessoa, pessoa_id)
        if pessoa is None:
            raise LookupError("Pessoa não encontrada.")
        for campo in ("nome", "email"):
            if campo in data:
                setattr(pessoa, campo, _texto(data, campo))
        if "telefone" in data:
            pessoa.telefone = _texto(data, "telefone", obrigatorio=False)
        _salvar(session)
        return _pessoa_dict(pessoa)


def excluir_pessoa(pessoa_id: int) -> None:
    with SessionLocal() as session:
        pessoa = session.get(Pessoa, pessoa_id)
        if pessoa is None:
            raise LookupError("Pessoa não encontrada.")
        session.delete(pessoa)
        _salvar(session)


def listar_celulares(pessoa_id: int | None = None) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        consulta = select(Celular).order_by(Celular.id)
        if pessoa_id is not None:
            consulta = consulta.where(Celular.pessoa_id == pessoa_id)
        celulares = session.scalars(consulta).all()
        return [_celular_dict(celular) for celular in celulares]


def obter_celular(celular_id: int) -> dict[str, Any]:
    with SessionLocal() as session:
        celular = session.get(Celular, celular_id)
        if celular is None:
            raise LookupError("Celular não encontrado.")
        return _celular_dict(celular)


def criar_celular(data: dict[str, Any]) -> dict[str, Any]:
    celular = Celular(
        numero=_texto(data, "numero"),
        modelo=_texto(data, "modelo"),
        marca=_texto(data, "marca"),
        pessoa_id=_pessoa_id(data),
    )
    with SessionLocal() as session:
        if session.get(Pessoa, celular.pessoa_id) is None:
            raise LookupError("Pessoa não encontrada.")
        session.add(celular)
        _salvar(session)
        return _celular_dict(celular)


def atualizar_celular(celular_id: int, data: dict[str, Any]) -> dict[str, Any]:
    with SessionLocal() as session:
        celular = session.get(Celular, celular_id)
        if celular is None:
            raise LookupError("Celular não encontrado.")
        for campo in ("numero", "modelo", "marca"):
            if campo in data:
                setattr(celular, campo, _texto(data, campo))
        if "pessoa_id" in data:
            celular.pessoa_id = _pessoa_id(data)
            if session.get(Pessoa, celular.pessoa_id) is None:
                raise LookupError("Pessoa não encontrada.")
        _salvar(session)
        return _celular_dict(celular)


def excluir_celular(celular_id: int) -> None:
    with SessionLocal() as session:
        celular = session.get(Celular, celular_id)
        if celular is None:
            raise LookupError("Celular não encontrado.")
        session.delete(celular)
        _salvar(session)


def _pessoa_id(data: dict[str, Any]) -> int:
    try:
        pessoa_id = int(data["pessoa_id"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("O campo 'pessoa_id' deve ser um número válido.") from error
    if pessoa_id < 1:
        raise ValueError("O campo 'pessoa_id' deve ser um número válido.")
    return pessoa_id
