# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from urllib.parse import quote
from odoo.exceptions import UserError


class WizardProductReplace(models.TransientModel):

    _name = 'wizard.product.replace'

    source_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Produto solicitado",
        required=False,
        )

    source_qty = fields.Float(
        string="Quantidade solicitada",
        required=False,
        )

    dest_qty = fields.Float(
        string="Quantidade nova",
        required=False,
        )

    dest_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Produto novo",
        required=False,
        )

    @api.model
    def default_get(self, fields):
        res = super(WizardProductReplace, self).default_get(fields)

        model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        move_id = self.env[model].browse(active_ids)

        res.update({
            'source_product_id': move_id.product_id.id,
            'source_qty': move_id.product_uom_qty,
            'dest_qty': move_id.product_uom_qty,
            })
        return res

    def action_apply(self):
        model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        move_id = self.env[model].browse(active_ids)

        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may only replace one picking at a time!"))

        picking_id = move_id.picking_id
        sale_order_id = picking_id.sale_id

        # if dest product -> add to SO
        if self.dest_product_id:
            order_line = self.env['sale.order.line'].sudo()
            dest_product_id = self.env['product.product']\
                .browse(self.dest_product_id.id)

            line_id = order_line.create({
                'product_id': dest_product_id.id,
                'order_id': sale_order_id.id,
                'is_replacement': True,
                'product_uom_qty': self.dest_qty,
                })

            line_id._onchange_product_id_fiscal()
            line_id._onchange_commercial_quantity()
            line_id._onchange_ncm_id()
            line_id._onchange_fiscal_operation_id()
            line_id._onchange_fiscal_operation_line_id()
            line_id._onchange_fiscal_taxes()
            line_id._onchange_fiscal_tax_ids()

            # sale_order_line_data = line_id._convert_to_write(line_id._cache)
            # order_line.create(sale_order_line_data)

            move_id.cancel_move()
