
from odoo import api, fields, models


class DocumentLine(models.Model):
    _inherit = 'l10n_br_fiscal.document.line'

    def write(self, values):
        # don't write to document line if product is donation
        if not values.get('product_id'):
            return super(DocumentLine, self).write(values)
        if not self.env['product.product'].browse(
                values['product_id']).donation:
            return super(DocumentLine, self).write(values)
