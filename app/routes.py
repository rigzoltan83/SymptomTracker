import csv
from io import BytesIO, StringIO

from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from openpyxl import Workbook

from flask import (
    abort,
    Response,
    send_file,
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
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
    FoodRiskComponent,
    Ingredient,
    IngredientRiskComponent,
    Medication,
    MedicationEvent,
    RiskComponent,
    SymptomEvent,
    SymptomImage,
    SymptomType,
)

main = Blueprint("main", __name__)

LOCAL_TIMEZONE = ZoneInfo("Europe/Budapest")

from app.i18n import (
    SUPPORTED_LANGUAGES,
    set_current_language,
)


from app.reference_i18n import (
    apply_reference_name_join,
    create_reference_translations,
    find_reference_by_name,
    get_reference_description,
    get_reference_name,
    order_reference_query,
    reference_description_matches,
    reference_name_matches,
    update_current_reference_translation,
)


@main.get("/language/<language_code>")
def change_language(language_code):
    if language_code not in SUPPORTED_LANGUAGES:
        abort(404)

    set_current_language(
        language_code
    )

    next_url = request.args.get(
        "next",
        "",
    ).strip()

    if (
        not next_url
        or not next_url.startswith("/")
        or next_url.startswith("//")
    ):
        next_url = url_for(
            "main.index"
        )

    return redirect(
        next_url
    )


def event_export_row(event):
    medication = ""
    dose = ""

    food_name = ""
    food_brand = ""
    food_amount = ""
    ingredients = ""

    symptom_type = ""
    severity = ""
    body_parts = ""

    if (
        event.event_type == "medication"
        and event.medication_event
    ):
        medication = (
            event.medication_event.medication.name
        )

        dose = (
            event.medication_event.dose
            or ""
        )

    if (
        event.event_type == "food"
        and event.food_event
    ):
        food = event.food_event.food

        food_name = food.name
        food_brand = food.brand or ""
        food_amount = (
            event.food_event.amount
            or ""
        )

        ingredients = ", ".join(
            item.ingredient.name
            for item in food.ingredients
        )

    if (
        event.event_type == "symptom"
        and event.symptom_event
    ):
        symptom_type = (
            event.symptom_event
            .symptom_type
            .name
        )

        if event.symptom_event.severity is not None:
            severity = (
                event.symptom_event.severity
            )

        body_parts = ", ".join(
            body_part.name
            for body_part
            in event.symptom_event.body_parts
        )

    return {
        "id": event.id,

        "date_time": local_datetime_value(
            event.occurred_at
        ).replace("T", " "),

        "event_type": event.event_type,

        "active": (
            "Igen"
            if event.active
            else "Nem"
        ),

        "medication": medication,
        "dose": dose,

        "food": food_name,
        "brand": food_brand,
        "amount": food_amount,
        "ingredients": ingredients,

        "symptom": symptom_type,
        "severity": severity,
        "body_parts": body_parts,

        "notes": event.notes or "",
    }

def build_export_query():
    query = Event.query

    status = request.args.get(
        "status",
        "active",
    ).strip()

    date_from = request.args.get(
        "date_from",
        "",
    ).strip()

    date_to = request.args.get(
        "date_to",
        "",
    ).strip()

    if status == "active":
        query = query.filter(
            Event.active.is_(True)
        )

    elif status == "inactive":
        query = query.filter(
            Event.active.is_(False)
        )

    if date_from:
        try:
            start_local = datetime.strptime(
                date_from,
                "%Y-%m-%d",
            ).replace(
                tzinfo=LOCAL_TIMEZONE
            )

            query = query.filter(
                Event.occurred_at
                >= start_local.astimezone(
                    timezone.utc
                )
            )

        except ValueError:
            pass

    if date_to:
        try:
            end_local = datetime.strptime(
                date_to,
                "%Y-%m-%d",
            ).replace(
                hour=23,
                minute=59,
                second=59,
                tzinfo=LOCAL_TIMEZONE,
            )

            query = query.filter(
                Event.occurred_at
                <= end_local.astimezone(
                    timezone.utc
                )
            )

        except ValueError:
            pass

    return query.order_by(
        Event.occurred_at
    )

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


@main.route("/analysis")
def analysis_page():
    from app.analysis import build_analysis

    allowed_windows = (
        3,
        6,
        12,
        24,
        48,
    )

    allowed_days = (
        30,
        90,
        180,
        365,
        0,
    )

    window_hours = request.args.get(
        "window",
        12,
        type=int,
    )

    days = request.args.get(
        "days",
        90,
        type=int,
    )

    symptom_type_id = request.args.get(
        "symptom_type_id",
        type=int,
    )

    if window_hours not in allowed_windows:
        window_hours = 12

    if days not in allowed_days:
        days = 90

    if symptom_type_id is not None:
        symptom_type = db.session.get(
            SymptomType,
            symptom_type_id,
        )

        if symptom_type is None:
            symptom_type_id = None

    analysis = build_analysis(
        window_hours=window_hours,
        days=days,
        symptom_type_id=symptom_type_id,
    )

    symptom_types = (
        order_reference_query(
            SymptomType.query
            .filter(
                SymptomType.active.is_(True)
            ),
            SymptomType,
        )
        .all()
    )

    return render_template(
        "analysis.html",
        analysis=analysis,
        symptom_types=symptom_types,
        selected_window=window_hours,
        selected_days=days,
        selected_symptom_type_id=(
            symptom_type_id
        ),
    )


