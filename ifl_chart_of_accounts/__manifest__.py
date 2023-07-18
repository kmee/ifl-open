# Copyright 2020 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ifl Chart Of Accounts',
    'description': """
        Esse módulo implementa o plano de contas customizado do Instituto Feira Livre.""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE INFORMATICA LTDA',
    'website': 'www.kmee.com.br',
    "depends": [
        "l10n_br_coa"
    ],
    "data": [
        "data/ifl_coa_template.xml",
        "data/account_group.xml",
        "data/account.account.template.csv",
        "data/account_tax_group.xml",
        "data/account_fiscal_position_template.xml",
        "data/ifl_coa_template_post.xml",
    ],
    "post_init_hook": "post_init_hook",
    'demo': [
    ],
}
