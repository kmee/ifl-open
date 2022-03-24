# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

import re


class Document(models.Model):

    _inherit = "l10n_br_fiscal.document"

    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
    )

    @api.multi
    def action_open_link_nfe_po(self):
        self.ensure_one()
        result = self.env.ref('nfe_import.act_link_nfe_po').read()[0]
        result['context'] = {'default_origin_model': 'document', 'default_linked': False}
        return result

    def button_unlink_po_nfe(self):
        purchase = self.purchase_id
        if purchase.picking_ids:
            for picking in purchase.picking_ids:
                if picking.state == 'done':
                    raise UserError(_('Impossível desconciliar documentos após conclusão da transferência.'))
        self.purchase_id = False
