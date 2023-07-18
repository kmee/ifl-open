# Copyright 2020 Akretion (Raphaël Valyi <raphael.valyi@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    # We overwrite this method to search by default_code, as it'll be edited to match an internal product by the import wizard
    def match_or_create_m2o(self, rec_dict, parent_dict, model=None):
        domain = []
        if parent_dict.get("nfe40_cProd"):
            rec_dict["default_code"] = parent_dict["nfe40_cProd"]
            domain = [("default_code", "=", rec_dict.get("default_code"))]
        match = self.search(domain, limit=1)
        if match:
            return match.id
        return super().match_or_create_m2o(rec_dict, parent_dict, model)
