from flask import session


SUPPORTED_LANGUAGES = {
    "hu": "Magyar",
    "en": "English",
}

DEFAULT_LANGUAGE = "hu"


TRANSLATIONS = {
    "hu": {
        "index.subtitle": "Esemény rögzítése",
        "index.medication": "Gyógyszer",
        "index.food_drink": "Étel / ital",
        "index.symptom": "Tünet",
        "index.previous_events": "Korábbi események",
        "index.analysis": "Elemzés",
        "index.management": "Kezelés",
        "index.export": "Export",
        "index.recent_events": "Legutóbbi események",
        "index.no_events": "Még nincs rögzített esemény.",
        "language.hu": "Magyar",
        "language.en": "English",
        "common.back": "Vissza",
        "common.save": "Mentés",
        "common.cancel": "Mégse",
        "common.search": "Keresés",
        "common.active": "Aktív",
        "common.inactive": "Inaktív",
        "common.all": "Mind",
    },
    "en": {
        "index.subtitle": "Log an event",
        "index.medication": "Medication",
        "index.food_drink": "Food / drink",
        "index.symptom": "Symptom",
        "index.previous_events": "Previous events",
        "index.analysis": "Analysis",
        "index.management": "Management",
        "index.export": "Export",
        "index.recent_events": "Recent events",
        "index.no_events": "No events have been recorded yet.",
        "language.hu": "Hungarian",
        "language.en": "English",
        "common.back": "Back",
        "common.save": "Save",
        "common.cancel": "Cancel",
        "common.search": "Search",
        "common.active": "Active",
        "common.inactive": "Inactive",
        "common.all": "All",
    },
}


def normalize_language(language_code):
    if not language_code:
        return DEFAULT_LANGUAGE

    language_code = (
        str(language_code)
        .strip()
        .lower()
    )

    if language_code not in SUPPORTED_LANGUAGES:
        return DEFAULT_LANGUAGE

    return language_code


def get_current_language():
    return normalize_language(
        session.get(
            "language",
            DEFAULT_LANGUAGE,
        )
    )


def set_current_language(language_code):
    language_code = normalize_language(
        language_code
    )

    session["language"] = language_code

    return language_code


def translate(key, **values):
    language_code = get_current_language()

    language_translations = (
        TRANSLATIONS.get(
            language_code,
            {},
        )
    )

    text = language_translations.get(key)

    if text is None:
        text = TRANSLATIONS[
            DEFAULT_LANGUAGE
        ].get(
            key,
            key,
        )

    if values:
        return text.format(**values)

    return text
