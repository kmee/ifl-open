# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from unidecode import unidecode


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends("name", "attribute_value_ids", "auto_generate_default_code")
    def _compute_default_code(self):
        for record in self:
            if not record.auto_generate_default_code:
                if record.manual_default_code:
                    record.default_code = record.manual_default_code
                continue
            default_code = record.name[0:30] if record.name else ""
            if record.attribute_value_ids:
                max_attr_len = ((60 - len(default_code))//len(record.attribute_value_ids)) - 1  # Must leave space for hyphens
                for attr in record.attribute_value_ids:
                    default_code += "-" + attr.name[0:max_attr_len]
            default_code = unidecode(default_code.replace(" ", "-").upper())
            record.default_code = default_code

    def _inverse_default_code(self):
        for record in self:
            if record.default_code:
                record.manual_default_code = record.default_code
            elif record.manual_default_code and not record.auto_generate_default_code:
                record.default_code = record.manual_default_code
            record.auto_generate_default_code = False

    default_code = fields.Char(
        'Internal Reference',
        index=True,
        compute=_compute_default_code,
        inverse=_inverse_default_code,
        store=True
    )

    manual_default_code = fields.Char(
        'Manually inserted default code',
        required=False,
        store=True,
    )

    auto_generate_default_code = fields.Boolean(
        'Gerar Referência Automaticamente',
        default=True,
    )
