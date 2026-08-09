from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)

from sqlalchemy import or_

from app import db
from app.models import (
    BodyPart,
    Event,
    Food,
    FoodEvent,
    FoodImage,
    FoodIngredient,
    Ingredient,
    Medication,
    MedicationEvent,
    SymptomEvent,
    SymptomImage,
    SymptomType,
)

main = Blueprint("main", __name__)

LOCAL_TIMEZONE = ZoneInfo("Europe/Budapest")

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def save_food_images(files):
    saved_filenames = []

    upload_dir = Path(
        "/opt/symptomtracker/uploads/foods"
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    for file in files:
        if not file or not file.filename:
            continue

        original_name = secure_filename(
            file.filename
        )

        extension = Path(
            original_name
        ).suffix.lower()

        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            continue

        filename = f"{uuid4().hex}{extension}"

        file.save(
            upload_dir / filename
        )

        saved_filenames.append(
            filename
        )

    return saved_filenames


def save_symptom_images(files):
    saved_filenames = []

    upload_dir = Path(
        "/opt/symptomtracker/uploads/symptoms"
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    for file in files:
        if not file or not file.filename:
            continue

        original_name = secure_filename(
            file.filename
        )

        extension = Path(
            original_name
        ).suffix.lower()

        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            continue

        filename = (
            f"{uuid4().hex}{extension}"
        )

        file.save(
            upload_dir / filename
        )

        saved_filenames.append(
            filename
        )

    return saved_filenames

def local_datetime_value(value):
    if value is None:
        return ""

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return (
        value
        .astimezone(LOCAL_TIMEZONE)
        .strftime("%Y-%m-%dT%H:%M")
    )


def parse_local_datetime(value):
    local_value = datetime.fromisoformat(value)

    local_value = local_value.replace(
        tzinfo=LOCAL_TIMEZONE
    )

    return local_value.astimezone(timezone.utc)


@main.route("/")
def index():
    recent_events = (
        Event.query
        .filter(Event.active.is_(True))
        .order_by(Event.occurred_at.desc())
        .limit(20)
        .all()
    )

    return render_template(
        "index.html",
        recent_events=recent_events,
    )


@main.route("/events")
def events():
    page = request.args.get(
        "page",
        1,
        type=int,
    )

    event_type = request.args.get(
        "type",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "active",
    ).strip()

    search = request.args.get(
        "q",
        "",
    ).strip()

    query = Event.query

    if status == "active":
        query = query.filter(
            Event.active.is_(True)
        )

    elif status == "inactive":
        query = query.filter(
            Event.active.is_(False)
        )

    if event_type in {
        "medication",
        "food",
        "symptom",
    }:
        query = query.filter(
            Event.event_type == event_type
        )

    if search:
        pattern = f"%{search}%"

        query = query.filter(
            or_(
                Event.notes.ilike(pattern),

                Event.medication_event.has(
                    MedicationEvent.medication.has(
                        Medication.name.ilike(pattern)
                    )
                ),

                Event.food_event.has(
                    FoodEvent.food.has(
                        or_(
                            Food.name.ilike(pattern),
                            Food.brand.ilike(pattern),

                            Food.ingredients.any(
                                FoodIngredient.ingredient.has(
                                    Ingredient.name.ilike(
                                        pattern
                                    )
                                )
                            ),
                        )
                    )
                ),

                Event.symptom_event.has(
                    or_(
                        SymptomEvent.symptom_type.has(
                            SymptomType.name.ilike(
                                pattern
                            )
                        ),

                        SymptomEvent.body_parts.any(
                            BodyPart.name.ilike(
                                pattern
                            )
                        ),
                    )
                ),
            )
        )

    pagination = (
        query
        .order_by(Event.occurred_at.desc())
        .paginate(
            page=page,
            per_page=50,
            error_out=False,
        )
    )

    return render_template(
        "events.html",
        events=pagination.items,
        pagination=pagination,
        selected_type=event_type,
        selected_status=status,
        search=search,
    )


@main.route(
    "/events/<int:event_id>/edit",
    methods=["GET", "POST"],
)
def edit_event(event_id):
    event = db.get_or_404(
        Event,
        event_id,
    )

    if request.method == "POST":
        occurred_at = request.form.get(
            "occurred_at",
            "",
        ).strip()

        notes = request.form.get(
            "notes",
            "",
        ).strip()

        if not occurred_at:
            return render_template(
                "edit_event.html",
                event=event,
                local_occurred_at=local_datetime_value(
                    event.occurred_at
                ),
                error="Az időpont megadása kötelező.",
            )

        try:
            event.occurred_at = parse_local_datetime(
                occurred_at
            )

        except ValueError:
            return render_template(
                "edit_event.html",
                event=event,
                local_occurred_at=occurred_at,
                error="Érvénytelen dátum vagy időpont.",
            )

        event.notes = notes or None

        if (
            event.event_type == "medication"
            and event.medication_event
        ):
            dose = request.form.get(
                "dose",
                "",
            ).strip()

            event.medication_event.dose = (
                dose or None
            )

        if (
            event.event_type == "food"
            and event.food_event
        ):
            food_id = request.form.get(
                "food_id",
                type=int,
            )

            amount = request.form.get(
                "amount",
                "",
            ).strip()

            food = db.session.get(
                Food,
                food_id,
            )

            if food is None or not food.active:
                foods = (
                    Food.query
                    .filter(Food.active.is_(True))
                    .order_by(Food.name, Food.brand)
                    .all()
                )

                return render_template(
                    "edit_event.html",
                    event=event,
                    local_occurred_at=occurred_at,
                    foods=foods,
                    symptom_types=[],
                    body_parts=[],
                    selected_body_part_ids=[],
                    error="Érvénytelen étel / ital.",
                )

            event.food_event.food = food
            event.food_event.amount = (
                amount or None
            )

        if (
            event.event_type == "symptom"
            and event.symptom_event
        ):
            symptom_type_id = request.form.get(
                "symptom_type_id",
                type=int,
            )

            severity = request.form.get(
                "severity",
                type=int,
            )

            selected_body_part_ids = request.form.getlist(
                "body_part_ids",
                type=int,
            )

            symptom_type = db.session.get(
                SymptomType,
                symptom_type_id,
            )

            if symptom_type is None:
                return render_template(
                    "edit_event.html",
                    event=event,
                    local_occurred_at=occurred_at,
                    symptom_types=(
                        SymptomType.query
                        .filter(
                            SymptomType.active.is_(True)
                        )
                        .order_by(SymptomType.name)
                        .all()
                    ),
                    body_parts=(
                        BodyPart.query
                        .filter(
                            BodyPart.active.is_(True)
                        )
                        .order_by(BodyPart.name)
                        .all()
                    ),
                    selected_body_part_ids=(
                        selected_body_part_ids
                    ),
                    error="Érvénytelen tünettípus.",
                )

            if (
                severity is None
                or severity < 0
                or severity > 10
            ):
                return render_template(
                    "edit_event.html",
                    event=event,
                    local_occurred_at=occurred_at,
                    symptom_types=(
                        SymptomType.query
                        .filter(
                            SymptomType.active.is_(True)
                        )
                        .order_by(SymptomType.name)
                        .all()
                    ),
                    body_parts=(
                        BodyPart.query
                        .filter(
                            BodyPart.active.is_(True)
                        )
                        .order_by(BodyPart.name)
                        .all()
                    ),
                    selected_body_part_ids=(
                        selected_body_part_ids
                    ),
                    error=(
                        "Az erősség 0 és 10 közötti "
                        "érték legyen."
                    ),
                )

            event.symptom_event.symptom_type = (
                symptom_type
            )

            event.symptom_event.severity = severity

            event.symptom_event.body_parts = (
                BodyPart.query
                .filter(
                    BodyPart.id.in_(
                        selected_body_part_ids
                    )
                )
                .all()
            )

            uploaded_files = request.files.getlist(
                "images"
            )

            saved_filenames = save_symptom_images(
                uploaded_files
            )

            for filename in saved_filenames:
                event.symptom_event.images.append(
                    SymptomImage(
                        filename=filename
                    )
                )

        db.session.commit()

        return redirect(
            "/symptomtracker/events"
        )

    foods = []
    symptom_types = []
    body_parts = []
    selected_body_part_ids = []

    if (
        event.event_type == "food"
        and event.food_event
    ):
        foods = (
            Food.query
            .filter(Food.active.is_(True))
            .order_by(Food.name, Food.brand)
            .all()
        )

    if (
        event.event_type == "symptom"
        and event.symptom_event
    ):
        symptom_types = (
            SymptomType.query
            .filter(SymptomType.active.is_(True))
            .order_by(SymptomType.name)
            .all()
        )

        body_parts = (
            BodyPart.query
            .filter(BodyPart.active.is_(True))
            .order_by(BodyPart.name)
            .all()
        )

        selected_body_part_ids = [
            body_part.id
            for body_part
            in event.symptom_event.body_parts
        ]

    return render_template(
        "edit_event.html",
        event=event,
        local_occurred_at=local_datetime_value(
            event.occurred_at
        ),
        foods=foods,
        symptom_types=symptom_types,
        body_parts=body_parts,
        selected_body_part_ids=selected_body_part_ids,
        error=None,
    )


@main.route(
    "/events/<int:event_id>/toggle",
    methods=["POST"],
)
def toggle_event(event_id):
    event = db.get_or_404(
        Event,
        event_id,
    )

    event.active = not event.active

    db.session.commit()

    return redirect(
        request.referrer
        or "/symptomtracker/events"
    )


@main.route("/foods")
def foods():
    search = request.args.get(
        "q",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "active",
    ).strip()

    query = Food.query

    if status == "active":
        query = query.filter(
            Food.active.is_(True)
        )

    elif status == "inactive":
        query = query.filter(
            Food.active.is_(False)
        )

    if search:
        pattern = f"%{search}%"

        query = query.filter(
            or_(
                Food.name.ilike(pattern),
                Food.brand.ilike(pattern),
            )
        )

    food_list = (
        query
        .order_by(
            Food.name,
            Food.brand,
        )
        .limit(100)
        .all()
    )

    return render_template(
        "foods.html",
        foods=food_list,
        search=search,
        selected_status=status,
    )


@main.route(
    "/foods/new",
    methods=["GET", "POST"],
)
def new_food():
    ingredients = (
        Ingredient.query
        .order_by(Ingredient.name)
        .all()
    )

    selected_ingredient_ids = []

    if request.method == "POST":
        name = request.form.get(
            "name",
            "",
        ).strip()

        brand = request.form.get(
            "brand",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        selected_ingredient_ids = (
            request.form.getlist(
                "ingredient_ids",
                type=int,
            )
        )

        new_ingredient_names = [
            value.strip()
            for value
            in request.form.getlist(
                "new_ingredients"
            )
            if value.strip()
        ]

        if not name:
            return render_template(
                "food_form.html",
                ingredients=ingredients,
                selected_ingredient_ids=(
                    selected_ingredient_ids
                ),
                form=request.form,
                error="Az étel neve kötelező.",
            )

        duplicate_query = Food.query.filter(
            db.func.lower(Food.name)
            == name.lower()
        )

        if brand:
            duplicate_query = (
                duplicate_query.filter(
                    db.func.lower(Food.brand)
                    == brand.lower()
                )
            )
        else:
            duplicate_query = (
                duplicate_query.filter(
                    or_(
                        Food.brand.is_(None),
                        Food.brand == "",
                    )
                )
            )

        duplicate = duplicate_query.first()

        if duplicate is not None:
            return render_template(
                "food_form.html",
                ingredients=ingredients,
                selected_ingredient_ids=(
                    selected_ingredient_ids
                ),
                form=request.form,
                error=(
                    "Ez az étel már szerepel a listában. "
                    "Válaszd ki a meglévő ételt."
                ),
            )

        food = Food(
            name=name,
            brand=brand or None,
            description=description or None,
        )

        position = 0
        used_ingredient_ids = set()

        if selected_ingredient_ids:
            selected_ingredients = (
                Ingredient.query
                .filter(
                    Ingredient.id.in_(
                        selected_ingredient_ids
                    )
                )
                .all()
            )

            for ingredient in selected_ingredients:
                food.ingredients.append(
                    FoodIngredient(
                        ingredient=ingredient,
                        position=position,
                    )
                )

                used_ingredient_ids.add(
                    ingredient.id
                )

                position += 1

        seen_new_names = set()

        for ingredient_name in new_ingredient_names:
            normalized_name = (
                ingredient_name
                .strip()
                .lower()
            )

            if normalized_name in seen_new_names:
                continue

            seen_new_names.add(
                normalized_name
            )

            ingredient = (
                Ingredient.query
                .filter(
                    db.func.lower(
                        Ingredient.name
                    ) == normalized_name
                )
                .first()
            )

            if ingredient is None:
                ingredient = Ingredient(
                    name=ingredient_name.strip()
                )

                db.session.add(ingredient)
                db.session.flush()

            if ingredient.id in used_ingredient_ids:
                continue

            food.ingredients.append(
                FoodIngredient(
                    ingredient=ingredient,
                    position=position,
                )
            )

            used_ingredient_ids.add(
                ingredient.id
            )

            position += 1

        uploaded_files = request.files.getlist(
            "images"
        )

        saved_filenames = save_food_images(
            uploaded_files
        )

        for filename in saved_filenames:
            food.images.append(
                FoodImage(
                    filename=filename,
                    image_type="general",
                )
            )

        db.session.add(food)
        db.session.commit()

        return redirect(
            f"/symptomtracker/foods/"
            f"{food.id}/log"
        )

    return render_template(
        "food_form.html",
        ingredients=ingredients,
        selected_ingredient_ids=[],
        form={},
        error=None,
    )


@main.route(
    "/foods/<int:food_id>/edit",
    methods=["GET", "POST"],
)
def edit_food(food_id):
    food = db.get_or_404(
        Food,
        food_id,
    )

    ingredients = (
        Ingredient.query
        .order_by(Ingredient.name)
        .all()
    )

    if request.method == "POST":
        name = request.form.get(
            "name",
            "",
        ).strip()

        brand = request.form.get(
            "brand",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        selected_ingredient_ids = (
            request.form.getlist(
                "ingredient_ids",
                type=int,
            )
        )

        new_ingredient_names = [
            value.strip()
            for value
            in request.form.getlist(
                "new_ingredients"
            )
            if value.strip()
        ]

        if not name:
            return render_template(
                "edit_food.html",
                food=food,
                ingredients=ingredients,
                selected_ingredient_ids=(
                    selected_ingredient_ids
                ),
                error="Az étel neve kötelező.",
            )

        food.name = name
        food.brand = brand or None
        food.description = (
            description or None
        )

        food.ingredients.clear()

        position = 0
        used_ingredient_ids = set()

        if selected_ingredient_ids:
            selected_ingredients = (
                Ingredient.query
                .filter(
                    Ingredient.id.in_(
                        selected_ingredient_ids
                    )
                )
                .all()
            )

            for ingredient in selected_ingredients:
                food.ingredients.append(
                    FoodIngredient(
                        ingredient=ingredient,
                        position=position,
                    )
                )

                used_ingredient_ids.add(
                    ingredient.id
                )

                position += 1

        seen_new_names = set()

        for ingredient_name in new_ingredient_names:
            normalized_name = (
                ingredient_name
                .strip()
                .lower()
            )

            if normalized_name in seen_new_names:
                continue

            seen_new_names.add(
                normalized_name
            )

            ingredient = (
                Ingredient.query
                .filter(
                    db.func.lower(
                        Ingredient.name
                    ) == normalized_name
                )
                .first()
            )

            if ingredient is None:
                ingredient = Ingredient(
                    name=ingredient_name.strip()
                )

                db.session.add(ingredient)
                db.session.flush()

            if ingredient.id in used_ingredient_ids:
                continue

            food.ingredients.append(
                FoodIngredient(
                    ingredient=ingredient,
                    position=position,
                )
            )

            used_ingredient_ids.add(
                ingredient.id
            )

            position += 1

        uploaded_files = request.files.getlist(
            "images"
        )

        saved_filenames = save_food_images(
            uploaded_files
        )

        for filename in saved_filenames:
            food.images.append(
                FoodImage(
                    filename=filename,
                    image_type="general",
                )
            )

        db.session.commit()

        return redirect(
            f"/symptomtracker/foods/"
            f"{food.id}/edit"
        )

    selected_ingredient_ids = [
        item.ingredient_id
        for item in food.ingredients
    ]

    return render_template(
        "edit_food.html",
        food=food,
        ingredients=ingredients,
        selected_ingredient_ids=(
            selected_ingredient_ids
        ),
        error=None,
    )


@main.route(
    "/foods/<int:food_id>/toggle",
    methods=["POST"],
)
def toggle_food(food_id):
    food = db.get_or_404(
        Food,
        food_id,
    )

    food.active = not food.active

    db.session.commit()

    return redirect(
        f"/symptomtracker/foods/"
        f"{food.id}/edit"
    )


@main.route(
    "/foods/<int:food_id>/log",
    methods=["GET", "POST"],
)
def log_food(food_id):
    food = db.get_or_404(
        Food,
        food_id,
    )

    if not food.active:
        return redirect(
            "/symptomtracker/foods"
        )

    if request.method == "POST":
        occurred_at = request.form.get(
            "occurred_at",
            "",
        ).strip()

        amount = request.form.get(
            "amount",
            "",
        ).strip()

        notes = request.form.get(
            "notes",
            "",
        ).strip()

        if not occurred_at:
            return render_template(
                "food_log.html",
                food=food,
                local_now="",
                form=request.form,
                error="Az időpont kötelező.",
            )

        try:
            occurred_at_utc = (
                parse_local_datetime(
                    occurred_at
                )
            )

        except ValueError:
            return render_template(
                "food_log.html",
                food=food,
                local_now=occurred_at,
                form=request.form,
                error="Érvénytelen dátum vagy időpont.",
            )

        event = Event(
            event_type="food",
            occurred_at=occurred_at_utc,
            notes=notes or None,
        )

        event.food_event = FoodEvent(
            food=food,
            amount=amount or None,
        )

        db.session.add(event)
        db.session.commit()

        return redirect(
            "/symptomtracker/"
        )

    local_now = (
        datetime.now(timezone.utc)
        .astimezone(LOCAL_TIMEZONE)
        .strftime("%Y-%m-%dT%H:%M")
    )

    return render_template(
        "food_log.html",
        food=food,
        local_now=local_now,
        form={},
        error=None,
    )


@main.route(
    "/symptoms/new",
    methods=["GET", "POST"],
)
def add_symptom():
    symptom_types = (
        SymptomType.query
        .filter(SymptomType.active.is_(True))
        .order_by(SymptomType.name)
        .all()
    )

    body_parts = (
        BodyPart.query
        .filter(BodyPart.active.is_(True))
        .order_by(BodyPart.name)
        .all()
    )

    if request.method == "POST":
        occurred_at = request.form.get(
            "occurred_at",
            "",
        ).strip()

        symptom_type_id = request.form.get(
            "symptom_type_id",
            type=int,
        )

        severity = request.form.get(
            "severity",
            type=int,
        )

        selected_body_part_ids = request.form.getlist(
            "body_part_ids",
            type=int,
        )

        notes = request.form.get(
            "notes",
            "",
        ).strip()

        if not occurred_at or not symptom_type_id:
            return render_template(
                "symptom_form.html",
                symptom_types=symptom_types,
                body_parts=body_parts,
                form=request.form,
                selected_body_part_ids=selected_body_part_ids,
                error="Az időpont és a tünettípus kötelező.",
            )

        if severity is None or severity < 0 or severity > 10:
            return render_template(
                "symptom_form.html",
                symptom_types=symptom_types,
                body_parts=body_parts,
                form=request.form,
                selected_body_part_ids=selected_body_part_ids,
                error="Az erősség 0 és 10 közötti érték legyen.",
            )

        symptom_type = db.session.get(
            SymptomType,
            symptom_type_id,
        )

        if symptom_type is None:
            return render_template(
                "symptom_form.html",
                symptom_types=symptom_types,
                body_parts=body_parts,
                form=request.form,
                selected_body_part_ids=selected_body_part_ids,
                error="Érvénytelen tünettípus.",
            )

        try:
            occurred_at_utc = parse_local_datetime(
                occurred_at
            )
        except ValueError:
            return render_template(
                "symptom_form.html",
                symptom_types=symptom_types,
                body_parts=body_parts,
                form=request.form,
                selected_body_part_ids=selected_body_part_ids,
                error="Érvénytelen dátum vagy időpont.",
            )

        event = Event(
            event_type="symptom",
            occurred_at=occurred_at_utc,
            notes=notes or None,
        )

        symptom_event = SymptomEvent(
            symptom_type=symptom_type,
            severity=severity,
        )

        if selected_body_part_ids:
            symptom_event.body_parts = (
                BodyPart.query
                .filter(
                    BodyPart.id.in_(
                        selected_body_part_ids
                    )
                )
                .all()
            )

        event.symptom_event = symptom_event

        uploaded_files = request.files.getlist(
            "images"
        )

        saved_filenames = save_symptom_images(
            uploaded_files
        )

        for filename in saved_filenames:
            symptom_event.images.append(
                SymptomImage(
                    filename=filename
                )
            )

        db.session.add(event)
        db.session.commit()

        return redirect(
            "/symptomtracker/"
        )

    local_now = (
        datetime.now(timezone.utc)
        .astimezone(LOCAL_TIMEZONE)
        .strftime("%Y-%m-%dT%H:%M")
    )

    return render_template(
        "symptom_form.html",
        symptom_types=symptom_types,
        body_parts=body_parts,
        form={},
        selected_body_part_ids=[],
        local_now=local_now,
        error=None,
    )


@main.route(
    "/symptoms/images/<int:image_id>/delete",
    methods=["POST"],
)
def delete_symptom_image(image_id):
    image = db.get_or_404(
        SymptomImage,
        image_id,
    )

    event_id = image.symptom_event.event_id

    image_path = (
        Path("/opt/symptomtracker/uploads/symptoms")
        / image.filename
    )

    db.session.delete(image)
    db.session.commit()

    image_path.unlink(
        missing_ok=True
    )

    return redirect(
        f"/symptomtracker/events/"
        f"{event_id}/edit"
    )


@main.route(
    "/uploads/symptoms/<path:filename>"
)
def symptom_image(filename):
    return send_from_directory(
        "/opt/symptomtracker/uploads/symptoms",
        filename,
    )


@main.route(
    "/foods/images/<int:image_id>/delete",
    methods=["POST"],
)
def delete_food_image(image_id):
    image = db.get_or_404(
        FoodImage,
        image_id,
    )

    food_id = image.food_id

    image_path = (
        Path("/opt/symptomtracker/uploads/foods")
        / image.filename
    )

    db.session.delete(image)
    db.session.commit()

    image_path.unlink(
        missing_ok=True
    )

    return redirect(
        f"/symptomtracker/foods/"
        f"{food_id}/edit"
    )


@main.route(
    "/uploads/foods/<path:filename>"
)
def food_image(filename):
    return send_from_directory(
        "/opt/symptomtracker/uploads/foods",
        filename,
    )


@main.route(
    "/api/events/cetirizine",
    methods=["POST"],
)
def add_cetirizine():
    medication = Medication.query.filter_by(
        name="Cetirizin"
    ).first()

    if medication is None:
        return jsonify(
            {
                "ok": False,
                "message":
                    "A Cetirizin nincs a törzsadatok között.",
            }
        ), 500

    event = Event(
        event_type="medication",
        occurred_at=datetime.now(timezone.utc),
    )

    medication_event = MedicationEvent(
        medication=medication,
    )

    event.medication_event = medication_event

    db.session.add(event)
    db.session.commit()

    return jsonify(
        {
            "ok": True,
            "event_id": event.id,
            "message": "Cetirizin rögzítve.",
        }
    )
