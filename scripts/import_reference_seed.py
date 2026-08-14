import json
import os
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

SEED_FILE = (
    BASE_DIR
    / "seed"
    / "reference_data.json"
)

if not os.environ.get(
    "DATABASE_URL"
):
    load_dotenv(
        ENV_FILE
    )

if str(BASE_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BASE_DIR),
    )


from app import create_app, db
from app.models import (
    BodyPart,
    BodyPartTranslation,
    Ingredient,
    IngredientRiskComponent,
    IngredientTranslation,
    Medication,
    RiskComponent,
    RiskComponentTranslation,
    SymptomType,
    SymptomTypeTranslation,
)


def load_seed():
    return json.loads(
        SEED_FILE.read_text(
            encoding="utf-8"
        )
    )


def upsert_translation(
    model,
    parent_field,
    parent_id,
    language_code,
    name,
    description=None,
):
    filters = {
        parent_field: parent_id,
        "language_code": language_code,
    }

    row = (
        model.query
        .filter_by(
            **filters
        )
        .first()
    )

    if row is None:
        kwargs = {
            parent_field: parent_id,
            "language_code": language_code,
            "name": name,
        }

        if hasattr(
            model,
            "description",
        ):
            kwargs["description"] = (
                description
            )

        row = model(
            **kwargs
        )

        db.session.add(
            row
        )

    else:
        row.name = name

        if hasattr(
            row,
            "description",
        ):
            row.description = (
                description
            )

    return row


def import_ingredients(data):
    result = {}

    for item in data:
        base_name = item[
            "base_name"
        ]

        row = (
            Ingredient.query
            .filter_by(
                name=base_name
            )
            .first()
        )

        if row is None:
            row = Ingredient(
                name=base_name
            )

            db.session.add(
                row
            )

            db.session.flush()

        result[
            base_name
        ] = row

        for (
            language_code,
            translation,
        ) in item[
            "translations"
        ].items():
            upsert_translation(
                IngredientTranslation,
                "ingredient_id",
                row.id,
                language_code,
                translation["name"],
            )

    return result


def import_risk_components(data):
    result = {}

    for item in data:
        base_name = item[
            "base_name"
        ]

        row = (
            RiskComponent.query
            .filter_by(
                name=base_name
            )
            .first()
        )

        if row is None:
            row = RiskComponent(
                name=base_name,
                category=item[
                    "category"
                ],
                description=item.get(
                    "description"
                ),
                active=item.get(
                    "active",
                    True,
                ),
            )

            db.session.add(
                row
            )

            db.session.flush()

        else:
            row.category = item[
                "category"
            ]

            row.description = item.get(
                "description"
            )

            row.active = item.get(
                "active",
                True,
            )

        result[
            base_name
        ] = row

        for (
            language_code,
            translation,
        ) in item[
            "translations"
        ].items():
            upsert_translation(
                RiskComponentTranslation,
                "risk_component_id",
                row.id,
                language_code,
                translation["name"],
                translation.get(
                    "description"
                ),
            )

    return result


def import_ingredient_risks(
    data,
    ingredients,
    risk_components,
):
    for item in data:
        ingredient = ingredients[
            item["ingredient"]
        ]

        risk_component = (
            risk_components[
                item[
                    "risk_component"
                ]
            ]
        )

        row = (
            IngredientRiskComponent.query
            .filter_by(
                ingredient_id=(
                    ingredient.id
                ),
                risk_component_id=(
                    risk_component.id
                ),
            )
            .first()
        )

        if row is None:
            row = IngredientRiskComponent(
                ingredient_id=(
                    ingredient.id
                ),
                risk_component_id=(
                    risk_component.id
                ),
                confidence=item[
                    "confidence"
                ],
                notes=item.get(
                    "notes"
                ),
            )

            db.session.add(
                row
            )

        else:
            row.confidence = item[
                "confidence"
            ]

            row.notes = item.get(
                "notes"
            )


def import_symptom_types(data):
    for item in data:
        base_name = item[
            "base_name"
        ]

        row = (
            SymptomType.query
            .filter_by(
                name=base_name
            )
            .first()
        )

        if row is None:
            row = SymptomType(
                name=base_name,
                active=item.get(
                    "active",
                    True,
                ),
            )

            db.session.add(
                row
            )

            db.session.flush()

        else:
            row.active = item.get(
                "active",
                True,
            )

        for (
            language_code,
            translation,
        ) in item[
            "translations"
        ].items():
            upsert_translation(
                SymptomTypeTranslation,
                "symptom_type_id",
                row.id,
                language_code,
                translation["name"],
            )


def import_body_parts(data):
    for item in data:
        base_name = item[
            "base_name"
        ]

        row = (
            BodyPart.query
            .filter_by(
                name=base_name
            )
            .first()
        )

        if row is None:
            row = BodyPart(
                name=base_name,
                active=item.get(
                    "active",
                    True,
                ),
            )

            db.session.add(
                row
            )

            db.session.flush()

        else:
            row.active = item.get(
                "active",
                True,
            )

        for (
            language_code,
            translation,
        ) in item[
            "translations"
        ].items():
            upsert_translation(
                BodyPartTranslation,
                "body_part_id",
                row.id,
                language_code,
                translation["name"],
            )


def import_medications(data):
    default_rows = []

    for item in data:
        row = (
            Medication.query
            .filter_by(
                name=item["name"]
            )
            .first()
        )

        if row is None:
            row = Medication(
                name=item["name"],
                active=item.get(
                    "active",
                    True,
                ),
                is_default=False,
            )

            db.session.add(
                row
            )

        else:
            row.active = item.get(
                "active",
                True,
            )

            row.is_default = False

        if item.get(
            "is_default",
            False,
        ):
            default_rows.append(
                row
            )

    db.session.flush()

    if len(default_rows) > 1:
        raise RuntimeError(
            "A seed több alapértelmezett "
            "gyógyszert tartalmaz."
        )

    if default_rows:
        default_rows[
            0
        ].is_default = True


def main():
    data = load_seed()

    if data.get(
        "format_version"
    ) != 1:
        raise RuntimeError(
            "Nem támogatott seed formátum."
        )

    app = create_app()

    with app.app_context():
        try:
            ingredients = (
                import_ingredients(
                    data[
                        "ingredients"
                    ]
                )
            )

            risk_components = (
                import_risk_components(
                    data[
                        "risk_components"
                    ]
                )
            )

            import_ingredient_risks(
                data[
                    "ingredient_risk_components"
                ],
                ingredients,
                risk_components,
            )

            import_symptom_types(
                data[
                    "symptom_types"
                ]
            )

            import_body_parts(
                data[
                    "body_parts"
                ]
            )

            import_medications(
                data[
                    "medications"
                ]
            )

            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        print(
            "OK: reference seed import kész."
        )


if __name__ == "__main__":
    main()
