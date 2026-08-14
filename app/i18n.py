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


TRANSLATIONS["hu"].update({
    "events.title": "Események",
    "events.results": "{count} találat",
    "events.search_placeholder": "🔎 Étel, összetevő, tünet...",
    "events.all_types": "Minden típus",
    "events.medication": "Gyógyszer",
    "events.food": "Étel / ital",
    "events.symptom": "Tünet",
    "events.filter": "Keresés / Szűrés",
    "events.event_count": "{count} esemény",
    "events.ongoing": "még tart",
    "events.edit": "Szerkesztés",
    "events.deactivate": "Inaktiválás",
    "events.activate": "Aktiválás",
    "events.no_results": "Nincs a szűrésnek megfelelő esemény.",
    "events.previous_50": "Előző 50",
    "events.next_50": "Következő 50",
    "common.home": "Főoldal",
    "common.management": "Kezelés",
    "common.name": "Név",
    "common.brand": "Márka / gyártó",
    "common.ingredients": "Összetevők",
    "common.notes": "Megjegyzés",
    "common.optional": "Opcionális",
    "common.optional_dots": "Opcionális...",
    "common.date_time": "Dátum és idő",
    "common.amount": "Mennyiség",
    "common.photo_take": "Fotó készítése",
    "common.image_select": "Kép kiválasztása",
    "common.current_images": "Jelenlegi képek",
    "food.new_title": "Új étel / ital",
    "food.new_heading": "Új étel",
    "food.name_example": "pl. Sonkás pizza",
    "food.no_ingredients": "Még nincs összetevő a törzsben.",
    "food.add_ingredient": "Új összetevő hozzáadása",
    "food.photo": "Fotó az ételről / csomagolásról",
    "food.multiple_photos": "Több fotót is készíthetsz egymás után.",
    "food.photos_preview": "A képek mentés előtt itt megjelennek.",
    "food.notes": "Megjegyzés az ételhez",
    "food.save": "Étel mentése",
    "food.edit_title": "Étel szerkesztése",
    "food.risks": "Felismert rizikófaktorok",
    "food.new_ingredient": "Új összetevő",
    "food.add_images": "Új képek hozzáadása",
    "food.status": "Ételtörzs állapota",
    "food.deactivate": "Étel inaktiválása",
    "food.reactivate": "Étel újraaktiválása",
    "food.back": "Ételek / italok",
    "food.log_title": "Étel rögzítése",
    "food.log_consumption": "Fogyasztás rögzítése",
    "food.log_save": "Rögzítés",
    "food.other": "Másik étel",
    "foods.title": "Étel / ital",
    "foods.question": "Mit fogyasztottál?",
    "foods.search_placeholder": "🔎 Étel vagy márka keresése...",
    "foods.active": "Aktív ételek",
    "foods.inactive": "Inaktív ételek",
    "foods.new": "Új étel / ital felvétele",
    "foods.no_items": "Még nincs felvett étel vagy ital.",
    "symptom.new_title": "Tünet rögzítése",
    "symptom.new": "Új tünet rögzítése",
    "symptom.end_time": "Megszűnés ideje",
    "symptom.end_hint": "Hagyd üresen, ha a tünet még tart.",
    "symptom.type": "Tünet típusa",
    "symptom.choose": "Válassz...",
    "symptom.severity": "Erősség:",
    "symptom.body_parts": "Testrész(ek)",
    "symptom.photo": "Fénykép",
    "symptom.multi_images": "Több képet is csatolhatsz.",
    "symptom.save": "Tünet mentése",
    "event.edit_title": "Esemény szerkesztése",
    "event.food_images": "Törzsképek",
    "event.add_image": "Új kép hozzáadása",
    "event.back": "Vissza az eseményekhez",
    "export.title": "Események mentése",
    "export.start_date": "Kezdő dátum",
    "export.end_date": "Záró dátum",
    "export.status": "Állapot",
    "export.active_only": "Csak aktív",
    "export.all": "Aktív + inaktív",
    "export.inactive_only": "Csak inaktív",
})

