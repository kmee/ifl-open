# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons.queue_job.job import job
import odoorpc


class ImportRemoteRecords(models.TransientModel):

    _name = 'import.remote.records'

    fields_to_import_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        string='Fields to Import',
        domain=lambda r: "[('model', '=', '%s')]" %
            r._context.get('active_model'),
    )
    number_of_records = fields.Integer(
        string='Number of records to import',
        default=500,
    )
    only_new_records = fields.Boolean(
        string='Consider only new records?',
    )
    errors = fields.Text()

    def _get_remote_instance(self):
        remote_host = self.env['ir.config_parameter'].get_param(
            'import_records.remote_host')
        remote_port = self.env['ir.config_parameter'].get_param(
            'import_records.remote_port')
        remote = odoorpc.ODOO(host=remote_host, port=remote_port, timeout=500)
        db_name = self.env['ir.config_parameter'].get_param(
            'import_records.remote_db_name')
        login = self.env['ir.config_parameter'].get_param(
            'import_records.remote_login')
        passwd = self.env['ir.config_parameter'].get_param(
            'import_records.remote_password')
        remote.login(db_name, login, passwd)
        return remote

    def _get_fields_to_import(self, active_model, exclude_binary=False):
        remote = self._get_remote_instance()

        local_obj = self.env[active_model]
        local_fields = local_obj.fields_get()

        remote_obj = remote.env[active_model]
        remote_field_items = remote_obj.fields_get().items()

        fields_to_not_import = [
            '__last_update', 'create_date', 'create_uid', 'display_name',
            'id', 'write_date', 'write_uid'
        ]

        fields_to_import = []
        for name, data in remote_field_items:
            if name not in local_fields.keys():
                continue
            if data.get('type') == 'selection':
                if any(opt not in local_fields.get(name, {}).get(
                       'selection', []) for opt in data.get('selection')):
                    continue
            if exclude_binary and data.get('type') in ('binary', 'image'):
                continue
            if data.get('relation'):
                continue
            if name in fields_to_not_import:
                continue
            fields_to_import.append(name)
        return fields_to_import

    def clear_fields_to_import(self):
        self.fields_to_import_ids = [(6, 0, [])]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.remote.records',
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_model = self.env.context.get('active_model')

        fields_to_import = self._get_fields_to_import(active_model)

        rec.update(
            fields_to_import_ids=[(6, 0, self.env['ir.model.fields'].search([
                ('model', '=', active_model),
                ('name', 'in', fields_to_import)
            ]).ids)]
        )
        return rec

    @job
    def import_record(self, active_model, remote_record_id, fields_to_import):
        remote = self._get_remote_instance()

        local_obj = self.env[active_model]

        remote_obj = remote.env[active_model]

        remote_record = remote_obj.browse(remote_record_id)

        remote_vals = remote_record.read(fields_to_import)[0]
        remote_vals.update({'remote_record_id': remote_record_id})

        if active_model == 'mrp.bom':
            remote_vals.update({
                'product_tmpl_id': self.env['product.template'].search([
                    ('remote_record_id', '=',
                     remote_record.product_tmpl_id.id)
                ]).id
            })
        elif active_model == 'stock.warehouse.orderpoint':
            remote_vals.update({
                'product_id': self.env['product.template'].search([
                    ('remote_record_id', '=',
                     remote_record.product_id.product_tmpl_id.id)
                ]).product_variant_ids.id
            })
        elif active_model == 'sale.order':
            remote_vals.update({
                'company_id': self.env['res.company'].search([
                    ('name', '=', 'ASTUSTECNICA')
                ]).id,
                'partner_id': self.env['res.partner'].search([
                    ('remote_record_id', '=', remote_record.partner_id.id)
                ]).id,
                'state': remote_record.state,
                'user_id': self.env['res.users'].search([
                    ('remote_record_id', '=', remote_record.user_id.id)
                ]).id,
                'require_signature': True,
                'picking_policy': remote_record.picking_policy,
                'discount_rate': remote_record.discount_value
                if remote_record.discount_type == 'percent' else 0.0,
            })
        elif active_model == 'stock.production.lot':
            remote_vals.update({
                'product_id': self.env['product.template'].search([
                    ('remote_record_id', '=',
                     remote_record.product_id.product_tmpl_id.id)
                ]).product_variant_ids.id
            })

        local_record = local_obj.create(remote_vals)
        if active_model == 'sale.order':
            self.with_delay(priority=9).import_order_line(
                    local_record, 'order_line'
                )

    @api.multi
    def action_import(self):
        result_ids = []
        for wizard in self:
            errors = []

            remote = self._get_remote_instance()

            active_model = self.env.context.get('active_model')

            local_obj = self.env[active_model]

            remote_obj = remote.env[active_model]

            already_imported = local_obj.search([
                ('remote_record_id', '!=', False)]).mapped('remote_record_id')

            domain = [('id', 'not in', already_imported)]
            if active_model == 'sale.order':
                domain += [('state', 'in', ['draft', 'sent'])]
                domain += [('company_id', 'in', [5, 1])]

            for remote_record_id in remote_obj.search(domain):
                wizard.with_delay().import_record(
                    active_model,
                    remote_record_id,
                    wizard.fields_to_import_ids.mapped('name')
                )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.remote.records',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    @job
    def import_fiscal_settings(self, active_model, local_record):
        remote = self._get_remote_instance()

        local_obj = self.env[active_model]

        remote_obj = remote.env[active_model]

        remote_record = remote_obj.browse(local_record.remote_record_id)
        remote_code = remote_record.ncm_id.code
        #local_code = '%s.%s.%s' % (
        #    remote_code[:4], remote_code[4:6], remote_code[6:]
        #) if remote_code and len(remote_code) == 8 else False
        local_ncm = self.env['l10n_br_fiscal.ncm'].search([
            ('code', '=', remote_code)
        ], limit=1)
        local_record.ncm_id = local_ncm
        if local_record.ncm_id:
            local_record.fiscal_settings_imported = True


    @api.multi
    def action_import_fiscal_settings(self):
        for wizard in self:
            remote = self._get_remote_instance()

            active_model = self.env.context.get('active_model')

            local_obj = self.env[active_model]

            remote_obj = remote.env[active_model]

            for local_record in local_obj.search([
                    ('remote_record_id', '!=', False),
                    ('fiscal_settings_imported', '=', False),
            ]):
                wizard.with_delay().import_fiscal_settings(
                    active_model, local_record)

    @job
    def import_one2many_field(self, local_record, field_name):
        remote = self._get_remote_instance()
        # remote_record_id = local_record.remote_record_id

        active_model = local_record._name
        remote_obj = remote.env[active_model]

        local_data_id = self.env['ir.model.data'].search([
            ('model', '=', active_model),
            ('res_id', '=', local_record.id),
        ])

        remote_data_id = remote.env['ir.model.data'].search([
            ('model', '=', active_model),
            ('name', '=', local_data_id.name),
        ])
        remote_record_id = remote_data_id.res_id

        remote_field_values = remote_obj.fields_get().get(field_name)
        comodel_name = remote_field_values.get('relation')
        inverse_name = remote_field_values.get('relation_field')

        remote_comodel_obj = remote.env[comodel_name]

        fields_to_import = self._get_fields_to_import(
            comodel_name, exclude_binary=False
        )

        for remote_field_record_id in remote_comodel_obj.search([
                (inverse_name, '=', remote_record_id),
        ]):
            vals = remote_comodel_obj.browse(remote_field_record_id).read(
                fields_to_import
            )[0]
            domain = [(inverse_name, '=', local_record.id)]
            if vals.get('name') and vals.get('code'):
                domain += [
                    '|', ('name', '=', vals['name']),
                    ('code', '=', vals['code'])
                ]
            elif vals.get('name'):
                domain += [('name', '=', vals['name'])]
            elif vals.get('code'):
                domain += [('code', '=', vals['code'])]
            records_to_update = self.env[comodel_name].search(domain)
            if not records_to_update:
                vals.update({inverse_name: local_record.id})
                self.env[comodel_name].create(vals)
            else:
                records_to_update.write(vals)

    @job
    def update_record(self, local_record, fields_to_update):
        remote = self._get_remote_instance()

        remote_obj = remote.env[local_record._name]

        remote_record = remote_obj.browse(local_record.remote_record_id)
        remote_vals = remote_record.read(
            fields_to_update.mapped('name')
        )[0]

        local_record.write(remote_vals)

    @api.multi
    def action_update_prices(self):
        fields_to_import = [
            'list_price', 'lst_price', 'price', 'pricelist_id',
            'standard_price', 'website_price', 'website_price_difference',
            'website_public_price'
        ]
        for wizard in self:
            active_model = self.env.context.get('active_model')

            for local_record in self.env[active_model].search([
                ('remote_record_id', '!=', False)] + [
                    ('create_date', '>=', fields.Date.today())
                ] if wizard.only_new_records else [
            ]):
                wizard.with_delay().update_record(
                    local_record, self.env['ir.model.fields'].search([
                        ('name', 'in', fields_to_import),
                        ('model', '=', active_model),
                    ])
                )

    @api.multi
    def action_import_images(self):
        for wizard in self:
            active_model = self.env.context.get('active_model')

            local_obj = self.env[active_model]

            for local_record in local_obj.search([
                ('product_image_ids', '=', False)
            ]):
                wizard.with_delay().import_one2many_field(
                    local_record, 'product_image_ids'
                )

    @api.multi
    def action_import_variants(self):
        for wizard in self:
            active_model = self.env.context.get('active_model')

            local_obj = self.env[active_model]

            for local_record in local_obj.search([
                ('remote_record_id', '!=', False)] + [
                    ('create_date', '>=', fields.Date.today())
                ] if wizard.only_new_records else [
            ]):
                wizard.with_delay().import_one2many_field(
                    local_record, 'product_variant_ids'
                )

    @api.multi
    def action_import_seller_ids(self):
        for wizard in self:
            active_model = self.env.context.get('active_model')

            local_obj = self.env[active_model]

            for local_record in local_obj.search([
                ('remote_record_id', '!=', False)
            ]):
                wizard.with_delay().import_one2many_field(
                    local_record, 'seller_ids'
                )

    @api.multi
    def action_update_records(self):
        for wizard in self:
            active_model = self.env.context.get('active_model')

            local_obj = self.env[active_model]

            for local_record in local_obj.search([
                ('remote_record_id', '!=', False),
            ]):
                wizard.with_delay().update_record(
                    local_record, wizard.fields_to_import_ids
                )

    @api.multi
    def action_import_inventory(self):
        for wizard in self:
            active_model = self.env.context.get('active_model')
            local_obj = self.env[active_model].browse(
                self.env.context.get('active_record')
            )
            local_obj.import_remote_inventory()
