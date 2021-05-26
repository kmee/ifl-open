# Copyright 2020 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_subtotal_cart(self, id):
        return self.price_subtotal


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_order_subtotal(self, id):
        return self.amount_price_gross
