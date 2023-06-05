import copy

from odoo import api, fields, models


class DocumentWorkflow(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.workflow"

    def action_document_confirm(self):
        for record in self:
            if record.partner_id:
                record.partner_id.zip_search()

            pag_line = self.env["nfe.40.detpag"].search(
                [("nfe40_detPag_pag_id", "=", record.id)]
            )
            if not pag_line:
                invoice_id = self.env["account.invoice"].search(
                    [("fiscal_document_id", "=", record.id)]
                )
                line = self.env["nfe.40.detpag"].create(
                    {
                        "nfe40_indPag": "0",
                        "nfe40_tPag": "03",
                        "nfe40_vPag": invoice_id.amount_total,
                        "nfe40_detPag_pag_id": record.id,
                    }
                )

        res = super().action_document_confirm()