@main.route(
    "/analysis/risk/<int:risk_component_id>"
)
def analysis_risk_detail(
    risk_component_id
):
    from app.analysis import (
        build_risk_detail
    )

    risk_component = db.get_or_404(
        RiskComponent,
        risk_component_id,
    )

    allowed_windows = (
        3,
        6,
        12,
        24,
        48,
    )

    allowed_days = (
        30,
        90,
        180,
        365,
        0,
    )

    window_hours = request.args.get(
        "window",
        12,
        type=int,
    )

    days = request.args.get(
        "days",
        90,
        type=int,
    )

    symptom_type_id = request.args.get(
        "symptom_type_id",
        type=int,
    )

    if window_hours not in allowed_windows:
        window_hours = 12

    if days not in allowed_days:
        days = 90

    if symptom_type_id is not None:
        symptom_type = db.session.get(
            SymptomType,
            symptom_type_id,
        )

        if symptom_type is None:
            symptom_type_id = None

    detail = build_risk_detail(
        risk_component_id=(
            risk_component.id
        ),
        window_hours=window_hours,
        days=days,
        symptom_type_id=(
            symptom_type_id
        ),
    )

    symptom_types = (
        order_reference_query(
            SymptomType.query
            .filter(
                SymptomType.active.is_(True)
            ),
            SymptomType,
        )
        .all()
    )

    return render_template(
        "analysis_risk_detail.html",
        detail=detail,
        symptom_types=symptom_types,
        selected_window=window_hours,
        selected_days=days,
        selected_symptom_type_id=(
            symptom_type_id
        ),
    )


@main.route(
    "/analysis/combination/"
    "<int:first_risk_id>/"
    "<int:second_risk_id>"
)
def analysis_combination_detail(
    first_risk_id,
    second_risk_id,
):
    from app.analysis import (
        build_combination_detail
    )

    allowed_windows = (
        3,
        6,
        12,
        24,
        48,
    )

    allowed_days = (
        30,
        90,
        180,
        365,
        0,
    )

    window_hours = request.args.get(
        "window",
        12,
        type=int,
    )

    days = request.args.get(
        "days",
        90,
        type=int,
    )

    symptom_type_id = request.args.get(
        "symptom_type_id",
        type=int,
    )

    if window_hours not in allowed_windows:
        window_hours = 12

    if days not in allowed_days:
        days = 90

    if symptom_type_id is not None:
        symptom_type = db.session.get(
            SymptomType,
            symptom_type_id,
        )

        if symptom_type is None:
            symptom_type_id = None

    detail = build_combination_detail(
        first_risk_id=first_risk_id,
        second_risk_id=second_risk_id,
        window_hours=window_hours,
        days=days,
        symptom_type_id=(
            symptom_type_id
        ),
    )

    if detail is None:
        abort(404)

    symptom_types = (
        order_reference_query(
            SymptomType.query
            .filter(
                SymptomType.active.is_(True)
            ),
            SymptomType,
        )
        .all()
    )

    return render_template(
        "analysis_combination_detail.html",
        detail=detail,
        symptom_types=symptom_types,
        selected_window=window_hours,
        selected_days=days,
        selected_symptom_type_id=(
            symptom_type_id
        ),
    )


@main.route("/export")
def export_page():
    return_to = request.args.get(
        "return_to",
        "dashboard",
    ).strip()

    if return_to not in (
        "dashboard",
        "admin",
    ):
        return_to = "dashboard"

    return render_template(
        "export.html",
        return_to=return_to,
    )


@main.route("/export/csv")
def export_csv():
    events = (
        build_export_query()
        .all()
    )

    output = StringIO()

    writer = csv.writer(
        output,
        delimiter=";",
        lineterminator="\n",
    )

    writer.writerow(
        [
            "ID",
            "Dátum és idő",
            "Eseménytípus",
            "Aktív",
            "Gyógyszer",
            "Adag",
            "Étel / ital",
            "Márka",
            "Mennyiség",
            "Összetevők",
            "Tünet",
            "Erősség",
            "Testrészek",
            "Megjegyzés",
        ]
    )

    for event in events:
        row = event_export_row(
            event
        )

        writer.writerow(
            [
                row["id"],
                row["date_time"],
                row["event_type"],
                row["active"],
                row["medication"],
                row["dose"],
                row["food"],
                row["brand"],
                row["amount"],
                row["ingredients"],
                row["symptom"],
                row["severity"],
                row["body_parts"],
                row["notes"],
            ]
        )

    csv_data = (
        "\ufeff"
        + output.getvalue()
    )

    return Response(
        csv_data,
        mimetype=(
            "text/csv; charset=utf-8"
        ),
        headers={
            "Content-Disposition":
                "attachment; "
                "filename=symptomtracker.csv"
        },
    )


@main.route("/export/xlsx")
def export_xlsx():
    events = (
        build_export_query()
        .all()
    )

    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Események"

    headers = [
        "ID",
        "Dátum és idő",
        "Eseménytípus",
        "Aktív",
        "Gyógyszer",
        "Adag",
        "Étel / ital",
        "Márka",
        "Mennyiség",
        "Összetevők",
        "Tünet",
        "Erősség",
        "Testrészek",
        "Megjegyzés",
    ]

    sheet.append(headers)

    for event in events:
        row = event_export_row(
            event
        )

        sheet.append(
            [
                row["id"],
                row["date_time"],
                row["event_type"],
                row["active"],
                row["medication"],
                row["dose"],
                row["food"],
                row["brand"],
                row["amount"],
                row["ingredients"],
                row["symptom"],
                row["severity"],
                row["body_parts"],
                row["notes"],
            ]
        )

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = (
        sheet.dimensions
    )

    widths = {
        "A": 8,
        "B": 20,
        "C": 16,
        "D": 10,
        "E": 18,
        "F": 12,
        "G": 28,
        "H": 20,
        "I": 16,
        "J": 45,
        "K": 22,
        "L": 12,
        "M": 35,
        "N": 45,
    }

    for column, width in widths.items():
        sheet.column_dimensions[
            column
        ].width = width

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=(
            "symptomtracker.xlsx"
        ),
        mimetype=(
            "application/"
            "vnd.openxmlformats-"
            "officedocument."
            "spreadsheetml.sheet"
        ),
    )