TRANSLATIONS["en"].update({
    "events.title": "Events",
    "events.results": "{count} results",
    "events.search_placeholder": "🔎 Food, ingredient, symptom...",
    "events.all_types": "All types",
    "events.medication": "Medication",
    "events.food": "Food / drink",
    "events.symptom": "Symptom",
    "events.filter": "Search / Filter",
    "events.event_count": "{count} events",
    "events.ongoing": "ongoing",
    "events.edit": "Edit",
    "events.deactivate": "Deactivate",
    "events.activate": "Activate",
    "events.no_results": "No events match the filters.",
    "events.previous_50": "Previous 50",
    "events.next_50": "Next 50",
    "common.home": "Home",
    "common.management": "Management",
    "common.name": "Name",
    "common.brand": "Brand / manufacturer",
    "common.ingredients": "Ingredients",
    "common.notes": "Notes",
    "common.optional": "Optional",
    "common.optional_dots": "Optional...",
    "common.date_time": "Date and time",
    "common.amount": "Amount",
    "common.photo_take": "Take photo",
    "common.image_select": "Select image",
    "common.current_images": "Current images",
    "food.new_title": "New food / drink",
    "food.new_heading": "New food",
    "food.name_example": "e.g. Ham pizza",
    "food.no_ingredients": "There are no ingredients yet.",
    "food.add_ingredient": "Add new ingredient",
    "food.photo": "Photo of food / packaging",
    "food.multiple_photos": "You can take multiple photos before saving.",
    "food.photos_preview": "The images will appear here before saving.",
    "food.notes": "Food notes",
    "food.save": "Save food",
    "food.edit_title": "Edit food",
    "food.risks": "Detected risk factors",
    "food.new_ingredient": "New ingredient",
    "food.add_images": "Add new images",
    "food.status": "Food status",
    "food.deactivate": "Deactivate food",
    "food.reactivate": "Reactivate food",
    "food.back": "Foods / drinks",
    "food.log_title": "Log food",
    "food.log_consumption": "Log consumption",
    "food.log_save": "Log",
    "food.other": "Choose another food",
    "foods.title": "Food / drink",
    "foods.question": "What did you consume?",
    "foods.search_placeholder": "🔎 Search food or brand...",
    "foods.active": "Active foods",
    "foods.inactive": "Inactive foods",
    "foods.new": "Add new food / drink",
    "foods.no_items": "No food or drink has been added yet.",
    "symptom.new_title": "Log symptom",
    "symptom.new": "Log a new symptom",
    "symptom.end_time": "End time",
    "symptom.end_hint": "Leave empty if the symptom is still ongoing.",
    "symptom.type": "Symptom type",
    "symptom.choose": "Choose...",
    "symptom.severity": "Severity:",
    "symptom.body_parts": "Body part(s)",
    "symptom.photo": "Photo",
    "symptom.multi_images": "You can attach multiple images.",
    "symptom.save": "Save symptom",
    "event.edit_title": "Edit event",
    "event.food_images": "Food images",
    "event.add_image": "Add new image",
    "event.back": "Back to events",
    "export.title": "Export events",
    "export.start_date": "Start date",
    "export.end_date": "End date",
    "export.status": "Status",
    "export.active_only": "Active only",
    "export.all": "Active + inactive",
    "export.inactive_only": "Inactive only",
})


