# Copyright 2022 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Kmee Nfe Delivery',
    'description': """
        Adiciona campos para dados do transportador ao picking e o propaga ate a nfe""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE',
    'website': 'kmee.com.br',
    'depends': [
        'l10n_br_fiscal',
        'l10n_br_nfe',
        'l10n_br_sale',
        'l10n_br_stock_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking.xml',
        'views/res_partner.xml',
        'views/document.xml',
        'views/volume.xml',
        'views/sale_order.xml',
    ],
    'demo': [
    ],
}
