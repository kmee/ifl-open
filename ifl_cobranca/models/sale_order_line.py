from odoo import models


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = [_name, 'l10n_br_fiscal.document.line.mixin']

    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        result = self._prepare_br_fiscal_dict()
        if self.product_id and self.product_id.invoice_policy == 'delivery':
            result['fiscal_quantity'] = self.fiscal_qty_delivered
        if self.product_id.donation:
            result['fiscal_document_line_id'] = self.env.ref(
                'l10n_br_fiscal.fiscal_document_line_dummy').id
        result.update(super()._prepare_invoice_line(qty))
        return result
