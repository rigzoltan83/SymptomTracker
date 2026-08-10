import argparse

from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import (
    Ingredient,
    IngredientRiskComponent,
    RiskComponent,
)


RISK_COMPONENTS = {
    # EU allergén / allergiás szempont
    "Glutén": (
        "allergen",
        "Glutént tartalmazó gabonákhoz kapcsolódó faktor.",
    ),
    "Tejfehérje": (
        "allergen",
        "Tejből és tejtermékből származó fehérjék.",
    ),
    "Tojás": (
        "allergen",
        "Tojáshoz kapcsolódó allergén.",
    ),
    "Szója": (
        "allergen",
        "Szójához kapcsolódó allergén.",
    ),
    "Földimogyoró": (
        "allergen",
        "Földimogyoróhoz kapcsolódó allergén.",
    ),
    "Diófélék": (
        "allergen",
        "Mandula, mogyoró, dió, kesudió, pekándió, "
        "brazil dió, pisztácia és makadámdió.",
    ),
    "Szezám": (
        "allergen",
        "Szezámmaghoz kapcsolódó allergén.",
    ),
    "Mustár": (
        "allergen",
        "Mustárhoz kapcsolódó allergén.",
    ),
    "Zeller": (
        "allergen",
        "Zellerhez kapcsolódó allergén.",
    ),
    "Szulfit": (
        "allergen",
        "Kén-dioxid és szulfitok jelölésére.",
    ),
    "Rákfélék": (
        "allergen",
        "Rákfélékhez kapcsolódó allergén.",
    ),
    "Hal": (
        "allergen",
        "Halhoz kapcsolódó allergén.",
    ),
    "Csillagfürt": (
        "allergen",
        "Csillagfürthöz kapcsolódó allergén.",
    ),
    "Puhatestűek": (
        "allergen",
        "Kagylókhoz és más puhatestűekhez "
        "kapcsolódó allergén.",
    ),

    # FODMAP
    "Laktóz": (
        "fodmap",
        "Tejcukor; FODMAP diszacharid.",
    ),
    "Fruktóz": (
        "fodmap",
        "FODMAP szempontból elsősorban a "
        "glükózhoz képest feleslegben levő fruktóz.",
    ),
    "Fruktán": (
        "fodmap",
        "Fruktán típusú fermentálható "
        "oligoszacharid.",
    ),
    "GOS": (
        "fodmap",
        "Galakto-oligoszacharidok.",
    ),
    "Szorbit": (
        "fodmap",
        "Szorbitol típusú poliol.",
    ),
    "Mannit": (
        "fodmap",
        "Mannitol típusú poliol.",
    ),
    "Xilit": (
        "fodmap",
        "Xilitol típusú poliol.",
    ),

    # Külön, automatikusan NEM seedelt faktor
    "Hisztamin-kockázat": (
        "biogenic_amine",
        "Hisztaminnal kapcsolatos kockázati címke. "
        "Automatikus alapanyag-hozzárendelést a seed "
        "szándékosan nem végez.",
    ),
}


def r(name, confidence="certain"):
    return (name, confidence)


