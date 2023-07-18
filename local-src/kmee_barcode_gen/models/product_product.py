# Copyright 2023 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import re


class ProductProduct(models.Model):
    _inherit = "product.product"

    not_auto_gen_barcode_internal = fields.Boolean(
        string="Não gera barcode interno",
        copy=False,
    )

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

    @api.constrains("not_auto_gen_barcode_internal")
    def _constrain_not_auto_gen_barcode_internal(self):
        for record in self:
            if record.not_auto_gen_barcode_internal and record.uom_id != self.env.ref(
                "uom.product_uom_kgm"
            ):
                raise ValidationError(
                    "O checkbox 'Não gera barcode interno' não pode ser utilizado em"
                    " produtos cuja Unidade de Medida não seja kg."
                )

    @api.onchange("default_code")
    def _onchange_default_code_barcode(self):
        for record in self:
            if record.not_auto_gen_barcode_internal:
                continue

            if record.uom_id != self.env.ref("uom.product_uom_kgm"):
                continue

            record._constrain_default_code()
            record.barcode = record.generate_ean13_internal_barcode()

    @api.onchange("not_auto_gen_barcode_internal")
    def _onchange_not_auto_gen_barcode_internal(self):
        self._onchange_default_code_barcode()

    @api.onchange("uom_id")
    def _onchange_uom_id_barcode(self):
        self._onchange_default_code_barcode()

    def generate_ean13_internal_barcode(self):
        if len(self.default_code) > 6:
            raise ValidationError(
                "Não é possível criar código de barras para produtos com referência"
                " interna com mais de 6 caracteres"
            )

        ean = ""
        base_ean = "2" + self.default_code.zfill(6) + "".zfill(5)

        base_ean = base_ean.replace("f", "1")
        base_ean = base_ean.replace("l", "2")
        base_ean = base_ean.replace("v", "3")
        base_ean = base_ean.replace("m", "4")
        base_ean = base_ean.replace("g", "5")

        oddsum = 0
        evensum = 0
        total = 0

        code = base_ean[::-1]

        for i in range(len(code)):
            if i % 2 == 0:
                oddsum += int(code[i])
            else:
                evensum += int(code[i])

        total = oddsum * 3 + evensum

        ean = base_ean + str((10 - total % 10) % 10)
        return ean