TRANSLATIONS["hu"].update({
    "common.filter": "Szűrés",
    "common.inactive_label": "Inaktív",
    "common.hour": "óra",
    "common.selected_image": "Kiválasztott kép",
    "common.delete_image": "Kép törlése",
    "common.delete_image_confirm": "Biztosan törlöd ezt a képet?",
    "common.image_alt": "Tünetkép",

    "event.medication": "Gyógyszer",
    "event.food": "Étel / ital",
    "event.symptom": "Tünet",
    "event.amount": "Mennyiség",
    "event.symptom_type": "Tünet típusa",
    "event.severity": "Erősség:",
    "event.end_time": "Megszűnés ideje",
    "event.body_parts": "Testrész(ek)",
    "event.notes_placeholder": "Opcionális megjegyzés...",
    "event.save": "Mentés",
    "event.food_master_images": "Törzsképek",
    "event.food_images_hint_1": "A képek az ételtörzshöz tartoznak.",
    "event.food_images_hint_2": "Módosításuk a Kezelés →",
    "event.food_images_hint_3": "Ételek / italok alatt lehetséges.",
    "event.add_image_hint": "Új fotót készíthetsz vagy több meglévő képet is kiválaszthatsz.",

    "food.detected_risks": "Felismert rizikófaktorok",
    "food.risk_hint_1": "Az összetevők alapján automatikusan",
    "food.risk_hint_2": "felismert rizikófaktorok.",
    "food.new_images_hint": "Több új fotót is készíthetsz egymás után mentés előtt.",
    "food.active_hint_1": "Az étel jelenleg aktív és megjelenik",
    "food.active_hint_2": "a gyors kiválasztási listában.",
    "food.inactive_hint_1": "Az étel inaktív, ezért nem jelenik meg",
    "food.inactive_hint_2": "a normál gyors listában.",
    "food.no_search_result": "Nincs találat erre:",

    "events.hours": "{value} óra",
})

TRANSLATIONS["en"].update({
    "common.filter": "Filter",
    "common.inactive_label": "Inactive",
    "common.hour": "hour",
    "common.selected_image": "Selected image",
    "common.delete_image": "Delete image",
    "common.delete_image_confirm": "Are you sure you want to delete this image?",
    "common.image_alt": "Symptom image",

    "event.medication": "Medication",
    "event.food": "Food / drink",
    "event.symptom": "Symptom",
    "event.amount": "Amount",
    "event.symptom_type": "Symptom type",
    "event.severity": "Severity:",
    "event.end_time": "End time",
    "event.body_parts": "Body part(s)",
    "event.notes_placeholder": "Optional note...",
    "event.save": "Save",
    "event.food_master_images": "Food images",
    "event.food_images_hint_1": "These images belong to the food record.",
    "event.food_images_hint_2": "You can modify them under Management →",
    "event.food_images_hint_3": "Foods / drinks.",
    "event.add_image_hint": "You can take a new photo or select multiple existing images.",

    "food.detected_risks": "Detected risk factors",
    "food.risk_hint_1": "Risk factors are detected automatically",
    "food.risk_hint_2": "from the selected ingredients.",
    "food.new_images_hint": "You can add multiple new photos before saving.",
    "food.active_hint_1": "This food is currently active and appears",
    "food.active_hint_2": "in the quick selection list.",
    "food.inactive_hint_1": "This food is inactive and therefore does not appear",
    "food.inactive_hint_2": "in the normal quick selection list.",
    "food.no_search_result": "No results for:",

    "events.hours": "{value} hours",
})


