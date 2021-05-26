# Copyright 2020 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class ProductTemplateAttributeValue(models.Model):
    """Inherit product template attribute value and make price extra
    computed"""

    _inherit = "product.template.attribute.value"

    variant_price = fields.Float(
        string="Preço da Variante",
        required=False,
        default=0.0,
        digits=dp.get_precision('Product Price'),
        )

    @api.onchange('variant_price')
    def _onchange_variant_price(self):
        if 'active_id' in self.env.context:
            product_template = self.env.context['active_id']
            product_template_id = self.env['product.template'].browse(
                product_template)
            self.price_extra = self.variant_price - \
                product_template_id.list_price
