from datetime import (
    datetime,
    timedelta,
    timezone,
)
from statistics import median

from app.models import (
    Event,
    RiskComponent,
)

from app import db

def _food_risk_ids(event):
    if (
        event.food_event is None
        or event.food_event.food is None
    ):
        return set()

    return {
        link.risk_component_id
        for link
        in event.food_event.food.risk_components
        if (
            link.enabled
            and link.risk_component is not None
            and link.risk_component.active
        )
    }


def _matching_symptoms_after(
    food_event,
    symptom_events,
    window_end,
):
    return [
        symptom
        for symptom in symptom_events
        if (
            symptom.occurred_at
            >= food_event.occurred_at
            and symptom.occurred_at
            <= window_end
        )
    ]


def _signal_label(
    exposed_count,
    exposed_rate,
    control_rate,
):
    if exposed_count < 3:
        return "Kevés adat"

    difference = (
        exposed_rate
        - control_rate
    )

    if (
        exposed_count >= 5
        and difference >= 0.30
    ):
        return "Magasabb együttjárás"

    if (
        exposed_count >= 4
        and difference >= 0.15
    ):
        return "Mérsékelt együttjárás"

    if difference > 0:
        return "Enyhe együttjárás"

    return "Nem látszik többlet"


def build_analysis(
    window_hours=12,
    days=90,
    symptom_type_id=None,
):
    now = datetime.now(
        timezone.utc
    )

    start_at = None

    if days:
        start_at = (
            now
            - timedelta(days=days)
        )

    food_query = (
        Event.query
        .filter(
            Event.active.is_(True),
            Event.event_type == "food",
            Event.occurred_at <= now,
        )
    )

    symptom_query = (
        Event.query
        .filter(
            Event.active.is_(True),
            Event.event_type == "symptom",
            Event.occurred_at <= now,
        )
    )

    if start_at is not None:
        food_query = food_query.filter(
            Event.occurred_at >= start_at
        )

        symptom_query = (
            symptom_query.filter(
                Event.occurred_at >= start_at
            )
        )

    food_events = (
        food_query
        .order_by(Event.occurred_at)
        .all()
    )

    symptom_events = (
        symptom_query
        .order_by(Event.occurred_at)
        .all()
    )

    if symptom_type_id:
        symptom_events = [
            event
            for event in symptom_events
            if (
                event.symptom_event
                and event.symptom_event.symptom_type_id
                == symptom_type_id
            )
        ]

    window = timedelta(
        hours=window_hours
    )

    food_risks = {}

    all_risk_ids = set()

    for food_event in food_events:
        risk_ids = _food_risk_ids(
            food_event
        )

        food_risks[
            food_event.id
        ] = risk_ids

        all_risk_ids.update(
            risk_ids
        )

    food_outcomes = {}

    for food_event in food_events:
        matching = (
            _matching_symptoms_after(
                food_event,
                symptom_events,
                food_event.occurred_at
                + window,
            )
        )

        first_symptom = (
            matching[0]
            if matching
            else None
        )

        delay_hours = None

        if first_symptom is not None:
            delay_hours = (
                first_symptom.occurred_at
                - food_event.occurred_at
            ).total_seconds() / 3600

        food_outcomes[
            food_event.id
        ] = {
            "hit": bool(matching),
            "symptoms": matching,
            "first_symptom": (
                first_symptom
            ),
            "delay_hours": (
                delay_hours
            ),
        }

    risk_objects = {
        risk.id: risk
        for risk in (
            RiskComponent.query
            .filter(
                RiskComponent.id.in_(
                    all_risk_ids
                )
            )
            .all()
            if all_risk_ids
            else []
        )
    }

    risk_stats = []

    for risk_id in all_risk_ids:
        exposed = [
            event
            for event in food_events
            if risk_id
            in food_risks[event.id]
        ]

        controls = [
            event
            for event in food_events
            if risk_id
            not in food_risks[event.id]
        ]

        exposed_hits = [
            event
            for event in exposed
            if food_outcomes[
                event.id
            ]["hit"]
        ]

        control_hits = [
            event
            for event in controls
            if food_outcomes[
                event.id
            ]["hit"]
        ]

        exposed_count = len(
            exposed
        )

        control_count = len(
            controls
        )

        exposed_hit_count = len(
            exposed_hits
        )

        control_hit_count = len(
            control_hits
        )

        exposed_rate = (
            exposed_hit_count
            / exposed_count
            if exposed_count
            else 0
        )

        control_rate = (
            control_hit_count
            / control_count
            if control_count
            else 0
        )

        rate_difference = (
            exposed_rate
            - control_rate
        )

        lift = None

        if control_rate > 0:
            lift = (
                exposed_rate
                / control_rate
            )

        delays = [
            food_outcomes[
                event.id
            ]["delay_hours"]
            for event in exposed_hits
            if food_outcomes[
                event.id
            ]["delay_hours"]
            is not None
        ]

        median_delay = (
            median(delays)
            if delays
            else None
        )

        symptom_counts = {}

        for event in exposed_hits:
            for symptom in (
                food_outcomes[
                    event.id
                ]["symptoms"]
            ):
                if not symptom.symptom_event:
                    continue

                symptom_type = (
                    symptom
                    .symptom_event
                    .symptom_type
                )

                if symptom_type is None:
                    continue

                symptom_counts[
                    symptom_type.name
                ] = (
                    symptom_counts.get(
                        symptom_type.name,
                        0,
                    )
                    + 1
                )

        top_symptoms = sorted(
            symptom_counts.items(),
            key=lambda item: (
                -item[1],
                item[0].lower(),
            ),
        )[:5]

        risk = risk_objects.get(
            risk_id
        )

        if risk is None:
            continue

        risk_stats.append(
            {
                "risk_id": risk.id,
                "name": risk.name,
                "category": (
                    risk.category
                ),
                "exposed_count": (
                    exposed_count
                ),
                "exposed_hits": (
                    exposed_hit_count
                ),
                "exposed_rate": (
                    exposed_rate
                ),
                "control_count": (
                    control_count
                ),
                "control_hits": (
                    control_hit_count
                ),
                "control_rate": (
                    control_rate
                ),
                "rate_difference": (
                    rate_difference
                ),
                "lift": lift,
                "median_delay": (
                    median_delay
                ),
                "signal": (
                    _signal_label(
                        exposed_count,
                        exposed_rate,
                        control_rate,
                    )
                ),
                "top_symptoms": (
                    top_symptoms
                ),
            }
        )

    risk_stats.sort(
        key=lambda item: (
            -item["rate_difference"],
            -item["exposed_count"],
            item["name"].lower(),
        )
    )

    combination_stats = []

    sorted_risk_ids = sorted(
        all_risk_ids
    )

    for index, first_risk_id in enumerate(
        sorted_risk_ids
    ):
        for second_risk_id in (
            sorted_risk_ids[
                index + 1:
            ]
        ):
            pair_exposed = [
                event
                for event in food_events
                if (
                    first_risk_id
                    in food_risks[event.id]
                    and second_risk_id
                    in food_risks[event.id]
                )
            ]

            single_only = [
                event
                for event in food_events
                if (
                    (
                        first_risk_id
                        in food_risks[event.id]
                    )
                    !=
                    (
                        second_risk_id
                        in food_risks[event.id]
                    )
                )
            ]

            pair_count = len(
                pair_exposed
            )

            single_count = len(
                single_only
            )

            if pair_count < 2:
                continue

            pair_hits = [
                event
                for event in pair_exposed
                if food_outcomes[
                    event.id
                ]["hit"]
            ]

            single_hits = [
                event
                for event in single_only
                if food_outcomes[
                    event.id
                ]["hit"]
            ]

            pair_hit_count = len(
                pair_hits
            )

            single_hit_count = len(
                single_hits
            )

            pair_rate = (
                pair_hit_count
                / pair_count
                if pair_count
                else 0
            )

            single_rate = (
                single_hit_count
                / single_count
                if single_count
                else 0
            )

            difference = (
                pair_rate
                - single_rate
            )

            lift = None

            if single_rate > 0:
                lift = (
                    pair_rate
                    / single_rate
                )

            first_risk = (
                risk_objects.get(
                    first_risk_id
                )
            )

            second_risk = (
                risk_objects.get(
                    second_risk_id
                )
            )

            if (
                first_risk is None
                or second_risk is None
            ):
                continue

            delays = [
                food_outcomes[
                    event.id
                ]["delay_hours"]
                for event in pair_hits
                if food_outcomes[
                    event.id
                ]["delay_hours"]
                is not None
            ]

            median_delay = (
                median(delays)
                if delays
                else None
            )

            if pair_count < 3:
                signal = "Kevés adat"

            elif (
                pair_count >= 5
                and difference >= 0.30
            ):
                signal = (
                    "Erős kombinációs jel"
                )

            elif difference >= 0.15:
                signal = (
                    "Mérsékelt kombinációs jel"
                )

            elif difference > 0:
                signal = (
                    "Enyhe kombinációs jel"
                )

            else:
                signal = (
                    "Nem látszik kombinációs többlet"
                )

            combination_stats.append(
                {
                    "first_risk_id": (
                        first_risk.id
                    ),
                    "first_name": (
                        first_risk.name
                    ),
                    "second_risk_id": (
                        second_risk.id
                    ),
                    "second_name": (
                        second_risk.name
                    ),
                    "pair_count": (
                        pair_count
                    ),
                    "pair_hits": (
                        pair_hit_count
                    ),
                    "pair_rate": (
                        pair_rate
                    ),
                    "single_count": (
                        single_count
                    ),
                    "single_hits": (
                        single_hit_count
                    ),
                    "single_rate": (
                        single_rate
                    ),
                    "rate_difference": (
                        difference
                    ),
                    "lift": lift,
                    "median_delay": (
                        median_delay
                    ),
                    "signal": signal,
                }
            )

    combination_stats.sort(
        key=lambda item: (
            -item["rate_difference"],
            -item["pair_count"],
            item["first_name"].lower(),
            item["second_name"].lower(),
        )
    )

    combination_stats = (
        combination_stats[:30]
    )

    symptom_backtrace = []

    for symptom in reversed(
        symptom_events
    ):
        window_start = (
            symptom.occurred_at
            - window
        )

        preceding_foods = [
            event
            for event in food_events
            if (
                event.occurred_at
                <= symptom.occurred_at
                and event.occurred_at
                >= window_start
            )
        ]

        risks = {}

        foods = []

        for food_event in (
            reversed(
                preceding_foods
            )
        ):
            food = (
                food_event
                .food_event
                .food
                if food_event.food_event
                else None
            )

            if food is None:
                continue

            delay_hours = (
                symptom.occurred_at
                - food_event.occurred_at
            ).total_seconds() / 3600

            foods.append(
                {
                    "event_id": (
                        food_event.id
                    ),
                    "food_id": food.id,
                    "name": food.name,
                    "brand": food.brand,
                    "occurred_at": (
                        food_event
                        .occurred_at
                    ),
                    "delay_hours": (
                        delay_hours
                    ),
                }
            )

            for risk_id in (
                food_risks.get(
                    food_event.id,
                    set(),
                )
            ):
                risk = (
                    risk_objects.get(
                        risk_id
                    )
                )

                if risk is not None:
                    risks[
                        risk.id
                    ] = risk.name

        symptom_event = (
            symptom.symptom_event
        )

        symptom_backtrace.append(
            {
                "event_id": symptom.id,
                "occurred_at": (
                    symptom.occurred_at
                ),
                "symptom_name": (
                    symptom_event
                    .symptom_type
                    .name
                    if (
                        symptom_event
                        and symptom_event
                        .symptom_type
                    )
                    else "Tünet"
                ),
                "severity": (
                    symptom_event.severity
                    if symptom_event
                    else None
                ),
                "foods": foods,
                "risks": sorted(
                    risks.values(),
                    key=str.lower,
                ),
            }
        )

    symptom_backtrace = (
        symptom_backtrace[:50]
    )

    symptom_with_prior_food = sum(
        1
        for item
        in symptom_backtrace
        if item["foods"]
    )

    summary = {
        "food_events": len(
            food_events
        ),
        "symptom_events": len(
            symptom_events
        ),
        "risk_components": len(
            risk_stats
        ),
        "symptoms_with_prior_food": (
            symptom_with_prior_food
        ),
    }

    return {
        "summary": summary,
        "risk_stats": risk_stats,
        "combination_stats": (
            combination_stats
        ),
        "symptom_backtrace": (
            symptom_backtrace
        ),
        "window_hours": (
            window_hours
        ),
        "days": days,
        "symptom_type_id": (
            symptom_type_id
        ),
    }