TRANSLATIONS["hu"].update({
    "common.no_results": "Nincs találat.",
    "common.edit": "Szerkesztés",
    "common.activate": "Aktiválás",
    "common.deactivate": "Inaktiválás",
    "common.description": "Leírás",
    "common.category": "Kategória",
    "common.choose": "-- válassz --",

    "admin.title": "Kezelés",
    "admin.subtitle": "Törzsadatok és beállítások",
    "admin.foods": "Ételek / italok",
    "admin.foods_desc": "Szerkesztés, összetevők, képek",
    "admin.ingredients": "Összetevők",
    "admin.ingredients_desc": "Rizikófaktorok hozzárendelése",
    "admin.risks": "Rizikófaktorok",
    "admin.risks_desc": "Allergének, FODMAP, intolerancia",
    "admin.symptom_types": "Tünettípusok",
    "admin.body_parts": "Testrészek",
    "admin.medications": "Gyógyszerek",
    "admin.reference_desc": "Felvitel, szerkesztés, aktiválás",
    "admin.export_desc": "CSV és XLSX",

    "ingredient.title": "Összetevők",
    "ingredient.edit_title": "Összetevő szerkesztése",
    "ingredient.single": "Összetevő",
    "ingredient.search": "🔎 Összetevő keresése...",
    "ingredient.with_risk": "Van rizikófaktor",
    "ingredient.without_risk": "Nincs rizikófaktor",
    "ingredient.risk_count": "rizikófaktor",
    "ingredient.no_risk": "Nincs rizikófaktor megadva",
    "ingredient.risks": "Rizikófaktorok",
    "ingredient.risk_hint_1": "Jelöld azokat, amelyek ehhez az",
    "ingredient.risk_hint_2": "összetevőhöz kapcsolódhatnak.",
    "ingredient.product_dependent": "Termékfüggő",
    "ingredient.save_links": "Kapcsolatok mentése",
    "ingredient.linked_count": "kapcsolódó összetevő",

    "risk.title": "Rizikófaktorok",
    "risk.single": "Rizikófaktor",
    "risk.new": "Új rizikófaktor",
    "risk.subtitle": "Allergének, FODMAP és egyéb faktorok",
    "risk.new_button": "Új rizikófaktor",
    "risk.total_short": "össz.",
    "risk.edit_aria": "{name} szerkesztése",
    "risk.allergen": "Allergén",
    "risk.intolerance": "Intolerancia",
    "risk.biogenic_amine": "Biogén amin",
    "risk.other": "Egyéb",

    "symptom_type.title": "Tünettípusok",
    "symptom_type.single": "Tünettípus",
    "symptom_type.new": "Új tünettípus",
    "symptom_type.subtitle": "A tünetfelvitel során választható típusok",

    "body_part.title": "Testrészek",
    "body_part.single": "Testrész",
    "body_part.new": "Új testrész",
    "body_part.subtitle": "A tünetekhez választható testrészek",

    "medication.title": "Gyógyszerek",
    "medication.single": "Gyógyszer",
    "medication.new": "Új gyógyszer",
    "medication.subtitle": "A gyógyszeres eseményekhez használható törzs",
    "medication.search": "🔎 Gyógyszer keresése...",
    "medication.default": "Alapértelmezett",
    "medication.make_default": "Legyen alapértelmezett",
    "medication.default_full": "Alapértelmezett gyógyszer",

    "error.name_required": "A név kötelező.",
    "error.duplicate_body_part": "Már létezik ilyen testrész.",
    "error.duplicate_symptom_type": "Már létezik ilyen tünettípus.",
    "error.risk_required": "A név és a kategória kötelező.",
    "error.duplicate_risk": "Már létezik ilyen nevű rizikófaktor.",
    "error.ingredient_name_required": "Az összetevő neve kötelező.",
    "error.duplicate_ingredient": "Már létezik ilyen nevű összetevő.",
    "error.duplicate_medication": "Már létezik ilyen gyógyszer.",
    "error.datetime_required": "Az időpont megadása kötelező.",
    "error.datetime_required_short": "Az időpont kötelező.",
    "error.invalid_datetime": "Érvénytelen dátum vagy időpont.",
    "error.invalid_food": "Érvénytelen étel / ital.",
    "error.invalid_symptom_type": "Érvénytelen tünettípus.",
    "error.severity": "Az erősség 0 és 10 közötti érték legyen.",
    "error.invalid_end_time": "Érvénytelen megszűnési időpont.",
    "error.end_before_start": "A megszűnés ideje nem lehet korábbi a tünet kezdeténél.",
    "error.food_name_required": "Az étel neve kötelező.",
    "error.food_duplicate": "Ez az étel már szerepel a listában. Válaszd ki a meglévő ételt.",
    "error.datetime_symptom_required": "Az időpont és a tünettípus kötelező.",
    "error.invalid_symptom_interval": "Érvénytelen dátum vagy időpont, illetve a megszűnés nem lehet korábbi a kezdetnél.",
})

