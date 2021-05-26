import copy

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def enable_card_token(self):
        self.picking_ids.sale_id.enable_payment_token()

