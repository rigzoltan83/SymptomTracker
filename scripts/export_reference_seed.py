import json
import sys
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(
    __file__
).resolve().parent.parent

ENV_FILE = (
    BASE_DIR
    / ".env"
)

load_dotenv(
    ENV_FILE
)

if str(BASE_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BASE_DIR),
    )


from app import create_app
from app.models import (
    BodyPart,
    Ingredient,
    IngredientRiskComponent,
    Medication,
    RiskComponent,
    SymptomType,
)


OUTPUT_FILE = (
    BASE_DIR
    / "seed"
    / "reference_data.json"
)


def translations_for(item):
    result = {}

    for translation in sorted(
        item.translations,
        key=lambda row: row.language_code,
    ):
        data = {
            "name": translation.name,
        }

        if hasattr(
            translation,
            "description",
        ):
            data["description"] = (
                translation.description
            )

        result[
            translation.language_code
        ] = data

    return result


def main():
    app = create_app()

    with app.app_context():
        ingredients = (
            Ingredient.query
            .order_by(Ingredient.id)
            .all()
        )

        risk_components = (
            RiskComponent.query
            .order_by(RiskComponent.id)
            .all()
        )

        symptom_types = (
            SymptomType.query
            .order_by(SymptomType.id)
            .all()
        )

        body_parts = (
            BodyPart.query
            .order_by(BodyPart.id)
            .all()
        )

        medications = (
            Medication.query
            .order_by(Medication.id)
            .all()
        )

        ingredient_risks = (
            IngredientRiskComponent.query
            .order_by(
                IngredientRiskComponent.id
            )
            .all()
        )

        data = {
            "format_version": 1,

            "ingredients": [
                {
                    "base_name": item.name,
                    "translations":
                        translations_for(item),
                }
                for item in ingredients
            ],

            "risk_components": [
                {
                    "base_name": item.name,
                    "category":
                        item.category,
                    "description":
                        item.description,
                    "active":
                        item.active,
                    "translations":
                        translations_for(item),
                }
                for item in risk_components
            ],

            "ingredient_risk_components": [
                {
                    "ingredient":
                        row.ingredient.name,
                    "risk_component":
                        row.risk_component.name,
                    "confidence":
                        row.confidence,
                    "notes":
                        row.notes,
                }
                for row in ingredient_risks
            ],

            "symptom_types": [
                {
                    "base_name": item.name,
                    "active":
                        item.active,
                    "translations":
                        translations_for(item),
                }
                for item in symptom_types
            ],

            "body_parts": [
                {
                    "base_name": item.name,
                    "active":
                        item.active,
                    "translations":
                        translations_for(item),
                }
                for item in body_parts
            ],

            "medications": [
                {
                    "name":
                        item.name,
                    "active":
                        item.active,
                    "is_default":
                        item.is_default,
                }
                for item in medications
            ],
        }

        OUTPUT_FILE.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        print(
            "OK:",
            OUTPUT_FILE,
        )

        print(
            "ingredients:",
            len(
                data["ingredients"]
            ),
        )

        print(
            "risk_components:",
            len(
                data[
                    "risk_components"
                ]
            ),
        )

        print(
            "ingredient_risk_components:",
            len(
                data[
                    "ingredient_risk_components"
                ]
            ),
        )

        print(
            "symptom_types:",
            len(
                data["symptom_types"]
            ),
        )

        print(
            "body_parts:",
            len(
                data["body_parts"]
            ),
        )

        print(
            "medications:",
            len(
                data["medications"]
            ),
        )


if __name__ == "__main__":
    main()
