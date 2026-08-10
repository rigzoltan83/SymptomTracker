from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import RiskComponent


RISK_COMPONENTS = [
    # Klasszikus allergén / immunológiai szempontok
    (
        "Glutén",
        "allergen",
        "Glutént tartalmazó gabonákhoz kapcsolódó komponens.",
    ),
    (
        "Tejfehérje",
        "allergen",
        "Tejeredetű fehérjék.",
    ),
    (
        "Tojás",
        "allergen",
        "Tojáshoz kapcsolódó allergén.",
    ),
    (
        "Szója",
        "allergen",
        "Szójához kapcsolódó allergén.",
    ),
    (
        "Földimogyoró",
        "allergen",
        "Földimogyoróhoz kapcsolódó allergén.",
    ),
    (
        "Diófélék",
        "allergen",
        "Diófélékhez kapcsolódó allergéncsoport.",
    ),
    (
        "Szezám",
        "allergen",
        "Szezámmaghoz kapcsolódó allergén.",
    ),
    (
        "Mustár",
        "allergen",
        "Mustárhoz kapcsolódó allergén.",
    ),
    (
        "Zeller",
        "allergen",
        "Zellerhez kapcsolódó allergén.",
    ),
    (
        "Szulfit",
        "allergen",
        "Szulfitok és kén-dioxid jelölésére.",
    ),

    # Intolerancia / felszívódási szempontok
    (
        "Laktóz",
        "intolerance",
        "Tejcukor.",
    ),
    (
        "Fruktóz",
        "intolerance",
        "Gyümölcscukor.",
    ),

    # FODMAP csoportok
    (
        "Fruktán",
        "fodmap",
        "Fruktán típusú fermentálható szénhidrát.",
    ),
    (
        "GOS",
        "fodmap",
        "Galakto-oligoszacharidok.",
    ),
    (
        "Szorbit",
        "fodmap",
        "Poliol.",
    ),
    (
        "Mannit",
        "fodmap",
        "Poliol.",
    ),
    (
        "Xilit",
        "fodmap",
        "Poliol.",
    ),

    # Egyéb későbbi elemzési címkék
    (
        "Hisztamin-kockázat",
        "biogenic_amine",
        "Hisztaminnal kapcsolatos kockázati címke.",
    ),
]


def seed():
    created = 0
    existing = 0

    for name, category, description in RISK_COMPONENTS:
        item = (
            RiskComponent.query
            .filter(
                db.func.lower(
                    RiskComponent.name
                ) == name.lower()
            )
            .first()
        )

        if item is not None:
            existing += 1
            continue

        db.session.add(
            RiskComponent(
                name=name,
                category=category,
                description=description,
                active=True,
            )
        )

        created += 1

    db.session.commit()

    print(
        f"Rizikófaktorok: "
        f"{created} új, "
        f"{existing} már létezett."
    )


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        seed()
