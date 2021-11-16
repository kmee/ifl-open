from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    can_sell = fields.Boolean(string="Disponível no site?")

    def scheduled_set_can_sell(self, enable=True):
        for record in self:
            tmpl_id = record.product_tmpl_id
            record.can_sell = enable
            
            product_template_attribute_value_ids = self.env['product.template.attribute.value'].search([
                ('product_tmpl_id', '=', tmpl_id.id),
                ('product_attribute_value_id', 'in', record.attribute_value_ids.ids),
            ])
            product_template_attribute_value_ids.write({'can_sell': enable})


class ProductTemplateAttributeValue(models.Model):
    """Inherit product template attribute value and make price extra
    computed"""

    _inherit = "product.template.attribute.value"

    can_sell = fields.Boolean(
        store=True,
    )
