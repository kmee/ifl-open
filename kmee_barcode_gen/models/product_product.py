# Copyright 2023 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


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
