from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import (
    Food,
    FoodRiskComponent,
    IngredientRiskComponent,
)


def sync_food(food):
    ingredient_ids = {
        item.ingredient_id
        for item in food.ingredients
    }

    suggested_ids = set()

    if ingredient_ids:
        ingredient_risks = (
            IngredientRiskComponent.query
            .filter(
                IngredientRiskComponent.ingredient_id.in_(
                    ingredient_ids
                )
            )
            .all()
        )

        suggested_ids = {
            item.risk_component_id
            for item in ingredient_risks
        }

    existing = {
        item.risk_component_id: item
        for item in food.risk_components
    }

    created = 0
    removed = 0
    kept = 0

    for risk_component_id in sorted(
        suggested_ids
    ):
        existing_item = existing.get(
            risk_component_id
        )

        if existing_item is not None:
            # A meglévő enabled állapotot
            # szándékosan megtartjuk.
            kept += 1
            continue

        food.risk_components.append(
            FoodRiskComponent(
                risk_component_id=(
                    risk_component_id
                ),
                source="automatic",
                enabled=True,
            )
        )

        created += 1

    for risk_component_id, item in (
        existing.items()
    ):
        if risk_component_id not in suggested_ids:
            db.session.delete(
                item
            )

            removed += 1

    return created, removed, kept


def main():
    app = create_app()

    with app.app_context():
        foods = (
            Food.query
            .order_by(Food.id)
            .all()
        )

        total_created = 0
        total_removed = 0
        total_kept = 0

        print(
            f"Feldolgozandó ételek: "
            f"{len(foods)}"
        )

        print()

        for food in foods:
            created, removed, kept = (
                sync_food(food)
            )

            total_created += created
            total_removed += removed
            total_kept += kept

            print(
                f"{food.id}: {food.name} "
                f"| új: {created} "
                f"| törölt: {removed} "
                f"| megtartott: {kept}"
            )

        db.session.commit()

        print()
        print("----- ÖSSZESÍTÉS -----")

        print(
            f"Új kapcsolat: "
            f"{total_created}"
        )

        print(
            f"Törölt, már nem releváns: "
            f"{total_removed}"
        )

        print(
            f"Megtartott meglévő: "
            f"{total_kept}"
        )


if __name__ == "__main__":
    main()
