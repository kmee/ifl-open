# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_transporter = fields.Boolean(
        string="É transportadora",
        required=False,
        default=False,
    )

    @api.constrains("is_transporter", "street_name", "street_number", "street2")
    def check_transporter_address(self):
        for record in self:
            if record.is_transporter:
                address = [record.street_name, record.street_number, record.street2]
                str_length = 0
                for s in address:
                    str_length += len(s) if s else 0

                if str_length and str_length > 60:
                    raise ValidationError(
                        _(
                            "A soma do número de caracteres do nome da rua,"
                            " número e complemento do enredeço de transportadoras"
                            " não pode ser maior que 60."
                        )
                    )
