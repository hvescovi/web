from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from party_organizer.models import (
    Base,
    Donation,
    Food,
    FoodIngredient,
    Ingredient,
    Supplier,
)


def test_food_recipe_and_donation_persist_and_cascade() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        food = Food(name="Bolo", sale_price=Decimal("5.00"))
        ingredient = Ingredient(name="Farinha", unit="kg")
        supplier = Supplier(name="Mercado local")
        db.add_all([food, ingredient, supplier])
        db.flush()
        db.add_all(
            [
                FoodIngredient(
                    food_id=food.id,
                    ingredient_id=ingredient.id,
                    quantity=Decimal("0.500"),
                ),
                Donation(
                    supplier_id=supplier.id,
                    ingredient_id=ingredient.id,
                    quantity=Decimal("2.000"),
                    donated_at=date(2026, 11, 9),
                ),
            ]
        )
        db.commit()

        assert db.scalar(select(Food).where(Food.name == "Bolo")).sale_price == Decimal(
            "5.00"
        )
        assert len(db.scalars(select(FoodIngredient)).all()) == 1
        assert len(db.scalars(select(Donation)).all()) == 1

        db.delete(ingredient)
        db.commit()
        assert db.scalars(select(FoodIngredient)).all() == []
        assert db.scalars(select(Donation)).all() == []
