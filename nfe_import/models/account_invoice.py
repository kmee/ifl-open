# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def create(self, values):
        purchase_id = values.get("purchase_id")
        if purchase_id:
            purchase = self.env['purchase.order'].browse(purchase_id)
            if purchase and purchase.imported_nfe_id:
                values.update(
                    {"fiscal_document_id": purchase.imported_nfe_id.id}
                )
        invoice = super().create(values)
        return invoice
