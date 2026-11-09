from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

import streamlit as st
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from party_organizer.database import SessionLocal, init_db
from party_organizer.models import (
    Donation,
    Food,
    FoodIngredient,
    Ingredient,
    Supplier,
    Worker,
)


@dataclass(frozen=True)
class Field:
    name: str
    label: str
    kind: str = "text"
    required: bool = True
    reference: type | None = None
    choices: tuple[tuple[str, str], ...] = ()
    default: Any = None


@dataclass(frozen=True)
class EntityPage:
    key: str
    title: str
    model: type
    fields: tuple[Field, ...]
    columns: tuple[tuple[str, str], ...]
    choice_label: str


PAGES = (
    EntityPage(
        "foods",
        "Alimentos",
        Food,
        (
            Field("name", "Nome"),
            Field("description", "Descrição", "textarea", required=False),
            Field("sale_price", "Preço de venda (R$)", "decimal"),
        ),
        (("Nome", "name"), ("Descrição", "description"), ("Preço (R$)", "sale_price")),
        "name",
    ),
    EntityPage(
        "ingredients",
        "Ingredientes",
        Ingredient,
        (
            Field("name", "Nome"),
            Field(
                "unit",
                "Unidade",
                "select",
                choices=(
                    ("un", "Unidade"),
                    ("kg", "Quilograma"),
                    ("g", "Grama"),
                    ("L", "Litro"),
                    ("ml", "Mililitro"),
                    ("porção", "Porção"),
                ),
            ),
            Field("notes", "Observações", "textarea", required=False),
        ),
        (("Nome", "name"), ("Unidade", "unit"), ("Observações", "notes")),
        "name",
    ),
    EntityPage(
        "suppliers",
        "Fornecedores",
        Supplier,
        (
            Field("name", "Nome do fornecedor"),
            Field("contact_name", "Pessoa de contato", required=False),
            Field("phone", "Telefone", required=False),
            Field("email", "E-mail", required=False),
            Field("notes", "Observações", "textarea", required=False),
        ),
        (
            ("Fornecedor", "name"),
            ("Contato", "contact_name"),
            ("Telefone", "phone"),
            ("E-mail", "email"),
        ),
        "name",
    ),
    EntityPage(
        "donations",
        "Doações",
        Donation,
        (
            Field("supplier_id", "Fornecedor", "reference", reference=Supplier),
            Field("ingredient_id", "Ingrediente", "reference", reference=Ingredient),
            Field("quantity", "Quantidade doada", "decimal"),
            Field("donated_at", "Data da doação", "date", default=date.today),
            Field("notes", "Observações", "textarea", required=False),
        ),
        (
            ("Fornecedor", "supplier.name"),
            ("Ingrediente", "ingredient.name"),
            ("Quantidade", "quantity"),
            ("Data", "donated_at"),
            ("Observações", "notes"),
        ),
        "ingredient.name",
    ),
    EntityPage(
        "recipes",
        "Alimentos e ingredientes",
        FoodIngredient,
        (
            Field("food_id", "Alimento", "reference", reference=Food),
            Field("ingredient_id", "Ingrediente", "reference", reference=Ingredient),
            Field("quantity", "Quantidade por alimento", "decimal"),
        ),
        (
            ("Alimento", "food.name"),
            ("Ingrediente", "ingredient.name"),
            ("Quantidade", "quantity"),
        ),
        "food.name",
    ),
    EntityPage(
        "workers",
        "Equipe",
        Worker,
        (
            Field("name", "Nome"),
            Field(
                "category",
                "Categoria",
                "select",
                choices=(
                    ("Estudante", "Estudante"),
                    ("Responsável por estudante", "Responsável por estudante"),
                    ("Servidor", "Servidor"),
                ),
            ),
            Field("phone", "Telefone", required=False),
            Field("email", "E-mail", required=False),
            Field("notes", "Observações", "textarea", required=False),
        ),
        (
            ("Nome", "name"),
            ("Categoria", "category"),
            ("Telefone", "phone"),
            ("E-mail", "email"),
            ("Observações", "notes"),
        ),
        "name",
    ),
)


