# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    remote_host = fields.Char(
        string="Remote IP",
    )
    remote_port = fields.Integer(
        string="Remote Port",
        default=8069,
    )
    remote_db_name = fields.Char(
        string="Remote DB Name",
    )
    remote_login = fields.Char(
        string="Remote Login",
    )
    remote_password = fields.Char(
        string="Remote Password",
    )

    @api.model
    def get_values(self):
        res = super().get_values()

        res['remote_host'] = self.env['ir.config_parameter'].sudo().get_param(
            'import_records.remote_host', default='')
        res['remote_port'] = int(
            self.env['ir.config_parameter'].sudo().get_param(
                'import_records.remote_port', default=8069))
        res['remote_db_name'] = \
            self.env['ir.config_parameter'].sudo().get_param(
                'import_records.remote_db_name', default='')
        res['remote_login'] = \
            self.env['ir.config_parameter'].sudo().get_param(
                'import_records.remote_login', default='')
        res['remote_password'] = \
            self.env['ir.config_parameter'].sudo().get_param(
                'import_records.remote_password', default='')

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'import_records.remote_host', self.remote_host)
        self.env['ir.config_parameter'].sudo().set_param(
            'import_records.remote_port', self.remote_port)
        self.env['ir.config_parameter'].sudo().set_param(
            'import_records.remote_db_name', self.remote_db_name)
        self.env['ir.config_parameter'].sudo().set_param(
            'import_records.remote_login', self.remote_login)
        self.env['ir.config_parameter'].sudo().set_param(
            'import_records.remote_password', self.remote_password)

        super(ResConfigSettings, self).set_values()
