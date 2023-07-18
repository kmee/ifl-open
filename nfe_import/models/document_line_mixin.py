from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FiscalDocumentLineMixin(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin"

    origin_nfe_id = fields.Many2one(
        comodel_name='l10n_br_fiscal.document',
        string='Nota de Origem',
        required=False,
    )

    origin_nfe_line_id = fields.Many2one(
        comodel_name='l10n_br_fiscal.document.line',
        string='Nota de Origem',
        required=False,
    )
