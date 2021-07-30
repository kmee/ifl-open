import copy

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fiscal_profile_id = fields.Many2one(
        compute="_compute_default_fiscal_profile_id",
        store=True,
    )

    @api.multi
    def _compute_default_fiscal_profile_id(self):
        default_profile = self.env.ref('l10n_br_fiscal.partner_fiscal_profile_isent')
        for record in self:
            if not record.fiscal_profile_id:
                record.fiscal_profile_id = default_profile
        pass