INGREDIENT_KNOWLEDGE = {
    # ---------------------------------------------------------
    # GABONÁK / GLUTÉN / FRUKTÁN
    # ---------------------------------------------------------

    "búza": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "búzaliszt": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "liszt": [
        r("Glutén", "product_dependent"),
        r("Fruktán", "product_dependent"),
    ],
    "finomliszt": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "teljes kiőrlésű búzaliszt": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "durum": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "durumliszt": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "búzadara": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "gríz": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "kuszkusz": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "bulgur": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "tönkölybúza": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "tönkölyliszt": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "rozs": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "rozsliszt": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "árpa": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "zab": [
        r("Glutén"),
    ],
    "zabpehely": [
        r("Glutén"),
    ],
    "búzakenyér": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "teljes kiőrlésű kenyér": [
        r("Glutén", "product_dependent"),
        r("Fruktán", "typical"),
    ],
    "rozskenyér": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "búzatészta": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],
    "durumtészta": [
        r("Glutén"),
        r("Fruktán", "typical"),
    ],

    # ---------------------------------------------------------
    # TEJ / TEJTERMÉK
    # ---------------------------------------------------------

    "tej": [
        r("Tejfehérje"),
        r("Laktóz"),
    ],
    "tehéntej": [
        r("Tejfehérje"),
        r("Laktóz"),
    ],
    "kecsketej": [
        r("Tejfehérje"),
        r("Laktóz"),
    ],
    "juhtej": [
        r("Tejfehérje"),
        r("Laktóz"),
    ],
    "tejpor": [
        r("Tejfehérje"),
        r("Laktóz"),
    ],
    "sovány tejpor": [
        r("Tejfehérje"),
        r("Laktóz"),
    ],
    "sűrített tej": [
        r("Tejfehérje"),
        r("Laktóz"),
    ],
    "tejszín": [
        r("Tejfehérje"),
        r("Laktóz", "typical"),
    ],
    "főzőtejszín": [
        r("Tejfehérje"),
        r("Laktóz", "typical"),
    ],
    "joghurt": [
        r("Tejfehérje"),
        r("Laktóz", "typical"),
    ],
    "görög joghurt": [
        r("Tejfehérje"),
        r("Laktóz", "typical"),
    ],
    "kefir": [
        r("Tejfehérje"),
        r("Laktóz", "typical"),
    ],
    "túró": [
        r("Tejfehérje"),
        r("Laktóz", "typical"),
    ],
    "krémsajt": [
        r("Tejfehérje"),
        r("Laktóz", "product_dependent"),
    ],
    "mascarpone": [
        r("Tejfehérje"),
        r("Laktóz", "product_dependent"),
    ],
    "mozzarella": [
        r("Tejfehérje"),
        r("Laktóz", "product_dependent"),
    ],
    "feta": [
        r("Tejfehérje"),
        r("Laktóz", "product_dependent"),
    ],
    "parmezán": [
        r("Tejfehérje"),
    ],
    "sajt": [
        r("Tejfehérje"),
        r("Laktóz", "product_dependent"),
    ],
    "tejsavó": [
        r("Tejfehérje"),
        r("Laktóz", "typical"),
    ],
    "tejsavópor": [
        r("Tejfehérje"),
        r("Laktóz", "typical"),
    ],
    "fagylalt": [
        r("Tejfehérje", "product_dependent"),
        r("Laktóz", "product_dependent"),
    ],
    "vaj": [
        r("Tejfehérje", "product_dependent"),
        r("Laktóz", "product_dependent"),
    ],

    # ---------------------------------------------------------
    # TOJÁS
    # ---------------------------------------------------------

    "tojás": [
        r("Tojás"),
    ],
    "tojásfehérje": [
        r("Tojás"),
    ],
    "tojássárgája": [
        r("Tojás"),
    ],
    "tojáspor": [
        r("Tojás"),
    ],
    "majonéz": [
        r("Tojás", "product_dependent"),
    ],

    # ---------------------------------------------------------
    # SZÓJA
    # ---------------------------------------------------------

    "szója": [
        r("Szója"),
        r("GOS", "typical"),
    ],
    "szójabab": [
        r("Szója"),
        r("GOS", "typical"),
    ],
    "szójaliszt": [
        r("Szója"),
        r("GOS", "typical"),
    ],
    "szójafehérje": [
        r("Szója"),
    ],
    "tofu": [
        r("Szója"),
    ],
    "szójaital": [
        r("Szója"),
        r("GOS", "product_dependent"),
    ],
    "szójaszósz": [
        r("Szója"),
        r("Glutén", "product_dependent"),
    ],

    # ---------------------------------------------------------
    # FÖLDIMOGYORÓ / DIÓFÉLÉK
    # ---------------------------------------------------------

    "földimogyoró": [
        r("Földimogyoró"),
    ],
    "földimogyorókrém": [
        r("Földimogyoró"),
    ],
    "mandula": [
        r("Diófélék"),
    ],
    "mogyoró": [
        r("Diófélék"),
    ],
    "dió": [
        r("Diófélék"),
    ],
    "kesudió": [
        r("Diófélék"),
        r("Fruktán", "typical"),
        r("GOS", "typical"),
    ],
    "pekándió": [
        r("Diófélék"),
    ],
    "brazil dió": [
        r("Diófélék"),
    ],
    "pisztácia": [
        r("Diófélék"),
    ],
    "makadámdió": [
        r("Diófélék"),
    ],
    "vegyes diófélék": [
        r("Diófélék"),
    ],

    # ---------------------------------------------------------
    # SZEZÁM / MUSTÁR / ZELLER / CSILLAGFÜRT
    # ---------------------------------------------------------

    "szezámmag": [
        r("Szezám"),
    ],
    "tahini": [
        r("Szezám"),
    ],
    "szezámolaj": [
        r("Szezám", "product_dependent"),
    ],
    "mustár": [
        r("Mustár"),
    ],
    "mustármag": [
        r("Mustár"),
    ],
    "mustárpor": [
        r("Mustár"),
    ],
    "zeller": [
        r("Zeller"),
        r("Mannit", "typical"),
    ],
    "zellergumó": [
        r("Zeller"),
        r("Mannit", "typical"),
    ],
    "zellerszár": [
        r("Zeller"),
        r("Mannit", "typical"),
    ],
    "csillagfürt": [
        r("Csillagfürt"),
    ],
    "csillagfürtliszt": [
        r("Csillagfürt"),
    ],

    # ---------------------------------------------------------
    # HÜVELYESEK / GOS
    # ---------------------------------------------------------

    "csicseriborsó": [
        r("GOS", "typical"),
    ],
    "csicseriborsóliszt": [
        r("GOS", "typical"),
    ],
    "lencse": [
        r("GOS", "typical"),
    ],
    "vöröslencse": [
        r("GOS", "typical"),
    ],
    "bab": [
        r("GOS", "typical"),
    ],
    "vörösbab": [
        r("GOS", "typical"),
    ],
    "fehérbab": [
        r("GOS", "typical"),
    ],
    "tarkabab": [
        r("GOS", "typical"),
    ],
    "sárgaborsó": [
        r("GOS", "typical"),
    ],
    "zöldborsó": [
        r("GOS", "typical"),
    ],
    "falafel": [
        r("GOS", "product_dependent"),
    ],
    "sült bab": [
        r("GOS", "typical"),
    ],

    # ---------------------------------------------------------
    # FRUKTÁN - ZÖLDSÉGEK
    # ---------------------------------------------------------

    "hagyma": [
        r("Fruktán"),
    ],
    "vöröshagyma": [
        r("Fruktán"),
    ],
    "lilahagyma": [
        r("Fruktán"),
    ],
    "fokhagyma": [
        r("Fruktán"),
    ],
    "fokhagymapor": [
        r("Fruktán"),
    ],
    "hagymapor": [
        r("Fruktán"),
    ],
    "póréhagyma": [
        r("Fruktán", "typical"),
    ],
    "újhagyma fehér része": [
        r("Fruktán", "typical"),
    ],
    "articsóka": [
        r("Fruktán", "typical"),
    ],
    "csicsóka": [
        r("Fruktán", "typical"),
    ],

    # ---------------------------------------------------------
    # MANNIT
    # ---------------------------------------------------------

    "gomba": [
        r("Mannit", "typical"),
    ],
    "csiperke": [
        r("Mannit", "typical"),
    ],

    # ---------------------------------------------------------
    # GYÜMÖLCSÖK
    # ---------------------------------------------------------

    "alma": [
        r("Fruktóz", "typical"),
        r("Szorbit", "typical"),
    ],
    "körte": [
        r("Fruktóz", "typical"),
        r("Szorbit", "typical"),
    ],
    "nashi körte": [
        r("Fruktóz", "typical"),
        r("Szorbit", "typical"),
    ],
    "mangó": [
        r("Fruktóz", "typical"),
    ],
    "cseresznye": [
        r("Fruktóz", "typical"),
        r("Szorbit", "typical"),
    ],
    "füge": [
        r("Fruktóz", "typical"),
    ],
    "görögdinnye": [
        r("Fruktóz", "typical"),
    ],
    "őszibarack": [
        r("Szorbit", "typical"),
    ],
    "szilva": [
        r("Szorbit", "typical"),
    ],
    "sárgabarack": [
        r("Szorbit", "typical"),
    ],
    "aszalt gyümölcs": [
        r("Fruktóz", "typical"),
        r("Szorbit", "product_dependent"),
    ],
    "almalé": [
        r("Fruktóz", "typical"),
        r("Szorbit", "typical"),
    ],
    "körtelé": [
        r("Fruktóz", "typical"),
        r("Szorbit", "typical"),
    ],
    "gyümölcslé-koncentrátum": [
        r("Fruktóz", "product_dependent"),
    ],
    "méz": [
        r("Fruktóz", "typical"),
    ],

    # ---------------------------------------------------------
    # FODMAP ADALÉKOK / ÉDESÍTŐK
    # ---------------------------------------------------------

    "inulin": [
        r("Fruktán"),
    ],
    "FOS": [
        r("Fruktán"),
    ],
    "frukto-oligoszacharid": [
        r("Fruktán"),
    ],
    "GOS": [
        r("GOS"),
    ],
    "galakto-oligoszacharid": [
        r("GOS"),
    ],
    "fruktóz": [
        r("Fruktóz"),
    ],
    "glükóz-fruktóz szirup": [
        r("Fruktóz", "product_dependent"),
    ],
    "magas fruktóztartalmú kukoricaszirup": [
        r("Fruktóz", "typical"),
    ],
    "szorbit": [
        r("Szorbit"),
    ],
    "szorbitol": [
        r("Szorbit"),
    ],
    "E420": [
        r("Szorbit"),
    ],
    "mannit": [
        r("Mannit"),
    ],
    "mannitol": [
        r("Mannit"),
    ],
    "E421": [
        r("Mannit"),
    ],
    "xilit": [
        r("Xilit"),
    ],
    "xilitol": [
        r("Xilit"),
    ],
    "E967": [
        r("Xilit"),
    ],

    # ---------------------------------------------------------
    # SZULFIT - CSAK EXPLICIT ADALÉKANYAGNEVEK
    # ---------------------------------------------------------

    "kén-dioxid": [
        r("Szulfit"),
    ],
    "E220": [
        r("Szulfit"),
    ],
    "nátrium-szulfit": [
        r("Szulfit"),
    ],
    "E221": [
        r("Szulfit"),
    ],
    "nátrium-hidrogén-szulfit": [
        r("Szulfit"),
    ],
    "E222": [
        r("Szulfit"),
    ],
    "nátrium-metabiszulfit": [
        r("Szulfit"),
    ],
    "E223": [
        r("Szulfit"),
    ],
    "kálium-metabiszulfit": [
        r("Szulfit"),
    ],
    "E224": [
        r("Szulfit"),
    ],
    "kalcium-szulfit": [
        r("Szulfit"),
    ],
    "E226": [
        r("Szulfit"),
    ],
    "kalcium-hidrogén-szulfit": [
        r("Szulfit"),
    ],
    "E227": [
        r("Szulfit"),
    ],
    "kálium-hidrogén-szulfit": [
        r("Szulfit"),
    ],
    "E228": [
        r("Szulfit"),
    ],

    # ---------------------------------------------------------
    # HAL
    # ---------------------------------------------------------

    "hal": [
        r("Hal"),
    ],
    "lazac": [
        r("Hal"),
    ],
    "tonhal": [
        r("Hal"),
    ],
    "tőkehal": [
        r("Hal"),
    ],

    # ---------------------------------------------------------
    # RÁKFÉLÉK
    # ---------------------------------------------------------

    "rák": [
        r("Rákfélék"),
    ],
    "garnéla": [
        r("Rákfélék"),
    ],
    "homár": [
        r("Rákfélék"),
    ],
    "languszta": [
        r("Rákfélék"),
    ],

    # ---------------------------------------------------------
    # PUHATESTŰEK
    # ---------------------------------------------------------

    "kagyló": [
        r("Puhatestűek"),
    ],
    "osztriga": [
        r("Puhatestűek"),
    ],
    "tintahal": [
        r("Puhatestűek"),
    ],
    "polip": [
        r("Puhatestűek"),
    ],
    "éticsiga": [
        r("Puhatestűek"),
    ],
}


