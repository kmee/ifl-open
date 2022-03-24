# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    imported_nfe_id = fields.One2many(
        comodel_name='l10n_br_fiscal.document',
        inverse_name='purchase_id',
        string='NFe Importada',
        required=False,
        default=False,
    )

    entry_type = fields.Selection(
        string='Tipo de Recebimento',
        selection=[('automatico', 'Automático'),
                   ('semi_automatico', 'Semi Automático'),
                   ('manual', 'Manual'),
                   ],
        required=False,
        default=False,
    )

    def action_open_nfe(self):
        result = self.env.ref('nfe_import.action_document').read()[0]
        result['context'] = {}
        res = self.env.ref('l10n_br_fiscal.document_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.imported_nfe_id.id
        return result

    def action_open_import_document(self):
        result = self.env.ref('l10n_br_nfe.l10n_br_nfe_import_xml_action').read()[0]
        result['context'] = {'default_purchase_id': self.id}
        res = self.env.ref('l10n_br_nfe.l10n_br_nfe_import_xml_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        return result

    @api.multi
    def action_open_link_po_nfe(self):
        self.ensure_one()
        result = self.env.ref('nfe_import.act_link_nfe_po').read()[0]
        result['context'] = {'default_origin_model': 'purchase', 'default_linked': False}
        return result

    @api.multi
    def action_open_choose_entry_type(self):
        self.ensure_one()
        result = self.env.ref('nfe_import.act_link_nfe_po').read()[0]
        result['context'] = {'default_origin_model': 'purchase', 'default_linked': True, 'default_purchase_id': self.id, 'default_nfe_id': self.imported_nfe_id.id}
        return result

    def button_unlink_po_nfe(self):
        if self.picking_ids:
            for picking in self.picking_ids:
                if picking.state == 'done':
                    raise UserError(_('Impossível desconciliar documentos após conclusão da transferência.'))
        self.imported_nfe_id = False

    @api.multi
    def _add_supplier_to_product(self):
        res = super(PurchaseOrder, self)._add_supplier_to_product()
        for line in self.order_line:
            product_id = line.product_id
            supplierinfo = product_id.seller_ids.filtered(lambda s: s.name == self.partner_id)[0]
            if supplierinfo and not supplierinfo.product_id:
                product_id.write({'seller_ids': [(1, supplierinfo.id, {'product_id': product_id.id})]})
        return res
