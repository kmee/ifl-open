# Copyright 2022 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Nfe Import',
    'summary': """
        This module lets you link an imported NFe with a Purchase Order.""",
    'version': '12.0.0.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'https://kmee.com.br/',
    'depends': [
        'l10n_br_purchase',
        'l10n_br_nfe',
        'l10n_br_stock_account',
        'stock_picking_invoicing',
        'spec_driven_model',
    ],
    'data': [
        'views/document.xml',
        'views/purchase_order_views.xml',
        'views/stock_picking_views.xml',
        'wizards/link_nfe_view.xml'
    ],
    'demo': [
    ],
}
