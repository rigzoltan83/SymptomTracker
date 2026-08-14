from app import db
from app.i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    get_current_language,
    normalize_language,
)
from app.models import (
    BodyPart,
    BodyPartTranslation,
    Ingredient,
    IngredientTranslation,
    RiskComponent,
    RiskComponentTranslation,
    SymptomType,
    SymptomTypeTranslation,
)


REFERENCE_CONFIG = {
    Ingredient: {
        "translation_model": IngredientTranslation,
        "foreign_key": "ingredient_id",
        "has_description": False,
    },
    RiskComponent: {
        "translation_model": RiskComponentTranslation,
        "foreign_key": "risk_component_id",
        "has_description": True,
    },
    SymptomType: {
        "translation_model": SymptomTypeTranslation,
        "foreign_key": "symptom_type_id",
        "has_description": False,
    },
    BodyPart: {
        "translation_model": BodyPartTranslation,
        "foreign_key": "body_part_id",
        "has_description": False,
    },
}


def _get_config(entity):
    config = REFERENCE_CONFIG.get(
        type(entity)
    )

    if config is None:
        raise ValueError(
            "Nem támogatott többnyelvű törzsadat."
        )

    return config


def get_reference_translation(
    entity,
    language_code=None,
):
    if entity is None:
        return None

    language_code = normalize_language(
        language_code
        or get_current_language()
    )

    for translation in entity.translations:
        if (
            translation.language_code
            == language_code
        ):
            return translation

    return None


def get_reference_name(
    entity,
    language_code=None,
):
    if entity is None:
        return ""

    translation = get_reference_translation(
        entity,
        language_code,
    )

    if translation is not None:
        return translation.name

    fallback = get_reference_translation(
        entity,
        DEFAULT_LANGUAGE,
    )

    if fallback is not None:
        return fallback.name

    return entity.name


def get_reference_description(
    entity,
    language_code=None,
):
    if entity is None:
        return None

    config = _get_config(entity)

    if not config["has_description"]:
        return None

    translation = get_reference_translation(
        entity,
        language_code,
    )

    if (
        translation is not None
        and translation.description is not None
    ):
        return translation.description

    fallback = get_reference_translation(
        entity,
        DEFAULT_LANGUAGE,
    )

    if (
        fallback is not None
        and fallback.description is not None
    ):
        return fallback.description

    return entity.description


def create_reference_translations(
    entity,
    *,
    name,
    description=None,
):
    """
    Új törzsrekord létrehozásakor minden támogatott
    nyelvhez létrehozza a translation rekordot.

    Kezdetben mindegyik nyelv ugyanazt a felhasználó
    által megadott szöveget kapja.
    """

    config = _get_config(entity)

    if entity.id is None:
        db.session.flush()

    translation_model = config[
        "translation_model"
    ]

    foreign_key = config[
        "foreign_key"
    ]

    for language_code in SUPPORTED_LANGUAGES:
        values = {
            foreign_key: entity.id,
            "language_code": language_code,
            "name": name,
        }

        if config["has_description"]:
            values["description"] = (
                description or None
            )

        translation = translation_model(
            **values
        )

        db.session.add(
            translation
        )


def update_current_reference_translation(
    entity,
    *,
    name,
    description=None,
    language_code=None,
):
    """
    Csak az aktuális nyelvhez tartozó fordítást
    módosítja.

    Az alaprekord name mezőjét nem írja át.
    """

    config = _get_config(entity)

    language_code = normalize_language(
        language_code
        or get_current_language()
    )

    translation = get_reference_translation(
        entity,
        language_code,
    )

    if translation is None:
        translation_model = config[
            "translation_model"
        ]

        foreign_key = config[
            "foreign_key"
        ]

        values = {
            foreign_key: entity.id,
            "language_code": language_code,
            "name": name,
        }

        if config["has_description"]:
            values["description"] = (
                description or None
            )

        translation = translation_model(
            **values
        )

        db.session.add(
            translation
        )

    else:
        translation.name = name

        if config["has_description"]:
            translation.description = (
                description or None
            )

    return translation

