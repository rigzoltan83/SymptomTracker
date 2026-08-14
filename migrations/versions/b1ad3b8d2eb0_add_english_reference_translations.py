"""Add English reference translations

Revision ID: b1ad3b8d2eb0
Revises: c40bb29dbad8
Create Date: 2026-08-14 07:49:14.923554
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "b1ad3b8d2eb0"
down_revision = "c40bb29dbad8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO symptom_type_translations (
            symptom_type_id,
            language_code,
            name
        )
        SELECT
            source.id,
            'en',
            translations.en_name
        FROM symptom_types AS source
        JOIN (
            VALUES
                ('Viszketés', 'Itching'),
                ('Kiütés', 'Rash'),
                ('Hányás', 'Vomiting')
        ) AS translations(
            hu_name,
            en_name
        )
            ON source.name = translations.hu_name
        ON CONFLICT (
            symptom_type_id,
            language_code
        )
        DO UPDATE SET
            name = EXCLUDED.name
        """
    )

    op.execute(
        """
        INSERT INTO body_part_translations (
            body_part_id,
            language_code,
            name
        )
        SELECT
            source.id,
            'en',
            translations.en_name
        FROM body_parts AS source
        JOIN (
            VALUES
                ('Fej', 'Head'),
                ('Arc', 'Face'),
                ('Nyak', 'Neck'),
                ('Mellkas', 'Chest'),
                ('Has', 'Abdomen'),
                ('Hát', 'Back'),
                ('Bal váll', 'Left shoulder'),
                ('Jobb váll', 'Right shoulder'),
                ('Bal felkar', 'Left upper arm'),
                ('Jobb felkar', 'Right upper arm'),
                ('Bal alkar', 'Left forearm'),
                ('Jobb alkar', 'Right forearm'),
                ('Bal kéz', 'Left hand'),
                ('Jobb kéz', 'Right hand'),
                ('Bal comb', 'Left thigh'),
                ('Jobb comb', 'Right thigh'),
                ('Bal lábszár', 'Left lower leg'),
                ('Jobb lábszár', 'Right lower leg'),
                ('Bal lábfej', 'Left foot'),
                ('Jobb lábfej', 'Right foot'),
                ('Fül', 'Ear'),
                ('Mell', 'Breast')
        ) AS translations(
            hu_name,
            en_name
        )
            ON source.name = translations.hu_name
        ON CONFLICT (
            body_part_id,
            language_code
        )
        DO UPDATE SET
            name = EXCLUDED.name
        """
    )

    op.execute(
        """
        INSERT INTO ingredient_translations (
            ingredient_id,
            language_code,
            name
        )
        SELECT
            source.id,
            'en',
            translations.en_name
        FROM ingredients AS source
        JOIN (
            VALUES
                ('liszt', 'flour'),
                ('paradicsom', 'tomato'),
                ('sonka', 'ham'),
                ('sajt', 'cheese'),
                ('tej', 'milk'),
                ('kávé', 'coffee'),
                ('fahéj', 'cinnamon'),
                ('Tojás', 'egg'),
                ('cukor', 'sugar'),
                ('Élesztő', 'yeast'),
                ('búza', 'wheat'),
                ('búzaliszt', 'wheat flour'),
                ('finomliszt', 'refined wheat flour'),
                (
                    'teljes kiőrlésű búzaliszt',
                    'whole wheat flour'
                ),
                ('durum', 'durum wheat'),
                ('durumliszt', 'durum flour'),
                ('búzadara', 'semolina'),
                ('gríz', 'semolina'),
                ('kuszkusz', 'couscous'),
                ('bulgur', 'bulgur'),
                ('tönkölybúza', 'spelt'),
                ('tönkölyliszt', 'spelt flour'),
                ('rozs', 'rye'),
                ('rozsliszt', 'rye flour'),
                ('árpa', 'barley'),
                ('zab', 'oats'),
                ('zabpehely', 'oat flakes'),
                ('búzakenyér', 'wheat bread'),
                (
                    'teljes kiőrlésű kenyér',
                    'whole grain bread'
                ),
                ('rozskenyér', 'rye bread'),
                ('búzatészta', 'wheat pasta'),
                ('durumtészta', 'durum wheat pasta'),
                ('tehéntej', 'cow''s milk'),
                ('kecsketej', 'goat''s milk'),
                ('juhtej', 'sheep''s milk'),
                ('tejpor', 'milk powder'),
                ('sovány tejpor', 'skimmed milk powder'),
                ('sűrített tej', 'condensed milk'),
                ('tejszín', 'cream'),
                ('főzőtejszín', 'cooking cream'),
                ('joghurt', 'yogurt'),
                ('görög joghurt', 'Greek yogurt'),
                ('kefir', 'kefir'),
                ('túró', 'curd cheese'),
                ('krémsajt', 'cream cheese'),
                ('mascarpone', 'mascarpone'),
                ('mozzarella', 'mozzarella'),
                ('feta', 'feta'),
                ('parmezán', 'Parmesan'),
                ('tejsavó', 'whey'),
                ('tejsavópor', 'whey powder'),
                ('fagylalt', 'ice cream'),
                ('vaj', 'butter'),
                ('tojásfehérje', 'egg white'),
                ('tojássárgája', 'egg yolk'),
                ('tojáspor', 'egg powder'),
                ('majonéz', 'mayonnaise'),
                ('szója', 'soy'),
                ('szójabab', 'soybean'),
                ('szójaliszt', 'soy flour'),
                ('szójafehérje', 'soy protein'),
                ('tofu', 'tofu'),
                ('szójaital', 'soy drink'),
                ('szójaszósz', 'soy sauce'),
                ('földimogyoró', 'peanut'),
                ('földimogyorókrém', 'peanut butter'),
                ('mandula', 'almond'),
                ('mogyoró', 'hazelnut'),
                ('dió', 'walnut'),
                ('kesudió', 'cashew'),
                ('pekándió', 'pecan'),
                ('brazil dió', 'Brazil nut'),
                ('pisztácia', 'pistachio'),
                ('makadámdió', 'macadamia nut'),
                ('vegyes diófélék', 'mixed nuts'),
                ('szezámmag', 'sesame seed'),
                ('tahini', 'tahini'),
                ('szezámolaj', 'sesame oil'),
                ('mustár', 'mustard'),
                ('mustármag', 'mustard seed'),
                ('mustárpor', 'mustard powder'),
                ('zeller', 'celery'),
                ('zellergumó', 'celeriac'),
                ('zellerszár', 'celery stalk'),
                ('csillagfürt', 'lupin'),
                ('csillagfürtliszt', 'lupin flour'),
                ('csicseriborsó', 'chickpea'),
                ('csicseriborsóliszt', 'chickpea flour'),
                ('lencse', 'lentils'),
                ('vöröslencse', 'red lentils'),
                ('bab', 'beans'),
                ('vörösbab', 'red kidney beans'),
                ('fehérbab', 'white beans'),
                ('tarkabab', 'pinto beans'),
                ('sárgaborsó', 'yellow split peas'),
                ('zöldborsó', 'green peas'),
                ('falafel', 'falafel'),
                ('sült bab', 'baked beans'),
                ('hagyma', 'onion'),
                ('vöröshagyma', 'yellow onion'),
                ('lilahagyma', 'red onion'),
                ('fokhagyma', 'garlic'),
                ('fokhagymapor', 'garlic powder'),
                ('hagymapor', 'onion powder'),
                ('póréhagyma', 'leek'),
                (
                    'újhagyma fehér része',
                    'white part of spring onion'
                ),
                ('articsóka', 'artichoke'),
                ('csicsóka', 'Jerusalem artichoke'),
                ('gomba', 'mushroom'),
                ('csiperke', 'button mushroom'),
                ('alma', 'apple'),
                ('körte', 'pear'),
                ('nashi körte', 'nashi pear'),
                ('mangó', 'mango'),
                ('cseresznye', 'cherry'),
                ('füge', 'fig'),
                ('görögdinnye', 'watermelon'),
                ('őszibarack', 'peach'),
                ('szilva', 'plum'),
                ('sárgabarack', 'apricot'),
                ('aszalt gyümölcs', 'dried fruit'),
                ('almalé', 'apple juice'),
                ('körtelé', 'pear juice'),
                (
                    'gyümölcslé-koncentrátum',
                    'fruit juice concentrate'
                ),
                ('méz', 'honey'),
                ('inulin', 'inulin'),
                ('FOS', 'FOS'),
                (
                    'frukto-oligoszacharid',
                    'fructo-oligosaccharide'
                ),
                ('GOS', 'GOS'),
                (
                    'galakto-oligoszacharid',
                    'galacto-oligosaccharide'
                ),
                ('fruktóz', 'fructose'),
                (
                    'glükóz-fruktóz szirup',
                    'glucose-fructose syrup'
                ),
                (
                    'magas fruktóztartalmú kukoricaszirup',
                    'high-fructose corn syrup'
                ),
                ('szorbit', 'sorbitol'),
                ('szorbitol', 'sorbitol'),
                ('E420', 'E420'),
                ('mannit', 'mannitol'),
                ('mannitol', 'mannitol'),
                ('E421', 'E421'),
                ('xilit', 'xylitol'),
                ('xilitol', 'xylitol'),
                ('E967', 'E967'),
                ('kén-dioxid', 'sulfur dioxide'),
                ('E220', 'E220'),
                ('nátrium-szulfit', 'sodium sulfite'),
                ('E221', 'E221'),
                (
                    'nátrium-hidrogén-szulfit',
                    'sodium hydrogen sulfite'
                ),
                ('E222', 'E222'),
                (
                    'nátrium-metabiszulfit',
                    'sodium metabisulfite'
                ),
                ('E223', 'E223'),
                (
                    'kálium-metabiszulfit',
                    'potassium metabisulfite'
                ),
                ('E224', 'E224'),
                ('kalcium-szulfit', 'calcium sulfite'),
                ('E226', 'E226'),
                (
                    'kalcium-hidrogén-szulfit',
                    'calcium hydrogen sulfite'
                ),
                ('E227', 'E227'),
                (
                    'kálium-hidrogén-szulfit',
                    'potassium hydrogen sulfite'
                ),
                ('E228', 'E228'),
                ('hal', 'fish'),
                ('lazac', 'salmon'),
                ('tonhal', 'tuna'),
                ('tőkehal', 'cod'),
                ('rák', 'crustacean'),
                ('garnéla', 'shrimp'),
                ('homár', 'lobster'),
                ('languszta', 'spiny lobster'),
                ('kagyló', 'mussel'),
                ('osztriga', 'oyster'),
                ('tintahal', 'squid'),
                ('polip', 'octopus'),
                ('éticsiga', 'edible snail'),
                ('zsemlemorzsa', 'breadcrumbs'),
                ('basmati rizs', 'basmati rice'),
                ('rizsliszt', 'rice flour'),
                ('só', 'salt'),
                ('kókuszzsír', 'coconut fat'),
                ('glükózszirup', 'glucose syrup'),
                ('kakaóvaj', 'cocoa butter'),
                ('kukoricakeményítő', 'corn starch'),
                ('tejcukor', 'lactose'),
                ('vajzsír', 'butterfat'),
                ('étolaj', 'cooking oil'),
                ('vajkrém', 'butter spread'),
                ('medvesajt', 'processed cheese'),
                ('sertészsír', 'lard'),
                ('füstölt sonka', 'smoked ham'),
                ('bors', 'pepper'),
                (
                    'őrölt pirospaprika',
                    'ground paprika'
                ),
                ('Málna', 'raspberry'),
                ('Ribizli', 'currant')
        ) AS translations(
            hu_name,
            en_name
        )
            ON source.name = translations.hu_name
        ON CONFLICT (
            ingredient_id,
            language_code
        )
        DO UPDATE SET
            name = EXCLUDED.name
        """
    )

    op.execute(
        """
        INSERT INTO risk_component_translations (
            risk_component_id,
            language_code,
            name,
            description
        )
        SELECT
            source.id,
            'en',
            translations.en_name,
            translations.en_description
        FROM risk_components AS source
        JOIN (
            VALUES
                (
                    'Glutén',
                    'Gluten',
                    'Component associated with gluten-containing cereals.'
                ),
                (
                    'Tejfehérje',
                    'Milk protein',
                    'Proteins originating from milk.'
                ),
                (
                    'Tojás',
                    'Egg',
                    'Allergen associated with egg.'
                ),
                (
                    'Szója',
                    'Soy',
                    'Allergen associated with soy.'
                ),
                (
                    'Földimogyoró',
                    'Peanut',
                    'Allergen associated with peanuts.'
                ),
                (
                    'Diófélék',
                    'Tree nuts',
                    'Allergen group associated with tree nuts.'
                ),
                (
                    'Szezám',
                    'Sesame',
                    'Allergen associated with sesame seeds.'
                ),
                (
                    'Mustár',
                    'Mustard',
                    'Allergen associated with mustard.'
                ),
                (
                    'Zeller',
                    'Celery',
                    'Allergen associated with celery.'
                ),
                (
                    'Szulfit',
                    'Sulfites',
                    'Used to indicate sulfites and sulfur dioxide.'
                ),
                (
                    'Laktóz',
                    'Lactose',
                    'Milk sugar.'
                ),
                (
                    'Fruktóz',
                    'Fructose',
                    'Fruit sugar.'
                ),
                (
                    'Fruktán',
                    'Fructans',
                    'Fermentable carbohydrate of the fructan type.'
                ),
                (
                    'GOS',
                    'GOS',
                    'Galacto-oligosaccharides.'
                ),
                (
                    'Szorbit',
                    'Sorbitol',
                    'Polyol.'
                ),
                (
                    'Mannit',
                    'Mannitol',
                    'Polyol.'
                ),
                (
                    'Xilit',
                    'Xylitol',
                    'Polyol.'
                ),
                (
                    'Hisztamin-kockázat',
                    'Histamine risk',
                    'Risk label associated with histamine.'
                ),
                (
                    'Rákfélék',
                    'Crustaceans',
                    'Allergen associated with crustaceans.'
                ),
                (
                    'Hal',
                    'Fish',
                    'Allergen associated with fish.'
                ),
                (
                    'Csillagfürt',
                    'Lupin',
                    'Allergen associated with lupin.'
                ),
                (
                    'Puhatestűek',
                    'Molluscs',
                    'Allergen associated with shellfish and other molluscs.'
                ),
                (
                    'Magas zsírtartalom',
                    'High fat content',
                    NULL
                ),
                (
                    'Koffein',
                    'Caffeine',
                    NULL
                ),
                (
                    'Csípős / irritáló fűszer',
                    'Spicy / irritating seasoning',
                    NULL
                ),
                (
                    'Savas étel',
                    'Acidic food',
                    NULL
                ),
                (
                    'Feldolgozott / füstölt hús',
                    'Processed / smoked meat',
                    NULL
                )
        ) AS translations(
            hu_name,
            en_name,
            en_description
        )
            ON source.name = translations.hu_name
        ON CONFLICT (
            risk_component_id,
            language_code
        )
        DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM ingredient_translations
        WHERE language_code = 'en'
        """
    )

    op.execute(
        """
        DELETE FROM symptom_type_translations
        WHERE language_code = 'en'
        """
    )

    op.execute(
        """
        DELETE FROM body_part_translations
        WHERE language_code = 'en'
        """
    )

    op.execute(
        """
        DELETE FROM risk_component_translations
        WHERE language_code = 'en'
        """
    )