TRANSLATIONS["en"].update({
    "common.no_results": "No results.",
    "common.edit": "Edit",
    "common.activate": "Activate",
    "common.deactivate": "Deactivate",
    "common.description": "Description",
    "common.category": "Category",
    "common.choose": "-- choose --",

    "admin.title": "Management",
    "admin.subtitle": "Reference data and settings",
    "admin.foods": "Foods / drinks",
    "admin.foods_desc": "Edit, ingredients and images",
    "admin.ingredients": "Ingredients",
    "admin.ingredients_desc": "Assign risk factors",
    "admin.risks": "Risk factors",
    "admin.risks_desc": "Allergens, FODMAP and intolerance",
    "admin.symptom_types": "Symptom types",
    "admin.body_parts": "Body parts",
    "admin.medications": "Medications",
    "admin.reference_desc": "Add, edit and activate",
    "admin.export_desc": "CSV and XLSX",

    "ingredient.title": "Ingredients",
    "ingredient.edit_title": "Edit ingredient",
    "ingredient.single": "Ingredient",
    "ingredient.search": "🔎 Search ingredients...",
    "ingredient.with_risk": "Has risk factor",
    "ingredient.without_risk": "No risk factor",
    "ingredient.risk_count": "risk factors",
    "ingredient.no_risk": "No risk factors assigned",
    "ingredient.risks": "Risk factors",
    "ingredient.risk_hint_1": "Select the risk factors that may",
    "ingredient.risk_hint_2": "apply to this ingredient.",
    "ingredient.product_dependent": "Product-dependent",
    "ingredient.save_links": "Save links",
    "ingredient.linked_count": "linked ingredients",

    "risk.title": "Risk factors",
    "risk.single": "Risk factor",
    "risk.new": "New risk factor",
    "risk.subtitle": "Allergens, FODMAP and other factors",
    "risk.new_button": "New risk factor",
    "risk.total_short": "total",
    "risk.edit_aria": "Edit {name}",
    "risk.allergen": "Allergen",
    "risk.intolerance": "Intolerance",
    "risk.biogenic_amine": "Biogenic amine",
    "risk.other": "Other",

    "symptom_type.title": "Symptom types",
    "symptom_type.single": "Symptom type",
    "symptom_type.new": "New symptom type",
    "symptom_type.subtitle": "Types available when logging symptoms",

    "body_part.title": "Body parts",
    "body_part.single": "Body part",
    "body_part.new": "New body part",
    "body_part.subtitle": "Body parts available for symptoms",

    "medication.title": "Medications",
    "medication.single": "Medication",
    "medication.new": "New medication",
    "medication.subtitle": "Reference data used for medication events",
    "medication.search": "🔎 Search medications...",
    "medication.default": "Default",
    "medication.make_default": "Make default",
    "medication.default_full": "Default medication",

    "error.name_required": "Name is required.",
    "error.duplicate_body_part": "This body part already exists.",
    "error.duplicate_symptom_type": "This symptom type already exists.",
    "error.risk_required": "Name and category are required.",
    "error.duplicate_risk": "A risk factor with this name already exists.",
    "error.ingredient_name_required": "Ingredient name is required.",
    "error.duplicate_ingredient": "An ingredient with this name already exists.",
    "error.duplicate_medication": "This medication already exists.",
    "error.datetime_required": "Date and time are required.",
    "error.datetime_required_short": "Date and time are required.",
    "error.invalid_datetime": "Invalid date or time.",
    "error.invalid_food": "Invalid food / drink.",
    "error.invalid_symptom_type": "Invalid symptom type.",
    "error.severity": "Severity must be between 0 and 10.",
    "error.invalid_end_time": "Invalid symptom end time.",
    "error.end_before_start": "The symptom end time cannot be earlier than its start time.",
    "error.food_name_required": "Food name is required.",
    "error.food_duplicate": "This food is already in the list. Select the existing food.",
    "error.datetime_symptom_required": "Date/time and symptom type are required.",
    "error.invalid_symptom_interval": "Invalid date or time, or the symptom end time is earlier than its start time.",
})


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
