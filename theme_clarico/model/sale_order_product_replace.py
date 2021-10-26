# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ReplaceStrategy(models.Model):
    _name = 'product.replace.strategy'

    name = fields.Char(
        string='Estratégia de Substituição',
        required=True,
    )
    
    description = fields.Text(
        string="Description",
        required=False,
    )


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_replace_id = fields.Many2one(
        comodel_name='product.replace.strategy',
        string='Estratégia de Substituição',
        default=lambda self: self.env.ref('theme_clarico.product_replace_strategy_1').id,
        required=True,
    )

    replace_obs_text = fields.Text(
        string="Observação",
        required=False,
    )

    donation_percentage = fields.Float(
        string="Percentual de Contribuição",
        required=False,
        default=35,
    )

    def _strategy_update(self, id):
        self.write({
            'product_replace_id': id,
        })

    def _strategy_obs_update(self, obs="obs"):
        self.write({
            'replace_obs_text': obs,
        })

    def _donation_percentage_update(self, percentage):
        self.write({
            'donation_percentage': percentage,
        })
