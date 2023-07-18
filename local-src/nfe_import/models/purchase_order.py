# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    imported_nfe_ids = fields.Many2many(
        comodel_name='l10n_br_fiscal.document',
        relation='nfe_purchase_relation_1',
        column1='purchase_id',
        column2='document_id',
        string='NFes Importadas',
        required=False,
        default=False,
    )

    imported_document_count = fields.Integer(compute="_compute_imported_document_count")

    @api.multi
    def _compute_imported_document_count(self):
        for rec in self:
            rec.imported_document_count = len(rec.imported_nfe_ids)

    @api.multi
    def action_open_nfe(self):
        """ This function returns an action that display existing imported documents of given purchase order ids. When only one found, show the document immediately.
        """
        result = self.env.ref('nfe_import.action_document_tree_all').read()[0]
        document_ids = self.mapped('imported_nfe_ids')
        # choose the view_mode accordingly
        if not document_ids or len(document_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (document_ids.ids)
        elif len(document_ids) == 1:
            res = self.env.ref('l10n_br_fiscal.document_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = document_ids.id
        return result

    def action_open_import_document(self):
        result = self.env.ref('l10n_br_nfe.l10n_br_nfe_import_xml_action').read()[0]
        result['context'] = {'default_purchase_id': self.id}
        res = self.env.ref('l10n_br_nfe.l10n_br_nfe_import_xml_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        return result

    @api.multi
    def action_open_link_nfe(self):
        self.ensure_one()
        result = self.env.ref('nfe_import.act_link_nfe').read()[0]
        result['context'] = {'default_origin_model': 'purchase', 'default_link_with': 'purchase'}
        return result

    def button_unlink_nfe(self):
        for picking in self.picking_ids:
            if picking.state == 'done':
                raise UserError(_('Impossível desconciliar documentos após conclusão da transferência.'))
        self.write({'imported_nfe_ids': [(5,)]})

    @api.multi
    def _add_supplier_to_product(self):
        res = super(PurchaseOrder, self)._add_supplier_to_product()
        for line in self.order_line:
            product_id = line.product_id
            supplierinfo = product_id.seller_ids.filtered(lambda s: s.name == self.partner_id)[0]
            if supplierinfo and not supplierinfo.product_id:
                product_id.write({'seller_ids': [(1, supplierinfo.id, {'product_id': product_id.id})]})
        return res
