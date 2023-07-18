# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class FiscalDocumentMixinMethods(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.mixin.methods"

    def action_open_purchase(self):
        """ This function returns an action that display existing imported documents of given picking ids. When only one found, show the document immediately.
        """
        result = self.env.ref('nfe_import.action_purchase_tree_all').read()[0]
        purchase_ids = self.mapped('linked_purchase_ids')
        # choose the view_mode accordingly
        if not purchase_ids or len(purchase_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (purchase_ids.ids)
        elif len(purchase_ids) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = purchase_ids[0].id
        return result

    def action_open_industrialization_picking(self):
        """ This function returns an action that display existing imported documents of given picking ids. When only one found, show the document immediately.
        """
        result = self.env.ref('nfe_import.action_picking_tree_all').read()[0]
        industrialization_picking_ids = self.mapped('industrialization_picking_ids')
        # choose the view_mode accordingly
        if not industrialization_picking_ids or len(industrialization_picking_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (industrialization_picking_ids.ids)
        elif len(industrialization_picking_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = industrialization_picking_ids[0].id
        return result