def _format_value(value: Any) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    return str(value)


def _get_path_value(record: object, path: str) -> Any:
    value: Any = record
    for part in path.split("."):
        value = getattr(value, part)
    return value


def _display_record(page: EntityPage, record: object) -> str:
    return f"#{record.id} · {_get_path_value(record, page.choice_label)}"


def _field_input(
    db: Session,
    page: EntityPage,
    field: Field,
    *,
    key: str,
    current: Any = None,
) -> Any:
    if field.kind == "reference":
        assert field.reference is not None
        records = db.scalars(select(field.reference).order_by(field.reference.name)).all()
        if not records:
            st.warning(f"Cadastre primeiro um registro para “{field.label}”.")
            return None
        ids = [record.id for record in records]
        selected = current if current in ids else ids[0]
        labels = {record.id: record.name for record in records}
        return st.selectbox(
            field.label,
            options=ids,
            index=ids.index(selected),
            format_func=lambda record_id: labels[record_id],
            key=key,
        )

    if field.kind == "select":
        values = [value for value, _label in field.choices]
        labels = dict(field.choices)
        default = current if current in values else field.default
        if default is None:
            default = values[0]
        return st.selectbox(
            field.label,
            options=values,
            index=values.index(default),
            format_func=lambda value: labels[value],
            key=key,
        )

    if field.kind == "textarea":
        return st.text_area(
            field.label, value=current or "", key=key, height=90
        )
    if field.kind == "decimal":
        value = float(current) if current is not None else float(field.default or 0)
        return st.number_input(
            field.label,
            min_value=0.0,
            value=value,
            step=0.01,
            format="%.2f",
            key=key,
        )
    if field.kind == "date":
        value = current or (field.default() if callable(field.default) else field.default)
        return st.date_input(field.label, value=value or date.today(), key=key)

    return st.text_input(
        field.label,
        value=current or "",
        key=key,
        help="Campo obrigatório" if field.required else None,
    )


def _field_value(field: Field, value: Any) -> Any:
    if field.kind == "decimal":
        return Decimal(str(value))
    if field.kind in {"text", "textarea"}:
        value = value.strip() if value else ""
        if not field.required and not value:
            return None
    return value


def _has_missing_required_fields(page: EntityPage, values: dict[str, Any]) -> bool:
    return any(
        values[field.name] is None
        or (isinstance(values[field.name], str) and not values[field.name].strip())
        for field in page.fields
        if field.required
    )


def _save(db: Session, page: EntityPage, record: object, message: str) -> None:
    try:
        db.add(record)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        st.error(
            "Não foi possível salvar. Verifique se o nome já existe e se os "
            f"registros relacionados são válidos. Detalhe: {error.orig}"
        )
        return
    except SQLAlchemyError as error:
        db.rollback()
        st.error(f"Erro ao salvar {page.title.lower()}: {error}")
        return

    st.session_state["flash_message"] = message
    st.rerun()


def _render_records(db: Session, page: EntityPage) -> list[object]:
    records = db.scalars(select(page.model).order_by(page.model.id)).all()
    if not records:
        st.info("Nenhum registro cadastrado.")
        return records

    rows = []
    for record in records:
        row = {"ID": record.id}
        for label, path in page.columns:
            row[label] = _format_value(_get_path_value(record, path))
        rows.append(row)
    st.dataframe(rows, hide_index=True, width="stretch")
    return records


def _render_create(db: Session, page: EntityPage) -> None:
    with st.form(f"{page.key}-create-form"):
        values = {
            field.name: _field_input(
                db, page, field, key=f"{page.key}-create-{field.name}"
            )
            for field in page.fields
        }
        submitted = st.form_submit_button("Criar")

    if submitted:
        if _has_missing_required_fields(page, values):
            st.error("Preencha os campos obrigatórios e cadastre as opções relacionadas.")
            return
        record = page.model(
            **{
                field.name: _field_value(field, values[field.name])
                for field in page.fields
            }
        )
        _save(db, page, record, f"Registro criado em {page.title.lower()}.")


