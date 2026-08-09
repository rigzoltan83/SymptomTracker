from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import BodyPart, Medication, SymptomType


MEDICATIONS = [
    "Cetirizin",
]


SYMPTOM_TYPES = [
    "Viszketés",
    "Kiütés",
]


BODY_PARTS = [
    "Fej",
    "Arc",
    "Nyak",
    "Mellkas",
    "Has",
    "Hát",
    "Bal váll",
    "Jobb váll",
    "Bal felkar",
    "Jobb felkar",
    "Bal alkar",
    "Jobb alkar",
    "Bal kéz",
    "Jobb kéz",
    "Bal comb",
    "Jobb comb",
    "Bal lábszár",
    "Jobb lábszár",
    "Bal lábfej",
    "Jobb lábfej",
]


def get_or_create(model, name):
    item = model.query.filter_by(name=name).first()

    if item is None:
        item = model(name=name)
        db.session.add(item)

    return item


def seed():
    for name in MEDICATIONS:
        get_or_create(
            Medication,
            name,
        )

    for name in SYMPTOM_TYPES:
        get_or_create(
            SymptomType,
            name,
        )

    for name in BODY_PARTS:
        get_or_create(
            BodyPart,
            name,
        )

    db.session.commit()


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        seed()

    print("SymptomTracker alapadatok feltöltve.")
