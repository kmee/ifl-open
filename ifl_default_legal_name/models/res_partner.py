import copy

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    legal_name = fields.Char(
        compute="_compute_default_legal_name",
        store=True,
    )

    @api.multi
    @api.depends('name')
    def _compute_default_legal_name(self):
        for record in self:
            if not record.legal_name:
                record.legal_name = record.name
        pass
