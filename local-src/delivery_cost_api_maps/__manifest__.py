# Copyright 2020 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Delivery Cost Api Maps',
    'description': """
        This modules set a distance range for each delivery cost""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE INFORMATICA LTDA',
    'website': 'www.kmee.com.br',
    'depends': [
        'l10n_br_website_sale_delivery'
    ],
    'data': [
        'security/googlemaps_api_config.xml',
        'views/googlemaps_api_config.xml',
    ],
    'demo': [
    ],
    'installable': True
}