@main.route("/admin")
def admin():
    return render_template(
        "admin.html"
    )


@main.route("/admin/symptom-types")
def admin_symptom_types():
    search = request.args.get(
        "q",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "active",
    ).strip()

    query, display_name = (
        apply_reference_name_join(
            SymptomType.query,
            SymptomType,
        )
    )

    if status == "active":
        query = query.filter(
            SymptomType.active.is_(True)
        )

    elif status == "inactive":
        query = query.filter(
            SymptomType.active.is_(False)
        )

    if search:
        pattern = f"%{search}%"

        query = query.filter(
            display_name.ilike(pattern)
        )

    symptom_types = (
        query
        .order_by(display_name)
        .all()
    )

    return render_template(
        "admin_symptom_types.html",
        symptom_types=symptom_types,
        search=search,
        selected_status=status,
    )


@main.route("/admin/body-parts")
def admin_body_parts():
    search = request.args.get(
        "q",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "active",
    ).strip()

    query, display_name = (
        apply_reference_name_join(
            BodyPart.query,
            BodyPart,
        )
    )

    if status == "active":
        query = query.filter(
            BodyPart.active.is_(True)
        )

    elif status == "inactive":
        query = query.filter(
            BodyPart.active.is_(False)
        )

    if search:
        pattern = f"%{search}%"

        query = query.filter(
            display_name.ilike(pattern)
        )

    body_parts = (
        query
        .order_by(display_name)
        .all()
    )

    return render_template(
        "admin_body_parts.html",
        body_parts=body_parts,
        search=search,
        selected_status=status,
    )


@main.route(
    "/admin/body-parts/new",
    methods=["GET", "POST"],
)
def admin_new_body_part():
    if request.method == "POST":
        name = " ".join(
            request.form.get(
                "name",
                "",
            ).split()
        )

        if not name:
            return render_template(
                "admin_body_part_form.html",
                body_part=None,
                form=request.form,
                error="A név kötelező.",
            )

        duplicate = find_reference_by_name(
            BodyPart,
            name,
        )

        if duplicate is not None:
            return render_template(
                "admin_body_part_form.html",
                body_part=None,
                form=request.form,
                error=(
                    "Már létezik ilyen testrész."
                ),
            )

        body_part = BodyPart(
            name=name,
            active=True,
        )

        db.session.add(body_part)
        db.session.flush()

        create_reference_translations(
            body_part,
            name=body_part.name,
        )

        db.session.commit()

        return redirect(
            "/symptomtracker/admin/body-parts"
        )

    return render_template(
        "admin_body_part_form.html",
        body_part=None,
        form={},
        error=None,
    )


@main.route(
    "/admin/body-parts/<int:body_part_id>/edit",
    methods=["GET", "POST"],
)
def admin_edit_body_part(
    body_part_id
):
    body_part = db.get_or_404(
        BodyPart,
        body_part_id,
    )

    if request.method == "POST":
        name = " ".join(
            request.form.get(
                "name",
                "",
            ).split()
        )

        if not name:
            return render_template(
                "admin_body_part_form.html",
                body_part=body_part,
                body_part_display_name=(
                    get_reference_name(body_part)
                ),
                form=request.form,
                error="A név kötelező.",
            )

        duplicate = find_reference_by_name(
            BodyPart,
            name,
            exclude_id=body_part.id,
        )

        if duplicate is not None:
            return render_template(
                "admin_body_part_form.html",
                body_part=body_part,
                body_part_display_name=(
                    get_reference_name(body_part)
                ),
                form=request.form,
                error=(
                    "Már létezik ilyen testrész."
                ),
            )

        update_current_reference_translation(
            body_part,
            name=name,
        )

        db.session.commit()

        return redirect(
            f"/symptomtracker/admin/"
            f"body-parts/"
            f"{body_part.id}/edit"
        )

    return render_template(
        "admin_body_part_form.html",
        body_part=body_part,
        body_part_display_name=(
            get_reference_name(body_part)
        ),
        form={},
        error=None,
    )


@main.route(
    "/admin/body-parts/<int:body_part_id>/toggle",
    methods=["POST"],
)
def admin_toggle_body_part(
    body_part_id
):
    body_part = db.get_or_404(
        BodyPart,
        body_part_id,
    )

    body_part.active = (
        not body_part.active
    )

    db.session.commit()

    return redirect(
        f"/symptomtracker/admin/"
        f"body-parts/"
        f"{body_part.id}/edit"
    )


@main.route(
    "/admin/symptom-types/new",
    methods=["GET", "POST"],
)
def admin_new_symptom_type():
    if request.method == "POST":
        name = " ".join(
            request.form.get(
                "name",
                "",
            ).split()
        )

        if not name:
            return render_template(
                "admin_symptom_type_form.html",
                symptom_type=None,
                form=request.form,
                error="A név kötelező.",
            )

        duplicate = find_reference_by_name(
            SymptomType,
            name,
        )

        if duplicate is not None:
            return render_template(
                "admin_symptom_type_form.html",
                symptom_type=None,
                form=request.form,
                error=(
                    "Már létezik ilyen tünettípus."
                ),
            )

        symptom_type = SymptomType(
            name=name,
            active=True,
        )

        db.session.add(symptom_type)
        db.session.flush()

        create_reference_translations(
            symptom_type,
            name=symptom_type.name,
        )

        db.session.commit()

        return redirect(
            "/symptomtracker/admin/symptom-types"
        )

    return render_template(
        "admin_symptom_type_form.html",
        symptom_type=None,
        form={},
        error=None,
    )


