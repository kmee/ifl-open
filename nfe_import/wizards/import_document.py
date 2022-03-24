# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class NfeImport(models.TransientModel):
    """ Importar XML Nota Fiscal Eletrônica """

    _inherit = "l10n_br_nfe.import_xml"

    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        required=False,
        default=False,
    )

    def import_nfe_xml(self):
        res = super(NfeImport, self).import_nfe_xml()
        edoc = self.env["l10n_br_fiscal.document"].browse(res['res_id'])

        if self.purchase_id:
            purchase = self.purchase_id
            edoc.purchase_id = purchase

            if edoc.partner_id != purchase.partner_id:
                raise UserError(_("Os parceiros do Documento Fiscal e da Ordem de Compra não podem ser diferentes."))

            for edoc_line in edoc.line_ids:
                flag = False
                for purchase_line in purchase.order_line:
                    if edoc_line.product_id == purchase_line.product_id:
                        flag = True
                        continue
                if not flag:
                    raise UserError(_("Os produtos do Documento Fiscal e da Ordem de Compra não podem ser diferentes."))

        return res
