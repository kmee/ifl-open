# Copyright 2023 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Kmee Pos Scrap",
    "description": """
        This model facilitates scrapping products from POS.""",
    "version": "12.0.0.0.0",
    "license": "AGPL-3",
    "author": "KMEE INFORMATICA LTDA",
    "website": "kmee.com.br",
    "depends": ["point_of_sale"],
    "data": ["views/pos_scrap_templates.xml"],
    "qweb": [
        "static/src/xml/scrap.xml",
    ],
    "installable": True,
    "demo": [],
}
