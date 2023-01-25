# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

import re


class Document(models.Model):

    _inherit = "l10n_br_fiscal.document"

    linked_purchase_ids = fields.Many2many(
        comodel_name='purchase.order',
        relation='nfe_purchase_relation_1',
        column1='document_id',
        column2='purchase_id',
        string='Ordens de Compra',
        copy=False,
    )

    industrialization_picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        string='Transferências de Industrialização',
        required=False,
        default=False,
        copy=False,
    )

    linked_purchase_count = fields.Integer(compute="_compute_linked_purchase_count")

    linked_industrialization_picking_count = fields.Integer(compute="_compute_linked_industrialization_picking_count")

    @api.multi
    def _compute_linked_purchase_count(self):
        for rec in self:
            rec.linked_purchase_count = len(rec.linked_purchase_ids)
    @api.multi
    def _compute_linked_industrialization_picking_count(self):
        for rec in self:
            rec.linked_industrialization_picking_count = len(rec.industrialization_picking_ids)

    imported_document = fields.Boolean(copy=False)

    @api.multi
    def action_open_link_nfe(self):
        self.ensure_one()
        result = self.env.ref('nfe_import.act_link_nfe').read()[0]
        result['context'] = {'default_origin_model': 'document'}
        return result

    def button_unlink_po_nfe(self):
        for purchase in self.linked_purchase_ids:
            if purchase.picking_ids.filtered(lambda p: p.state == 'done'):
                continue
            self.write({'linked_purchase_ids': [(3, purchase.id)]})

    def button_unlink_picking_nfe(self):
        for picking in self.industrialization_picking_ids.filtered(lambda p: p.state != 'done'):
            self.write({'industrialization_picking_ids': [(3, picking.id)]})