def build_risk_detail(
    risk_component_id,
    window_hours=12,
    days=90,
    symptom_type_id=None,
):
    risk = (
        RiskComponent.query
        .filter_by(
            id=risk_component_id
        )
        .first()
    )

    if risk is None:
        return None

    now = datetime.now(
        timezone.utc
    )

    start_at = None

    if days:
        start_at = (
            now
            - timedelta(days=days)
        )

    food_query = (
        Event.query
        .filter(
            Event.active.is_(True),
            Event.event_type == "food",
            Event.occurred_at <= now,
        )
    )

    symptom_query = (
        Event.query
        .filter(
            Event.active.is_(True),
            Event.event_type == "symptom",
            Event.occurred_at <= now,
        )
    )

    if start_at is not None:
        food_query = food_query.filter(
            Event.occurred_at >= start_at
        )

        symptom_query = symptom_query.filter(
            Event.occurred_at >= start_at
        )

    food_events = (
        food_query
        .order_by(
            Event.occurred_at
        )
        .all()
    )

    symptom_events = (
        symptom_query
        .order_by(
            Event.occurred_at
        )
        .all()
    )

    if symptom_type_id:
        symptom_events = [
            event
            for event in symptom_events
            if (
                event.symptom_event
                and
                event.symptom_event.symptom_type_id
                == symptom_type_id
            )
        ]

    exposed_food_events = [
        event
        for event in food_events
        if (
            risk_component_id
            in _food_risk_ids(event)
        )
    ]

    window = timedelta(
        hours=window_hours
    )

    exposures = []

    total_hits = 0

    for food_event in reversed(
        exposed_food_events
    ):
        matching_symptoms = (
            _matching_symptoms_after(
                food_event,
                symptom_events,
                food_event.occurred_at
                + window,
            )
        )

        if matching_symptoms:
            total_hits += 1

        symptom_rows = []

        for symptom in matching_symptoms:
            symptom_event = (
                symptom.symptom_event
            )

            if symptom_event is None:
                continue

            delay_hours = (
                symptom.occurred_at
                - food_event.occurred_at
            ).total_seconds() / 3600

            duration_hours = None

            if symptom_event.ended_at:
                duration_hours = (
                    symptom_event.ended_at
                    - symptom.occurred_at
                ).total_seconds() / 3600

            symptom_rows.append(
                {
                    "event_id": symptom.id,
                    "name": (
                        symptom_event
                        .symptom_type
                        .name
                        if symptom_event.symptom_type
                        else "Tünet"
                    ),
                    "occurred_at": (
                        symptom.occurred_at
                    ),
                    "severity": (
                        symptom_event.severity
                    ),
                    "delay_hours": (
                        delay_hours
                    ),
                    "duration_hours": (
                        duration_hours
                    ),
                }
            )

        food = (
            food_event.food_event.food
            if food_event.food_event
            else None
        )

        if food is None:
            continue

        exposures.append(
            {
                "event_id": food_event.id,
                "food_id": food.id,
                "food_name": food.name,
                "brand": food.brand,
                "amount": (
                    food_event
                    .food_event
                    .amount
                ),
                "occurred_at": (
                    food_event.occurred_at
                ),
                "symptoms": symptom_rows,
                "has_symptom": bool(
                    symptom_rows
                ),
            }
        )

    food_stats_by_id = {}

    for exposure in exposures:
        food_id = exposure["food_id"]

        if food_id not in food_stats_by_id:
            food_stats_by_id[food_id] = {
                "food_id": food_id,
                "name": exposure["food_name"],
                "brand": exposure["brand"],
                "exposure_count": 0,
                "hit_count": 0,
                "severity_values": [],
                "delay_values": [],
            }

        row = food_stats_by_id[
            food_id
        ]

        row["exposure_count"] += 1

        if exposure["has_symptom"]:
            row["hit_count"] += 1

        for symptom in exposure["symptoms"]:
            if (
                symptom["severity"]
                is not None
            ):
                row[
                    "severity_values"
                ].append(
                    symptom["severity"]
                )

            if (
                symptom["delay_hours"]
                is not None
            ):
                row[
                    "delay_values"
                ].append(
                    symptom["delay_hours"]
                )

    food_stats = []

    for row in (
        food_stats_by_id.values()
    ):
        exposure_count = (
            row["exposure_count"]
        )

        hit_count = (
            row["hit_count"]
        )

        hit_rate = (
            hit_count / exposure_count
            if exposure_count
            else 0
        )

        average_severity = None

        if row["severity_values"]:
            average_severity = (
                sum(
                    row[
                        "severity_values"
                    ]
                )
                / len(
                    row[
                        "severity_values"
                    ]
                )
            )

        median_delay = None

        if row["delay_values"]:
            median_delay = median(
                row["delay_values"]
            )

        food_stats.append(
            {
                "food_id": (
                    row["food_id"]
                ),
                "name": row["name"],
                "brand": row["brand"],
                "exposure_count": (
                    exposure_count
                ),
                "hit_count": (
                    hit_count
                ),
                "hit_rate": (
                    hit_rate
                ),
                "average_severity": (
                    average_severity
                ),
                "median_delay": (
                    median_delay
                ),
            }
        )

    food_stats.sort(
        key=lambda row: (
            -row["hit_rate"],
            -row["exposure_count"],
            row["name"].lower(),
        )
    )

    analysis = build_analysis(
        window_hours=window_hours,
        days=days,
        symptom_type_id=symptom_type_id,
    )

    risk_stat = next(
        (
            row
            for row
            in analysis["risk_stats"]
            if row["risk_id"]
            == risk_component_id
        ),
        None,
    )

    return {
        "risk": risk,
        "stat": risk_stat,
        "exposures": exposures,
        "food_stats": food_stats,
        "exposure_count": len(
            exposures
        ),
        "hit_count": total_hits,
        "window_hours": (
            window_hours
        ),
        "days": days,
        "symptom_type_id": (
            symptom_type_id
        ),
    }


