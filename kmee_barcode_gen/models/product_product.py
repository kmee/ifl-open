# Copyright 2023 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import re


class ProductProduct(models.Model):
    _inherit = "product.product"

    barcode_bkp = fields.Char(
        string="Barcode Bkp",
        compute="_compute_barcode_bkp",
        store=True,
    )

    def _compute_barcode_bkp(self):
        for record in self:
            record.barcode_bkp = record.barcode

    @api.constrains("default_code")
    def _constrain_default_code(self):
        for record in self:
            # 1. if more than one alphabetical chracter continue
            if len(re.findall("[a-zA-Z]", record.default_code)) > 1:
                continue

            # 2. check one letter and  letters not f, l, v, m, g raise
            if len(re.findall("[a-zA-Z]", record.default_code)) == 1:
                letter = re.findall("[a-zA-Z]", record.default_code)[0]

                if letter not in ["f", "l", "v", "m", "g"]:
                    raise ValidationError(
                        "A nomenclatura estabelecida não permite códigos com letras"
                        " exceto f, l, v, m ou g"
                    )

                if (
                    len(record.default_code) != 4
                    or record.default_code.find(letter) != 0
                ):
                    raise ValidationError(
                        "A nomenclatura estabelecida não permite letras exceto seguidas"
                        " por 3 dígitos numéricos e sem prefixo."
                    )

            # 3. check thousand's digit is 1, 2, 3, 4, 5 raise
            if record.default_code[-4:-3] in ["1", "2", "3", "4", "5"]:
                raise ValidationError(
                    "A nomenclatura estabelecida não permite dígitos 1, 2, 3, 4, 5 na"
                    " posição de digito milhar. Essas posições são reservadas para as"
                    " letras f, l, v, m, g!"
                )
