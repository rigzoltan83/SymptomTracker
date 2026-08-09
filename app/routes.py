from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
)

from sqlalchemy import or_

from app import db
from app.models import (
    BodyPart,
    Event,
    FoodEvent,
    Medication,
    MedicationEvent,
    SymptomEvent,
    SymptomType,
)


main = Blueprint("main", __name__)

LOCAL_TIMEZONE = ZoneInfo("Europe/Budapest")


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

        query = (
            query
            .outerjoin(
                MedicationEvent,
                MedicationEvent.event_id == Event.id,
            )
            .outerjoin(
                Medication,
                Medication.id
                == MedicationEvent.medication_id,
            )
            .outerjoin(
                FoodEvent,
                FoodEvent.event_id == Event.id,
            )
            .outerjoin(
                SymptomEvent,
                SymptomEvent.event_id == Event.id,
            )
            .filter(
                or_(
                    Event.notes.ilike(pattern),
                    Medication.name.ilike(pattern),
                )
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

        db.session.commit()

        return redirect(
            "/symptomtracker/events"
        )

    symptom_types = []
    body_parts = []
    selected_body_part_ids = []

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
