# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ifl Cobranca',
    'description': """
        IFL Cobrança""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE',
    'website': 'kmee.com.br',
    'depends': [
        'sale',
        'stock',
        'sale_stock',
        'stock_picking_invoicing',
        'l10n_br_fiscal',
    ],
    'data': [
        'views/sale_order.xml',
        'wizard/wizard_product_replace.xml',
        'views/stock_picking_views.xml',
        'views/account_invoice.xml',
        'views/stock_move_views.xml',
        'wizard/sale_make_invoice_advance_views.xml',
        'templates/product_attribute.xml',
        'views/product_product_views.xml',
    ],
    'demo': [
    ],
}
