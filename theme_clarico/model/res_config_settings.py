

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_pricelist_display = fields.Many2one(
        comodel_name='product.pricelist',
        string='Website pricelist display',
        required=True,
        config_parameter='theme_clarico.default_website_pricelist_display',
    )
    website_pricelist_charge = fields.Many2one(
        comodel_name='product.pricelist',
        string='Website pricelist charge',
        required=True,
        config_parameter='theme_clarico.default_website_pricelist_charge',
    )