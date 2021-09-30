# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from urllib.parse import quote
import decimal

from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_replace = fields.Selection(
        string='Estratégia de Substituição',
        selection=[('estorna', 'Estornar Compra'),
                   ('estorna_variacao', 'Estornar Variação'),
                   ('aceita', 'Aceitar Variação')],
        required=True,
        default='estorna',
    )


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    product_replace = fields.Selection(
        string='Estratégia de Substituição',
        selection=[('estorna', 'Estornar Compra'),
                   ('estorna_variacao', 'Estornar Variação'),
                   ('aceita', 'Aceitar Variação')],
        required=True,
        related='sale_id.product_replace',
    )
