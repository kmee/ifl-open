# Copyright (C) 2020 - Gabriel Cardoso de Faria <gabriel.cardoso@kmee.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, tools, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    coa_ifl_tmpl = env.ref(
        'ifl_chart_of_accounts.ifl_coa_chart_template')
    if env['ir.module.module'].search_count([
        ('name', '=', 'l10n_br_account'),
        ('state', '=', 'installed'),
    ]):
        from odoo.addons.l10n_br_account.hooks import load_fiscal_taxes
        # Relate fiscal taxes to account taxes.
        load_fiscal_taxes(env, coa_ifl_tmpl)

    # Load COA to Demo Company
    if not tools.config.get('without_demo'):
        user_admin = env.ref('base.user_admin')
        company = env.ref(
            'base.main_company', raise_if_not_found=False)
        if company:
            user_admin.company_id = company
            coa_ifl_tmpl.sudo(
                user=user_admin.id).try_loading_for_current_company()
            user_admin.company_id = env.ref('base.main_company')