def build_combination_detail(
    first_risk_id,
    second_risk_id,
    window_hours=12,
    days=90,
    symptom_type_id=None,
):
    first_risk = db.session.get(
        RiskComponent,
        first_risk_id,
    )

    second_risk = db.session.get(
        RiskComponent,
        second_risk_id,
    )

    if (
        first_risk is None
        or second_risk is None
        or first_risk.id == second_risk.id
    ):
        return None

    now = datetime.now(
        timezone.utc
    )

    start_at = None

    if days:
        start_at = (
            now
            - timedelta(days=days)
        )

    food_query = (
        Event.query
        .filter(
            Event.active.is_(True),
            Event.event_type == "food",
            Event.occurred_at <= now,
        )
    )

    symptom_query = (
        Event.query
        .filter(
            Event.active.is_(True),
            Event.event_type == "symptom",
            Event.occurred_at <= now,
        )
    )

    if start_at is not None:
        food_query = food_query.filter(
            Event.occurred_at >= start_at
        )

        symptom_query = symptom_query.filter(
            Event.occurred_at >= start_at
        )

    food_events = (
        food_query
        .order_by(Event.occurred_at)
        .all()
    )

    symptom_events = (
        symptom_query
        .order_by(Event.occurred_at)
        .all()
    )

    if symptom_type_id:
        symptom_events = [
            event
            for event in symptom_events
            if (
                event.symptom_event
                and
                event.symptom_event.symptom_type_id
                == symptom_type_id
            )
        ]

    window = timedelta(
        hours=window_hours
    )

    exposures = []

    for event in reversed(food_events):
        risk_ids = _food_risk_ids(
            event
        )

        if not (
            first_risk_id in risk_ids
            and second_risk_id in risk_ids
        ):
            continue

        if (
            event.food_event is None
            or event.food_event.food is None
        ):
            continue

        matching_symptoms = (
            _matching_symptoms_after(
                event,
                symptom_events,
                event.occurred_at + window,
            )
        )

        symptoms = []

        for symptom in matching_symptoms:
            symptom_event = (
                symptom.symptom_event
            )

            if symptom_event is None:
                continue

            delay_hours = (
                symptom.occurred_at
                - event.occurred_at
            ).total_seconds() / 3600

            symptoms.append(
                {
                    "event_id": symptom.id,
                    "name": (
                        symptom_event
                        .symptom_type
                        .name
                        if symptom_event.symptom_type
                        else "Tünet"
                    ),
                    "occurred_at": (
                        symptom.occurred_at
                    ),
                    "severity": (
                        symptom_event.severity
                    ),
                    "delay_hours": (
                        delay_hours
                    ),
                }
            )

        food = (
            event.food_event.food
        )

        exposures.append(
            {
                "event_id": event.id,
                "food_id": food.id,
                "food_name": food.name,
                "brand": food.brand,
                "amount": (
                    event.food_event.amount
                ),
                "occurred_at": (
                    event.occurred_at
                ),
                "symptoms": symptoms,
                "has_symptom": bool(
                    symptoms
                ),
            }
        )

    food_stats_by_id = {}

    for exposure in exposures:
        food_id = exposure["food_id"]

        if food_id not in food_stats_by_id:
            food_stats_by_id[food_id] = {
                "food_id": food_id,
                "name": (
                    exposure["food_name"]
                ),
                "brand": (
                    exposure["brand"]
                ),
                "count": 0,
                "hits": 0,
                "severity_values": [],
                "delay_values": [],
            }

        row = food_stats_by_id[
            food_id
        ]

        row["count"] += 1

        if exposure["has_symptom"]:
            row["hits"] += 1

        for symptom in exposure[
            "symptoms"
        ]:
            if (
                symptom["severity"]
                is not None
            ):
                row[
                    "severity_values"
                ].append(
                    symptom["severity"]
                )

            row[
                "delay_values"
            ].append(
                symptom["delay_hours"]
            )

    food_stats = []

    for row in (
        food_stats_by_id.values()
    ):
        hit_rate = (
            row["hits"] / row["count"]
            if row["count"]
            else 0
        )

        average_severity = None

        if row["severity_values"]:
            average_severity = (
                sum(
                    row[
                        "severity_values"
                    ]
                )
                / len(
                    row[
                        "severity_values"
                    ]
                )
            )

        median_delay = None

        if row["delay_values"]:
            median_delay = median(
                row["delay_values"]
            )

        food_stats.append(
            {
                "food_id": (
                    row["food_id"]
                ),
                "name": row["name"],
                "brand": row["brand"],
                "count": row["count"],
                "hits": row["hits"],
                "hit_rate": hit_rate,
                "average_severity": (
                    average_severity
                ),
                "median_delay": (
                    median_delay
                ),
            }
        )

    food_stats.sort(
        key=lambda row: (
            -row["hit_rate"],
            -row["count"],
            row["name"].lower(),
        )
    )

    analysis = build_analysis(
        window_hours=window_hours,
        days=days,
        symptom_type_id=(
            symptom_type_id
        ),
    )

    combination_stat = next(
        (
            row
            for row
            in analysis[
                "combination_stats"
            ]
            if {
                row["first_risk_id"],
                row["second_risk_id"],
            }
            == {
                first_risk_id,
                second_risk_id,
            }
        ),
        None,
    )

    return {
        "first_risk": first_risk,
        "second_risk": second_risk,
        "stat": combination_stat,
        "food_stats": food_stats,
        "exposures": exposures,
    }