@main.route(
    "/admin/symptom-types/<int:symptom_type_id>/edit",
    methods=["GET", "POST"],
)
def admin_edit_symptom_type(
    symptom_type_id
):
    symptom_type = db.get_or_404(
        SymptomType,
        symptom_type_id,
    )

    if request.method == "POST":
        name = " ".join(
            request.form.get(
                "name",
                "",
            ).split()
        )

        if not name:
            return render_template(
                "admin_symptom_type_form.html",
                symptom_type=symptom_type,
                symptom_type_display_name=(
                    get_reference_name(symptom_type)
                ),
                form=request.form,
                error="A név kötelező.",
            )

        duplicate = find_reference_by_name(
            SymptomType,
            name,
            exclude_id=symptom_type.id,
        )

        if duplicate is not None:
            return render_template(
                "admin_symptom_type_form.html",
                symptom_type=symptom_type,
                symptom_type_display_name=(
                    get_reference_name(symptom_type)
                ),
                form=request.form,
                error=(
                    "Már létezik ilyen tünettípus."
                ),
            )

        update_current_reference_translation(
            symptom_type,
            name=name,
        )

        db.session.commit()

        return redirect(
            f"/symptomtracker/admin/"
            f"symptom-types/"
            f"{symptom_type.id}/edit"
        )

    return render_template(
        "admin_symptom_type_form.html",
        symptom_type=symptom_type,
        symptom_type_display_name=(
            get_reference_name(symptom_type)
        ),
        form={},
        error=None,
    )


@main.route(
    "/admin/symptom-types/<int:symptom_type_id>/toggle",
    methods=["POST"],
)
def admin_toggle_symptom_type(
    symptom_type_id
):
    symptom_type = db.get_or_404(
        SymptomType,
        symptom_type_id,
    )

    symptom_type.active = (
        not symptom_type.active
    )

    db.session.commit()

    return redirect(
        f"/symptomtracker/admin/"
        f"symptom-types/"
        f"{symptom_type.id}/edit"
    )


@main.route("/admin/risk-components")
def admin_risk_components():
    search = request.args.get(
        "q",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "active",
    ).strip()

    query, display_name = (
        apply_reference_name_join(
            RiskComponent.query,
            RiskComponent,
        )
    )

    if status == "active":
        query = query.filter(
            RiskComponent.active.is_(True)
        )

    elif status == "inactive":
        query = query.filter(
            RiskComponent.active.is_(False)
        )

    if search:
        pattern = f"%{search}%"

        query = query.filter(
            or_(
                display_name.ilike(pattern),
                RiskComponent.category.ilike(pattern),
                reference_description_matches(
                    RiskComponent,
                    pattern,
                )
            )
        )

    risk_components = (
        query
        .order_by(
            RiskComponent.category,
            display_name,
        )
        .all()
    )

    ingredient_counts = {
        risk.id: len(risk.ingredients)
        for risk in risk_components
    }

    return render_template(
        "admin_risk_components.html",
        risk_components=risk_components,
        ingredient_counts=ingredient_counts,
        search=search,
        selected_status=status,
    )


@main.route(
    "/admin/risk-components/"
    "<int:risk_component_id>/ingredients",
    methods=["GET", "POST"],
)
def admin_risk_component_ingredients(
    risk_component_id
):
    risk_component = db.get_or_404(
        RiskComponent,
        risk_component_id,
    )

    if request.method == "POST":
        selected_ids = set(
            request.form.getlist(
                "ingredient_ids",
                type=int,
            )
        )

        existing_links = {
            link.ingredient_id: link
            for link
            in (
                IngredientRiskComponent.query
                .filter_by(
                    risk_component_id=(
                        risk_component.id
                    )
                )
                .all()
            )
        }

        for ingredient_id in selected_ids:
            ingredient = db.session.get(
                Ingredient,
                ingredient_id,
            )

            if ingredient is None:
                continue

            confidence = request.form.get(
                f"confidence_{ingredient_id}",
                "certain",
            )

            if confidence not in {
                "certain",
                "typical",
                "product_dependent",
            }:
                confidence = "certain"

            existing_link = (
                existing_links.get(
                    ingredient_id
                )
            )

            if existing_link is not None:
                existing_link.confidence = (
                    confidence
                )

                continue

            db.session.add(
                IngredientRiskComponent(
                    ingredient_id=(
                        ingredient.id
                    ),
                    risk_component_id=(
                        risk_component.id
                    ),
                    confidence=confidence,
                )
            )

        for (
            ingredient_id,
            existing_link
        ) in existing_links.items():
            if (
                ingredient_id
                not in selected_ids
            ):
                db.session.delete(
                    existing_link
                )

        db.session.commit()

        return redirect(
            f"/symptomtracker/admin/"
            f"risk-components/"
            f"{risk_component.id}/ingredients"
        )

    search = request.args.get(
        "q",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "all",
    ).strip()

    existing_links = {
        link.ingredient_id: link
        for link
        in (
            IngredientRiskComponent.query
            .filter_by(
                risk_component_id=(
                    risk_component.id
                )
            )
            .all()
        )
    }

    query = Ingredient.query

    if search:
        pattern = f"%{search}%"

        query = query.filter(
            reference_name_matches(
                Ingredient,
                pattern,
            )
        )

    if status == "linked":
        if existing_links:
            query = query.filter(
                Ingredient.id.in_(
                    existing_links.keys()
                )
            )
        else:
            query = query.filter(
                db.false()
            )

    elif status == "unlinked":
        if existing_links:
            query = query.filter(
                ~Ingredient.id.in_(
                    existing_links.keys()
                )
            )

    selected_confidences = {
        ingredient_id:
            link.confidence
        for (
            ingredient_id,
            link
        ) in existing_links.items()
    }

    return render_template(
        "admin_risk_component_ingredients.html",
        risk_component=risk_component,
        ingredients=ingredients,
        selected_confidences=(
            selected_confidences
        ),
        linked_count=len(
            existing_links
        ),
        search=search,
        selected_status=status,
    )


