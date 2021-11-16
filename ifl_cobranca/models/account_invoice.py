import logging

from odoo.exceptions import ValidationError

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def enable_card_token(self):
        self.picking_ids.sale_id.enable_payment_token()

    def action_invoice_open(self):
        for line in self.invoice_line_ids:
            if line.product_id and not line.product_id.default_code:
                raise ValidationError(_('O produto %s não tem Referência Interna. Conserte-o antes de continuar.' % line.product_id.name))

        return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def payment_action_capture(self):
        super(AccountInvoice, self).payment_action_capture()
        try:
            self.authorized_transaction_ids._post_process_after_done()
            self.env.cr.commit()
        except Exception as e:
            _logger.exception("Transaction post processing failed")
            self.env.cr.rollback()

