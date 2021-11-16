from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    can_sell = fields.Boolean()


class ProductTemplateAttributeValue(models.Model):
    """Inherit product template attribute value and make price extra
    computed"""

    _inherit = "product.template.attribute.value"

    can_sell = fields.Boolean(
        store=True,
    )
