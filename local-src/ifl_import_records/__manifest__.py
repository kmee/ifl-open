# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Import Products',
    'description': """
        Import Products""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE',
    'website': 'www.kmee.com.br',
    'depends': [
        'l10n_br_fiscal',
        'queue_job',
        'sale',
    ],
    'data': [
        'wizards/import_remote_products.xml',
        'views/product_template.xml',
        'views/res_config_settings_view.xml',
    ],
    'demo': [
    ],
}