def normalize_name(value):
    return " ".join(
        str(value).strip().split()
    )


def find_risk_component(name):
    return (
        RiskComponent.query
        .filter(
            db.func.lower(
                RiskComponent.name
            ) == name.lower()
        )
        .first()
    )


def find_ingredient(name):
    normalized = normalize_name(name)

    return (
        Ingredient.query
        .filter(
            db.func.lower(
                Ingredient.name
            ) == normalized.lower()
        )
        .first()
    )


def ensure_risk_components(apply):
    created = 0
    updated = 0

    for name, (
        category,
        description,
    ) in RISK_COMPONENTS.items():

        item = find_risk_component(name)

        if item is None:
            print(
                f"[ÚJ RIZIKÓ] "
                f"{name} ({category})"
            )

            if apply:
                item = RiskComponent(
                    name=name,
                    category=category,
                    description=description,
                    active=True,
                )

                db.session.add(item)

            created += 1

            continue

        changes = []

        if item.category != category:
            changes.append(
                f"category: "
                f"{item.category} -> {category}"
            )

        if item.description != description:
            changes.append(
                "description eltér"
            )

        if changes:
            print(
                f"[MEGLÉVŐ RIZIKÓ MEGTARTVA] "
                f"{name}: "
                + ", ".join(changes)
            )

            updated += 1

    if apply:
        db.session.flush()

    return created, updated