@main.route(
    "/admin/risk-components/new",
    methods=["GET", "POST"],
)
def admin_new_risk_component():
    if request.method == "POST":
        name = " ".join(
            request.form.get(
                "name",
                "",
            ).split()
        )

        category = request.form.get(
            "category",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        if not name or not category:
            return render_template(
                "admin_risk_component_form.html",
                risk_component=None,
                form=request.form,
                error=(
                    "A név és a kategória kötelező."
                ),
            )

        duplicate = find_reference_by_name(
            RiskComponent,
            name,
        )

        if duplicate is not None:
            return render_template(
                "admin_risk_component_form.html",
                risk_component=None,
                form=request.form,
                error=(
                    "Már létezik ilyen nevű "
                    "rizikófaktor."
                ),
            )

        risk_component = RiskComponent(
            name=name,
            category=category,
            description=description or None,
            active=True,
        )

        db.session.add(risk_component)
        db.session.flush()

        create_reference_translations(
            risk_component,
            name=risk_component.name,
            description=risk_component.description,
        )

        db.session.commit()

        return redirect(
            "/symptomtracker/admin/risk-components"
        )

    return render_template(
        "admin_risk_component_form.html",
        risk_component=None,
        form={},
        error=None,
    )


@main.route(
    "/admin/risk-components/<int:risk_component_id>/edit",
    methods=["GET", "POST"],
)
def admin_edit_risk_component(
    risk_component_id
):
    risk_component = db.get_or_404(
        RiskComponent,
        risk_component_id,
    )

    if request.method == "POST":
        name = " ".join(
            request.form.get(
                "name",
                "",
            ).split()
        )

        category = request.form.get(
            "category",
            "",
        ).strip()

        description = request.form.get(
            "description",
            "",
        ).strip()

        if not name or not category:
            return render_template(
                "admin_risk_component_form.html",
                risk_component=risk_component,
                risk_component_display_name=(
                    get_reference_name(
                        risk_component
                    )
                ),
                risk_component_display_description=(
                    get_reference_description(
                        risk_component
                    )
                ),
                form=request.form,
                error=(
                    "A név és a kategória kötelező."
                ),
            )

        duplicate = find_reference_by_name(
            RiskComponent,
            name,
            exclude_id=risk_component.id,
        )

        if duplicate is not None:
            return render_template(
                "admin_risk_component_form.html",
                risk_component=risk_component,
                risk_component_display_name=(
                    get_reference_name(
                        risk_component
                    )
                ),
                risk_component_display_description=(
                    get_reference_description(
                        risk_component
                    )
                ),
                form=request.form,
                error=(
                    "Már létezik ilyen nevű "
                    "rizikófaktor."
                ),
            )

        update_current_reference_translation(
            risk_component,
            name=name,
            description=description or None,
        )

        risk_component.category = category

        db.session.commit()

        return redirect(
            f"/symptomtracker/admin/"
            f"risk-components/"
            f"{risk_component.id}/edit"
        )

    return render_template(
        "admin_risk_component_form.html",
        risk_component=risk_component,
        risk_component_display_name=(
            get_reference_name(
                risk_component
            )
        ),
        risk_component_display_description=(
            get_reference_description(
                risk_component
            )
        ),
        form={},
        error=None,
    )


@main.route(
    "/admin/risk-components/<int:risk_component_id>/toggle",
    methods=["POST"],
)
def admin_toggle_risk_component(
    risk_component_id
):
    risk_component = db.get_or_404(
        RiskComponent,
        risk_component_id,
    )

    risk_component.active = (
        not risk_component.active
    )

    db.session.commit()

    return redirect(
        f"/symptomtracker/admin/"
        f"risk-components/"
        f"{risk_component.id}/edit"
    )


@main.route("/admin/ingredients")
def admin_ingredients():
    search = request.args.get(
        "q",
        "",
    ).strip()

    risk_status = request.args.get(
        "risk_status",
        "all",
    ).strip()

    if risk_status not in (
        "all",
        "with",
        "without",
    ):
        risk_status = "all"

    query, display_name = (
        apply_reference_name_join(
            Ingredient.query,
            Ingredient,
        )
    )

    if search:
        pattern = f"%{search}%"

        query = query.filter(
            display_name.ilike(pattern)
        )

    if risk_status == "with":
        query = query.filter(
            Ingredient.risk_components.any()
        )

    elif risk_status == "without":
        query = query.filter(
            ~Ingredient.risk_components.any()
        )

    ingredients = (
        query
        .order_by(display_name)
        .all()
    )

    return render_template(
        "admin_ingredients.html",
        ingredients=ingredients,
        search=search,
        selected_risk_status=risk_status,
    )


@main.route(
    "/admin/ingredients/<int:ingredient_id>/edit",
    methods=["GET", "POST"],
)
def admin_edit_ingredient(ingredient_id):
    ingredient = db.get_or_404(
        Ingredient,
        ingredient_id,
    )

    risk_query, risk_display_name = (
        apply_reference_name_join(
            RiskComponent.query
            .filter(
                RiskComponent.active.is_(True)
            ),
            RiskComponent,
        )
    )

    risk_components = (
        risk_query
        .order_by(
            RiskComponent.category,
            risk_display_name,
        )
        .all()
    )

    if request.method == "POST":
        name = request.form.get(
            "name",
            "",
        ).strip()

        if not name:
            return render_template(
                "admin_edit_ingredient.html",
                ingredient=ingredient,
                ingredient_display_name=(
                    get_reference_name(ingredient)
                ),
                risk_components=risk_components,
                selected_risks={},
                error="Az összetevő neve kötelező.",
            )

        duplicate = find_reference_by_name(
            Ingredient,
            name,
            exclude_id=ingredient.id,
        )

        if duplicate is not None:
            return render_template(
                "admin_edit_ingredient.html",
                ingredient=ingredient,
                ingredient_display_name=(
                    get_reference_name(ingredient)
                ),
                risk_components=risk_components,
                selected_risks={
                    item.risk_component_id:
                        item.confidence
                    for item
                    in ingredient.risk_components
                },
                error=(
                    "Már létezik ilyen nevű összetevő."
                ),
            )

        update_current_reference_translation(
            ingredient,
            name=name,
        )

        selected_ids = set(
            request.form.getlist(
                "risk_component_ids",
                type=int,
            )
        )

        existing_links = {
            item.risk_component_id: item
            for item
            in ingredient.risk_components
        }

        for risk_component_id in selected_ids:
            risk_component = db.session.get(
                RiskComponent,
                risk_component_id,
            )

            if risk_component is None:
                continue

            confidence = request.form.get(
                f"confidence_{risk_component_id}",
                "certain",
            )

            if confidence not in {
                "certain",
                "typical",
                "product_dependent",
            }:
                confidence = "certain"

            existing_link = (
                existing_links.get(
                    risk_component_id
                )
            )

            if existing_link is not None:
                existing_link.confidence = (
                    confidence
                )

                continue

            ingredient.risk_components.append(
                IngredientRiskComponent(
                    risk_component=risk_component,
                    confidence=confidence,
                )
            )

        for (
            risk_component_id,
            existing_link
        ) in existing_links.items():
            if (
                risk_component_id
                not in selected_ids
            ):
                db.session.delete(
                    existing_link
                )

        db.session.commit()

        return redirect(
            f"/symptomtracker/admin/"
            f"ingredients/{ingredient.id}/edit"
        )

    selected_risks = {
        item.risk_component_id:
            item.confidence
        for item
        in ingredient.risk_components
    }

    return render_template(
        "admin_edit_ingredient.html",
        ingredient=ingredient,
        ingredient_display_name=(
            get_reference_name(ingredient)
        ),
        risk_components=risk_components,
        selected_risks=selected_risks,
        error=None,
    )


@main.route("/admin/medications")
def admin_medications():
    search = request.args.get(
        "q",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "active",
    ).strip()

    query = Medication.query

    if status == "active":
        query = query.filter(
            Medication.active.is_(True)
        )

    elif status == "inactive":
        query = query.filter(
            Medication.active.is_(False)
        )

    if search:
        pattern = f"%{search}%"

        query = query.filter(
            Medication.name.ilike(pattern)
        )

    medications = (
        query
        .order_by(Medication.name)
        .all()
    )

    return render_template(
        "admin_medications.html",
        medications=medications,
        search=search,
        selected_status=status,
    )


@main.route(
    "/admin/medications/new",
    methods=["GET", "POST"],
)
def admin_new_medication():
    if request.method == "POST":
        name = " ".join(
            request.form.get(
                "name",
                "",
            ).split()
        )

        if not name:
            return render_template(
                "admin_medication_form.html",
                medication=None,
                form=request.form,
                error="A név kötelező.",
            )

        duplicate = (
            Medication.query
            .filter(
                db.func.lower(
                    Medication.name
                ) == name.lower()
            )
            .first()
        )

        if duplicate is not None:
            return render_template(
                "admin_medication_form.html",
                medication=None,
                form=request.form,
                error=(
                    "Már létezik ilyen gyógyszer."
                ),
            )

        medication = Medication(
            name=name,
            active=True,
        )

        db.session.add(medication)
        db.session.commit()

        return redirect(
            "/symptomtracker/admin/medications"
        )

    return render_template(
        "admin_medication_form.html",
        medication=None,
        form={},
        error=None,
    )


@main.route(
    "/admin/medications/<int:medication_id>/edit",
    methods=["GET", "POST"],
)
def admin_edit_medication(
    medication_id
):
    medication = db.get_or_404(
        Medication,
        medication_id,
    )

    if request.method == "POST":
        name = " ".join(
            request.form.get(
                "name",
                "",
            ).split()
        )

        if not name:
            return render_template(
                "admin_medication_form.html",
                medication=medication,
                form=request.form,
                error="A név kötelező.",
            )

        duplicate = (
            Medication.query
            .filter(
                db.func.lower(
                    Medication.name
                ) == name.lower()
            )
            .filter(
                Medication.id != medication.id
            )
            .first()
        )

        if duplicate is not None:
            return render_template(
                "admin_medication_form.html",
                medication=medication,
                form=request.form,
                error=(
                    "Már létezik ilyen gyógyszer."
                ),
            )

        medication.name = name

        db.session.commit()

        return redirect(
            f"/symptomtracker/admin/"
            f"medications/"
            f"{medication.id}/edit"
        )

    return render_template(
        "admin_medication_form.html",
        medication=medication,
        form={},
        error=None,
    )


@main.route(
    "/admin/medications/<int:medication_id>/toggle",
    methods=["POST"],
)
def admin_toggle_medication(
    medication_id
):
    medication = db.get_or_404(
        Medication,
        medication_id,
    )

    if (
        medication.is_default
        and medication.active
    ):
        return redirect(
            f"/symptomtracker/admin/"
            f"medications/"
            f"{medication.id}/edit"
        )

    medication.active = (
        not medication.active
    )

    db.session.commit()

    return redirect(
        f"/symptomtracker/admin/"
        f"medications/"
        f"{medication.id}/edit"
    )


@main.route(
    "/admin/medications/<int:medication_id>/default",
    methods=["POST"],
)
def admin_set_default_medication(
    medication_id
):
    medication = db.get_or_404(
        Medication,
        medication_id,
    )

    if not medication.active:
        return redirect(
            f"/symptomtracker/admin/"
            f"medications/"
            f"{medication.id}/edit"
        )

    Medication.query.update(
        {
            Medication.is_default: False
        },
        synchronize_session=False,
    )

    medication.is_default = True

    db.session.commit()

    return redirect(
        f"/symptomtracker/admin/"
        f"medications/"
        f"{medication.id}/edit"
    )


@main.route("/")
def index():
    default_medication = (
        Medication.query
        .filter(
            Medication.active.is_(True),
            Medication.is_default.is_(True),
        )
        .first()
    )

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
        default_medication=default_medication,
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
                                    reference_name_matches(
                                        Ingredient,
                                        pattern,
                                    )
                                )
                            ),
                        )
                    )
                ),

                Event.symptom_event.has(
                    or_(
                        SymptomEvent.symptom_type.has(
                            reference_name_matches(
                                SymptomType,
                                pattern,
                            )
                        ),

                        SymptomEvent.body_parts.any(
                            reference_name_matches(
                                BodyPart,
                                pattern,
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

            ended_at = request.form.get(
                "ended_at",
                "",
            ).strip()

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
                        order_reference_query(
                        SymptomType.query
                        .filter(
                            SymptomType.active.is_(True)
                        ),
                        SymptomType,
                    )
                        .all()
                    ),
                    body_parts=(
                        order_reference_query(
                        BodyPart.query
                        .filter(
                            BodyPart.active.is_(True)
                        ),
                        BodyPart,
                    )
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
                        order_reference_query(
                        SymptomType.query
                        .filter(
                            SymptomType.active.is_(True)
                        ),
                        SymptomType,
                    )
                        .all()
                    ),
                    body_parts=(
                        order_reference_query(
                        BodyPart.query
                        .filter(
                            BodyPart.active.is_(True)
                        ),
                        BodyPart,
                    )
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

            ended_at_utc = None

            if ended_at:
                try:
                    ended_at_utc = parse_local_datetime(
                        ended_at
                    )
                except ValueError:
                    return render_template(
                        "edit_event.html",
                        event=event,
                        local_occurred_at=occurred_at,
                        symptom_types=(
                            order_reference_query(
                            SymptomType.query
                            .filter(
                                SymptomType.active.is_(True)
                            ),
                            SymptomType,
                        )
                        .all()
                        ),
                        body_parts=(
                            order_reference_query(
                            BodyPart.query
                            .filter(
                                BodyPart.active.is_(True)
                            ),
                            BodyPart,
                        )
                        .all()
                        ),
                        selected_body_part_ids=(
                            selected_body_part_ids
                        ),
                        error=(
                            "Érvénytelen megszűnési időpont."
                        ),
                    )

                if ended_at_utc < event.occurred_at:
                    return render_template(
                        "edit_event.html",
                        event=event,
                        local_occurred_at=occurred_at,
                        symptom_types=(
                            order_reference_query(
                            SymptomType.query
                            .filter(
                                SymptomType.active.is_(True)
                            ),
                            SymptomType,
                        )
                        .all()
                        ),
                        body_parts=(
                            order_reference_query(
                            BodyPart.query
                            .filter(
                                BodyPart.active.is_(True)
                            ),
                            BodyPart,
                        )
                        .all()
                        ),
                        selected_body_part_ids=(
                            selected_body_part_ids
                        ),
                        error=(
                            "A megszűnés ideje nem lehet "
                            "korábbi a tünet kezdeténél."
                        ),
                    )

            event.symptom_event.symptom_type = (
                symptom_type
            )

            event.symptom_event.severity = severity

            event.symptom_event.ended_at = (
                ended_at_utc
            )

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
            order_reference_query(
            SymptomType.query
            .filter(SymptomType.active.is_(True)),
            SymptomType,
        )
            .all()
        )

        body_parts = (
            order_reference_query(
            BodyPart.query
            .filter(BodyPart.active.is_(True)),
            BodyPart,
        )
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
        admin_mode=False,
    )


@main.route("/admin/foods")
def admin_foods():
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
        admin_mode=True,
    )


@main.route(
    "/foods/new",
    methods=["GET", "POST"],
)
def new_food():
    return_to = request.values.get(
        "return_to",
        "log",
    ).strip()

    if return_to not in (
        "log",
        "admin",
    ):
        return_to = "log"

    ingredients = (
        order_reference_query(
        Ingredient.query,
        Ingredient,
    )
        .all()
    )

    selected_ingredient_ids = []

    if request.method == "POST":
        name = " ".join(
            request.form.get(
                "name",
                "",
            ).split()
        )

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
                return_to=return_to,
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
                return_to=return_to,
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

            ingredient = find_reference_by_name(
                Ingredient,
                ingredient_name,
            )

            if ingredient is None:
                ingredient = Ingredient(
                    name=ingredient_name.strip()
                )

                db.session.add(ingredient)
                db.session.flush()

                create_reference_translations(
                    ingredient,
                    name=ingredient.name,
                )

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

        db.session.flush()

        risk_component_ids = set()

        if used_ingredient_ids:
            ingredient_risks = (
                IngredientRiskComponent.query
                .filter(
                    IngredientRiskComponent.ingredient_id.in_(
                        used_ingredient_ids
                    )
                )
                .all()
            )

            risk_component_ids = {
                item.risk_component_id
                for item in ingredient_risks
            }

        for risk_component_id in sorted(
            risk_component_ids
        ):
            food.risk_components.append(
                FoodRiskComponent(
                    risk_component_id=risk_component_id,
                    source="automatic",
                )
            )

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

        if return_to == "admin":
            return redirect(
                "/symptomtracker/admin/foods"
            )

        return redirect(
            f"/symptomtracker/foods/"
            f"{food.id}/log"
        )

    return render_template(
        "food_form.html",
        ingredients=ingredients,
        selected_ingredient_ids=[],
        form={},
        return_to=return_to,
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
        order_reference_query(
        Ingredient.query,
        Ingredient,
    )
        .all()
    )

    if request.method == "POST":
        name = " ".join(
            request.form.get(
                "name",
                "",
            ).split()
        )

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

        selected_risk_component_ids = set(
            request.form.getlist(
                "risk_component_ids",
                type=int,
            )
        )

        presented_risk_component_ids = set(
            request.form.getlist(
                "presented_risk_component_ids",
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

            ingredient = find_reference_by_name(
                Ingredient,
                ingredient_name,
            )

            if ingredient is None:
                ingredient = Ingredient(
                    name=ingredient_name.strip()
                )

                db.session.add(ingredient)
                db.session.flush()

                create_reference_translations(
                    ingredient,
                    name=ingredient.name,
                )

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

        existing_risks = {
            item.risk_component_id: item
            for item in food.risk_components
        }

        db.session.flush()

        suggested_risk_component_ids = set()

        if used_ingredient_ids:
            ingredient_risks = (
                IngredientRiskComponent.query
                .filter(
                    IngredientRiskComponent.ingredient_id.in_(
                        used_ingredient_ids
                    )
                )
                .all()
            )

            suggested_risk_component_ids = {
                item.risk_component_id
                for item in ingredient_risks
            }

        for risk_component_id in sorted(
            suggested_risk_component_ids
        ):
            existing_risk = existing_risks.get(
                risk_component_id
            )

            if existing_risk is not None:
                if (
                    risk_component_id
                    in presented_risk_component_ids
                ):
                    existing_risk.enabled = (
                        risk_component_id
                        in selected_risk_component_ids
                    )

                continue

            food.risk_components.append(
                FoodRiskComponent(
                    risk_component_id=risk_component_id,
                    source="automatic",
                    enabled=(
                        risk_component_id
                        not in presented_risk_component_ids
                        or risk_component_id
                        in selected_risk_component_ids
                    ),
                )
            )

        for risk_component_id, existing_risk in (
            existing_risks.items()
        ):
            if (
                risk_component_id
                not in suggested_risk_component_ids
            ):
                db.session.delete(existing_risk)

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

    selected_food_risk_ids = {
        item.risk_component_id
        for item in food.risk_components
        if item.enabled
    }

    risk_details_by_id = {}

    confidence_labels = {
        "certain": "Biztos",
        "typical": "Tipikus",
        "product_dependent": "Termékfüggő",
    }

    for food_ingredient in food.ingredients:
        ingredient = food_ingredient.ingredient

        for ingredient_risk in ingredient.risk_components:
            risk = ingredient_risk.risk_component

            if risk.id not in risk_details_by_id:
                risk_details_by_id[risk.id] = {
                    "risk": risk,
                    "sources": [],
                }

            risk_details_by_id[risk.id]["sources"].append(
                {
                    "ingredient": ingredient.name,
                    "confidence": confidence_labels.get(
                        ingredient_risk.confidence,
                        ingredient_risk.confidence,
                    ),
                }
            )

    risk_details = sorted(
        risk_details_by_id.values(),
        key=lambda item: item["risk"].name.lower(),
    )

    return render_template(
        "edit_food.html",
        food=food,
        ingredients=ingredients,
        selected_ingredient_ids=(
            selected_ingredient_ids
        ),
        risk_details=risk_details,
        selected_food_risk_ids=(
            selected_food_risk_ids
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
        order_reference_query(
        SymptomType.query
        .filter(SymptomType.active.is_(True)),
        SymptomType,
    )
    .all()
    )

    body_parts = (
        order_reference_query(
        BodyPart.query
        .filter(BodyPart.active.is_(True)),
        BodyPart,
    )
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

        ended_at = request.form.get(
            "ended_at",
            "",
        ).strip()

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

            ended_at_utc = None

            if ended_at:
                ended_at_utc = parse_local_datetime(
                    ended_at
                )

                if ended_at_utc < occurred_at_utc:
                    raise ValueError

        except ValueError:
            return render_template(
                "symptom_form.html",
                symptom_types=symptom_types,
                body_parts=body_parts,
                form=request.form,
                selected_body_part_ids=selected_body_part_ids,
                error=(
                    "Érvénytelen dátum vagy időpont, "
                    "illetve a megszűnés nem lehet "
                    "korábbi a kezdetnél."
                ),
            )

        event = Event(
            event_type="symptom",
            occurred_at=occurred_at_utc,
            notes=notes or None,
        )

        symptom_event = SymptomEvent(
            symptom_type=symptom_type,
            severity=severity,
            ended_at=ended_at_utc,
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
    "/api/events/default-medication",
    methods=["POST"],
)
def add_default_medication():
    medication = (
        Medication.query
        .filter(
            Medication.active.is_(True),
            Medication.is_default.is_(True),
        )
        .first()
    )

    if medication is None:
        return jsonify(
            {
                "ok": False,
                "message": (
                    "Nincs aktív alapértelmezett "
                    "gyógyszer beállítva."
                ),
            }
        ), 500

    event = Event(
        event_type="medication",
        occurred_at=datetime.now(
            timezone.utc
        ),
    )

    medication_event = MedicationEvent(
        medication=medication,
    )

    event.medication_event = (
        medication_event
    )

    db.session.add(event)
    db.session.commit()

    return jsonify(
        {
            "ok": True,
            "event_id": event.id,
            "message": (
                f"{medication.name} rögzítve."
            ),
        }
    )
