# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    # @api.model
    # def create(self, values):
    #     dummy_doc = self.env.user.company_id._default_fiscal_dummy_id()
    #     invoice = self.env["account.invoice"].browse(values["invoice_id"])
    #     if invoice.purchase_id and invoice.purchase_id.imported_nfe_id:
    #         original_fiscal_doc_id = invoice.fiscal_document_id.id
    #         invoice.fiscal_document_id = dummy_doc
    #         line = super().create(values)
    #         invoice.fiscal_document_id = original_fiscal_doc_id
    #     else:
    #         line = super().create(values)
    #     return line
