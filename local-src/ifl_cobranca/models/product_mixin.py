from odoo import api, models


class ProductMixin(models.AbstractModel):
    _inherit = "l10n_br_fiscal.product.mixin"

    @api.onchange("ncm_id", "fiscal_genre_id")
    def _onchange_ncm_id(self):
        for r in self:
            if r.ncm_id:
                r.fiscal_genre_id = self.env["l10n_br_fiscal.product.genre"].search(
                    [("code", "=", r.ncm_id.code[0:2])]
                )

            if r.fiscal_genre_id.code == "00":
                r.ncm_id = self.env.ref("l10n_br_fiscal.ncm_00000000")
