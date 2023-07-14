# Copyright 2023 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Kmee Barcode Gen",
    "description": """
        This addon provides custom barcode generation for products with internal reference.""",
    "version": "12.0.0.0.0",
    "license": "AGPL-3",
    "author": "KMEE INFORMATICA LTDA",
    "website": "kmee.com.br",
    "depends": [
        "product",
        "ifl_default_product_reference",
    ],
    "data": [
        "views/product_product.xml",
    ],
    "demo": [],
}
