# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    @api.multi
    def _build_invoice_values_from_pickings(self, pickings):
        """
        Build dict to create a new invoice from given pickings
        :param pickings: stock.picking recordset
        :return: dict
        """
        invoice, values = super(StockInvoiceOnshipping, self)._build_invoice_values_from_pickings(pickings)
        picking = fields.first(pickings)
        values.update({
            'volume_ids': [(6, 0, picking.volume_ids.ids)],
        })
        invoice, values = self._simulate_invoice_onchange(values)
        return invoice, values
