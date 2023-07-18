# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    remote_record_id = fields.Integer(string="Remote Product Id")

    last_update_at = fields.Datetime(
        string='Last update at',
        readonly=True,
    )

    fiscal_settings_imported = fields.Boolean(
        string="Fiscal Settings Imported?",
        default=False,
    )