def _render_update(db: Session, page: EntityPage, records: list[object]) -> None:
    if not records:
        st.info("Cadastre um registro antes de atualizar.")
        return

    record_ids = [record.id for record in records]
    selected_id = st.selectbox(
        "Registro para atualizar",
        options=record_ids,
        format_func=lambda record_id: _display_record(
            page, next(item for item in records if item.id == record_id)
        ),
        key=f"{page.key}-update-record",
    )
    record = next(item for item in records if item.id == selected_id)
    with st.form(f"{page.key}-update-form-{selected_id}"):
        values = {
            field.name: _field_input(
                db,
                page,
                field,
                key=f"{page.key}-update-{selected_id}-{field.name}",
                current=getattr(record, field.name),
            )
            for field in page.fields
        }
        submitted = st.form_submit_button("Salvar alterações")

    if submitted:
        if _has_missing_required_fields(page, values):
            st.error("Preencha os campos obrigatórios e cadastre as opções relacionadas.")
            return
        for field in page.fields:
            setattr(record, field.name, _field_value(field, values[field.name]))
        _save(db, page, record, f"Registro atualizado em {page.title.lower()}.")


def _render_delete(db: Session, page: EntityPage, records: list[object]) -> None:
    if not records:
        st.info("Não há registros para excluir.")
        return

    selected_id = st.selectbox(
        "Registro para excluir",
        options=[record.id for record in records],
        format_func=lambda record_id: _display_record(
            page, next(item for item in records if item.id == record_id)
        ),
        key=f"{page.key}-delete-record",
    )
    if st.button("Excluir registro", type="secondary", key=f"{page.key}-delete-button"):
        record = next(item for item in records if item.id == selected_id)
        try:
            db.delete(record)
            db.commit()
        except SQLAlchemyError as error:
            db.rollback()
            st.error(f"Erro ao excluir {page.title.lower()}: {error}")
            return
        st.session_state["flash_message"] = f"Registro excluído de {page.title.lower()}."
        st.rerun()


def _render_crud(db: Session, page: EntityPage) -> None:
    st.header(page.title)
    st.caption("Crie, consulte, atualize ou exclua registros.")
    records = _render_records(db, page)
    create_tab, update_tab, delete_tab = st.tabs(["Criar", "Atualizar", "Excluir"])
    with create_tab:
        _render_create(db, page)
    with update_tab:
        _render_update(db, page, records)
    with delete_tab:
        _render_delete(db, page, records)


def _render_dashboard(db: Session) -> None:
    st.title("Organização da festa")
    st.write(
        "Planeje os alimentos e preços, acompanhe os insumos doados e organize "
        "fornecedores e equipe da festa do IFC Campus Blumenau."
    )
    summaries = (
        ("Alimentos", Food),
        ("Ingredientes", Ingredient),
        ("Fornecedores", Supplier),
        ("Doações", Donation),
        ("Equipe", Worker),
    )
    columns = st.columns(len(summaries))
    for column, (label, model) in zip(columns, summaries):
        total = db.scalar(select(func.count()).select_from(model)) or 0
        column.metric(label, total)
    st.subheader("Comece por aqui")
    st.markdown(
        "- Cadastre os **alimentos** e seus preços de venda.\n"
        "- Cadastre **ingredientes** e **fornecedores**; registre cada doação.\n"
        "- Relacione ingredientes aos alimentos e cadastre as pessoas da **equipe**."
    )


def main() -> None:
    st.set_page_config(page_title="Festa IFC", page_icon="🎉", layout="wide")
    init_db()

    st.sidebar.title("Festa IFC")
    options = ["Visão geral", *(page.title for page in PAGES)]
    selected = st.sidebar.radio("Menu", options)

    flash_message = st.session_state.pop("flash_message", None)
    if flash_message:
        st.success(flash_message)

    with SessionLocal() as db:
        if selected == "Visão geral":
            _render_dashboard(db)
        else:
            page = next(page for page in PAGES if page.title == selected)
            _render_crud(db, page)


if __name__ == "__main__":
    main()
