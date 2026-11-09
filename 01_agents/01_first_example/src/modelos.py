from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .configuracoes import Base


class Pessoa(Base):
    __tablename__ = "pessoas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    celulares: Mapped[list["Celular"]] = relationship(
        back_populates="pessoa",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Celular(Base):
    __tablename__ = "celulares"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(40), nullable=False)
    modelo: Mapped[str] = mapped_column(String(120), nullable=False)
    marca: Mapped[str] = mapped_column(String(80), nullable=False)
    pessoa_id: Mapped[int] = mapped_column(
        ForeignKey("pessoas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pessoa: Mapped[Pessoa] = relationship(back_populates="celulares")