def find_reference_by_name(
    model,
    name,
    language_code=None,
    exclude_id=None,
):
    """
    Törzsrekord keresése a megjelenített,
    aktuális nyelvű név alapján.

    Ha az adott nyelvhez nincs translation,
    az alap name mező a fallback.
    """

    config = REFERENCE_CONFIG.get(model)

    if config is None:
        raise ValueError(
            "Nem támogatott többnyelvű törzsadat."
        )

    normalized_name = str(name).strip()

    if not normalized_name:
        return None

    language_code = normalize_language(
        language_code
        or get_current_language()
    )

    translation_model = config[
        "translation_model"
    ]

    foreign_key = config[
        "foreign_key"
    ]

    translated_name = db.func.coalesce(
        translation_model.name,
        model.name,
    )

    query = (
        model.query
        .outerjoin(
            translation_model,
            db.and_(
                getattr(
                    translation_model,
                    foreign_key,
                ) == model.id,
                translation_model.language_code
                == language_code,
            ),
        )
        .filter(
            db.func.lower(
                translated_name
            ) == normalized_name.lower()
        )
    )

    if exclude_id is not None:
        query = query.filter(
            model.id != exclude_id
        )

    return query.first()

def reference_name_expression(
    model,
    language_code=None,
):
    config = REFERENCE_CONFIG.get(model)

    if config is None:
        raise ValueError(
            "Nem támogatott többnyelvű törzsadat."
        )

    language_code = normalize_language(
        language_code
        or get_current_language()
    )

    translation_model = config[
        "translation_model"
    ]

    foreign_key = config[
        "foreign_key"
    ]

    expression = db.func.coalesce(
        translation_model.name,
        model.name,
    )

    return (
        translation_model,
        foreign_key,
        language_code,
        expression,
    )


def apply_reference_name_join(
    query,
    model,
    language_code=None,
):
    (
        translation_model,
        foreign_key,
        language_code,
        expression,
    ) = reference_name_expression(
        model,
        language_code,
    )

    query = query.outerjoin(
        translation_model,
        db.and_(
            getattr(
                translation_model,
                foreign_key,
            ) == model.id,
            translation_model.language_code
            == language_code,
        ),
    )

    return query, expression

def order_reference_query(
    query,
    model,
    language_code=None,
):
    query, display_name = (
        apply_reference_name_join(
            query,
            model,
            language_code,
        )
    )

    return query.order_by(
        display_name
    )

def reference_name_matches(
    model,
    pattern,
    language_code=None,
):
    config = REFERENCE_CONFIG.get(model)

    if config is None:
        raise ValueError(
            "Nem támogatott többnyelvű törzsadat."
        )

    language_code = normalize_language(
        language_code
        or get_current_language()
    )

    translation_model = config[
        "translation_model"
    ]

    language_exists = model.translations.any(
        translation_model.language_code
        == language_code
    )

    translated_match = (
        model.translations.any(
            db.and_(
                translation_model.language_code
                == language_code,
                translation_model.name.ilike(
                    pattern
                ),
            )
        )
    )

    fallback_match = db.and_(
        ~language_exists,
        model.name.ilike(pattern),
    )

    return db.or_(
        translated_match,
        fallback_match,
    )


def reference_description_matches(
    model,
    pattern,
    language_code=None,
):
    config = REFERENCE_CONFIG.get(model)

    if (
        config is None
        or not config["has_description"]
    ):
        raise ValueError(
            "A törzsadatnak nincs fordítható leírása."
        )

    language_code = normalize_language(
        language_code
        or get_current_language()
    )

    translation_model = config[
        "translation_model"
    ]

    language_exists = model.translations.any(
        translation_model.language_code
        == language_code
    )

    translated_match = (
        model.translations.any(
            db.and_(
                translation_model.language_code
                == language_code,
                translation_model.description.ilike(
                    pattern
                ),
            )
        )
    )

    fallback_match = db.and_(
        ~language_exists,
        model.description.ilike(pattern),
    )

    return db.or_(
        translated_match,
        fallback_match,
    )
