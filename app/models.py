from datetime import datetime, timezone

from app import db


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    # medication / food / symptom
    event_type = db.Column(
        db.String(20),
        nullable=False,
        index=True,
    )

    occurred_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    notes = db.Column(
        db.Text,
        nullable=True,
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=db.true(),
        index=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    medication_event = db.relationship(
        "MedicationEvent",
        back_populates="event",
        uselist=False,
        cascade="all, delete-orphan",
    )

    food_event = db.relationship(
        "FoodEvent",
        back_populates="event",
        uselist=False,
        cascade="all, delete-orphan",
    )

    symptom_event = db.relationship(
        "SymptomEvent",
        back_populates="event",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Medication(db.Model):
    __tablename__ = "medications"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(200),
        nullable=False,
        unique=True,
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    is_default = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=db.false(),
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.Index(
            "uq_medications_one_default",
            "is_default",
            unique=True,
            postgresql_where=db.text(
                "is_default = true"
            ),
        ),
    )


class MedicationEvent(db.Model):
    __tablename__ = "medication_events"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "events.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    medication_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "medications.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    dose = db.Column(
        db.String(100),
        nullable=True,
    )

    event = db.relationship(
        "Event",
        back_populates="medication_event",
    )

    medication = db.relationship(
        "Medication",
    )


class Food(db.Model):
    __tablename__ = "foods"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(250),
        nullable=False,
        index=True,
    )

    brand = db.Column(
        db.String(200),
        nullable=True,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    ingredients = db.relationship(
        "FoodIngredient",
        back_populates="food",
        cascade="all, delete-orphan",
        order_by="FoodIngredient.position",
    )

    images = db.relationship(
        "FoodImage",
        back_populates="food",
        cascade="all, delete-orphan",
    )


    risk_components = db.relationship(
        "FoodRiskComponent",
        back_populates="food",
        cascade="all, delete-orphan",
    )


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(250),
        nullable=False,
        unique=True,
        index=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    risk_components = db.relationship(
        "IngredientRiskComponent",
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )


class RiskComponent(db.Model):
    __tablename__ = "risk_components"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(200),
        nullable=False,
        unique=True,
        index=True,
    )

    category = db.Column(
        db.String(50),
        nullable=False,
        index=True,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=db.true(),
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    ingredients = db.relationship(
        "IngredientRiskComponent",
        back_populates="risk_component",
        cascade="all, delete-orphan",
    )

    foods = db.relationship(
        "FoodRiskComponent",
        back_populates="risk_component",
        cascade="all, delete-orphan",
    )


class IngredientRiskComponent(db.Model):
    __tablename__ = "ingredient_risk_components"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "ingredients.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    risk_component_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "risk_components.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    confidence = db.Column(
        db.String(30),
        nullable=False,
        default="certain",
        server_default="certain",
    )

    notes = db.Column(
        db.Text,
        nullable=True,
    )

    ingredient = db.relationship(
        "Ingredient",
        back_populates="risk_components",
    )

    risk_component = db.relationship(
        "RiskComponent",
        back_populates="ingredients",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "ingredient_id",
            "risk_component_id",
            name="uq_ingredient_risk_component",
        ),
        db.CheckConstraint(
            "confidence IN "
            "('certain', 'typical', 'product_dependent')",
            name="ck_ingredient_risk_confidence",
        ),
    )


class FoodRiskComponent(db.Model):
    __tablename__ = "food_risk_components"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    food_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "foods.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    risk_component_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "risk_components.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    source = db.Column(
        db.String(20),
        nullable=False,
        default="automatic",
        server_default="automatic",
    )

    source = db.Column(
        db.String(20),
        nullable=False,
        default="automatic",
        server_default="automatic",
    )

    enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=db.true(),
    )

    notes = db.Column(
        db.Text,
        nullable=True,
    )

    notes = db.Column(
        db.Text,
        nullable=True,
    )

    food = db.relationship(
        "Food",
        back_populates="risk_components",
    )

    risk_component = db.relationship(
        "RiskComponent",
        back_populates="foods",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "food_id",
            "risk_component_id",
            name="uq_food_risk_component",
        ),
        db.CheckConstraint(
            "source IN ('automatic', 'manual')",
            name="ck_food_risk_source",
        ),
    )


class FoodIngredient(db.Model):
    __tablename__ = "food_ingredients"

    id = db.Column(db.Integer, primary_key=True)

    food_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "foods.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "ingredients.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    position = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    notes = db.Column(
        db.String(250),
        nullable=True,
    )

    food = db.relationship(
        "Food",
        back_populates="ingredients",
    )

    ingredient = db.relationship(
        "Ingredient",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "food_id",
            "ingredient_id",
            name="uq_food_ingredient",
        ),
    )


class FoodImage(db.Model):
    __tablename__ = "food_images"

    id = db.Column(db.Integer, primary_key=True)

    food_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "foods.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    filename = db.Column(
        db.String(500),
        nullable=False,
    )

    image_type = db.Column(
        db.String(50),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    food = db.relationship(
        "Food",
        back_populates="images",
    )


class FoodEvent(db.Model):
    __tablename__ = "food_events"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "events.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    food_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "foods.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    amount = db.Column(
        db.String(100),
        nullable=True,
    )

    event = db.relationship(
        "Event",
        back_populates="food_event",
    )

    food = db.relationship(
        "Food",
    )


class SymptomType(db.Model):
    __tablename__ = "symptom_types"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(200),
        nullable=False,
        unique=True,
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )


class BodyPart(db.Model):
    __tablename__ = "body_parts"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(200),
        nullable=False,
        unique=True,
    )

    active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )


symptom_event_body_parts = db.Table(
    "symptom_event_body_parts",

    db.Column(
        "symptom_event_id",
        db.Integer,
        db.ForeignKey(
            "symptom_events.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),

    db.Column(
        "body_part_id",
        db.Integer,
        db.ForeignKey(
            "body_parts.id",
            ondelete="RESTRICT",
        ),
        primary_key=True,
    ),
)


class SymptomImage(db.Model):
    __tablename__ = "symptom_images"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    symptom_event_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "symptom_events.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    filename = db.Column(
        db.String(500),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    symptom_event = db.relationship(
        "SymptomEvent",
        back_populates="images",
    )


class SymptomEvent(db.Model):
    __tablename__ = "symptom_events"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "events.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    symptom_type_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "symptom_types.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    severity = db.Column(
        db.Integer,
        nullable=True,
    )

    ended_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    event = db.relationship(
        "Event",
        back_populates="symptom_event",
    )

    symptom_type = db.relationship(
        "SymptomType",
    )

    body_parts = db.relationship(
        "BodyPart",
        secondary=symptom_event_body_parts,
    )

    images = db.relationship(
        "SymptomImage",
        back_populates="symptom_event",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.CheckConstraint(
            "severity IS NULL OR "
            "(severity >= 0 AND severity <= 10)",
            name="ck_symptom_severity_0_10",
        ),
    )
