import copy

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def enable_card_token(self):
        self.picking_ids.sale_id.enable_payment_token()

    def action_invoice_open(self):
        for line in self.invoice_line_ids:
            if line.product_id and not line.product_id.default_code:
                raise ValidationError(_('O produto %s não tem Referência Interna. Conserte-o antes de continuar.' % line.product_id.name))

        return super(AccountInvoice, self).action_invoice_open()

