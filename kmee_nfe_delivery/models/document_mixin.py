# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

# Modalidade do frete
MODFRETE_TRANSP = [
    ("0", "0 - Contratação do Frete por conta do Remetente (CIF)"),
    ("1", "1 - Contratação do Frete por conta do" " destinatário/remetente (FOB)"),
    ("2", "2 - Contratação do Frete por conta de terceiros"),
    ("3", "3 - Transporte próprio por conta do remetente"),
    ("4", "4 - Transporte próprio por conta do destinatário"),
    ("9", "9 - Sem Ocorrência de transporte."),
]


class DocumentMixin(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.mixin"

    transporter_id = fields.Many2one(
        comodel_name='res.partner',
        string='Transportadora',
        required=False
    )

    modFrete = fields.Selection(
        MODFRETE_TRANSP,
        string="Modalidade do frete",
        help="Modalidade do frete"
             "\n0- Contratação do Frete por conta do Remetente (CIF);"
             "\n1- Contratação do Frete por conta do destinatário/remetente (FOB);"
             "\n2- Contratação do Frete por conta de terceiros;"
             "\n3- Transporte próprio por conta do remetente;"
             "\n4- Transporte próprio por conta do destinatário;"
             "\n9- Sem Ocorrência de transporte."
    )