def seed_ingredients(apply):
    ingredient_created = 0
    mapping_created = 0
    mapping_existing = 0

    for raw_name, mappings in (
        INGREDIENT_KNOWLEDGE.items()
    ):
        name = normalize_name(raw_name)

        ingredient = find_ingredient(
            name
        )

        if ingredient is None:
            print(
                f"[ÚJ ÖSSZETEVŐ] {name}"
            )

            if apply:
                ingredient = Ingredient(
                    name=name
                )

                db.session.add(
                    ingredient
                )

                db.session.flush()

            ingredient_created += 1

        for (
            risk_name,
            confidence,
        ) in mappings:

            risk = find_risk_component(
                risk_name
            )

            if risk is None:
                if (
                    not apply
                    and risk_name
                    in RISK_COMPONENTS
                ):
                    print(
                        f"[ÚJ KAPCSOLAT] "
                        f"{name} -> {risk_name} "
                        f"[{confidence}]"
                    )

                    mapping_created += 1
                    continue

                raise RuntimeError(
                    "Hiányzó rizikófaktor: "
                    f"{risk_name}"
                )

            if not apply and ingredient is None:
                print(
                    f"[ÚJ KAPCSOLAT] "
                    f"{name} -> {risk_name} "
                    f"[{confidence}]"
                )

                mapping_created += 1
                continue

            existing = (
                IngredientRiskComponent.query
                .filter_by(
                    ingredient_id=(
                        ingredient.id
                    ),
                    risk_component_id=(
                        risk.id
                    ),
                )
                .first()
            )

            if existing is not None:
                mapping_existing += 1

                # Meglévő kézi beállítást
                # SZÁNDÉKOSAN nem írunk felül.
                if (
                    existing.confidence
                    != confidence
                ):
                    print(
                        f"[MEGTARTVA] "
                        f"{name} -> {risk_name}: "
                        f"DB={existing.confidence}, "
                        f"seed={confidence}"
                    )

                continue

            print(
                f"[ÚJ KAPCSOLAT] "
                f"{name} -> {risk_name} "
                f"[{confidence}]"
            )

            if apply:
                db.session.add(
                    IngredientRiskComponent(
                        ingredient=ingredient,
                        risk_component=risk,
                        confidence=confidence,
                        notes=(
                            "Alap tudásbázisból "
                            "seedelt kapcsolat."
                        ),
                    )
                )

            mapping_created += 1

    return (
        ingredient_created,
        mapping_created,
        mapping_existing,
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "SymptomTracker összetevő-"
            "rizikófaktor tudásbázis seed"
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Tényleges adatbázis-módosítás. "
            "Enélkül csak előnézet."
        ),
    )

    args = parser.parse_args()

    app = create_app()

    with app.app_context():
        print()
        print(
            "SymptomTracker tudásbázis seed"
        )

        print(
            "MÓD: "
            + (
                "ÉLES ÍRÁS"
                if args.apply
                else "ELŐNÉZET"
            )
        )

        print()

        risk_created, risk_updated = (
            ensure_risk_components(
                args.apply
            )
        )

        (
            ingredient_created,
            mapping_created,
            mapping_existing,
        ) = seed_ingredients(
            args.apply
        )

        if args.apply:
            db.session.commit()
        else:
            db.session.rollback()

        print()
        print("----- ÖSSZESÍTÉS -----")

        print(
            f"Új rizikófaktor: "
            f"{risk_created}"
        )

        print(
            f"Frissítendő rizikófaktor: "
            f"{risk_updated}"
        )

        print(
            f"Új összetevő: "
            f"{ingredient_created}"
        )

        print(
            f"Új kapcsolat: "
            f"{mapping_created}"
        )

        print(
            f"Már létező kapcsolat: "
            f"{mapping_existing}"
        )

        print()

        if args.apply:
            print(
                "A módosítások elmentve."
            )
        else:
            print(
                "ELŐNÉZET VOLT, "
                "az adatbázis nem változott."
            )


if __name__ == "__main__":
    main()
