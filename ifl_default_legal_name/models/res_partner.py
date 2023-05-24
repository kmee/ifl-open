import copy

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

try:
    from erpbrasil.base.fiscal import cnpj_cpf, ie
except ImportError:
    _logger.error("Biblioteca erpbrasil.base não instalada")


class ResPartner(models.Model):
    _inherit = "res.partner"

    legal_name = fields.Char(
        string="Razão Social",
        store=True,
    )

    @api.multi
    @api.depends("name")
    def _compute_default_legal_name(self):
        for record in self:
            if not record.legal_name:
                record.legal_name = record.name
        pass

    @api.constrains("cnpj_cpf", "inscr_est")
    def _check_cnpj_inscr_est(self):
        for record in self:
            domain = []

            # permite cnpj vazio
            if not record.cnpj_cpf:
                return

            if self.env.context.get("disable_allow_cnpj_multi_ie"):
                return

            allow_cnpj_multi_ie = (
                record.env["ir.config_parameter"]
                .sudo()
                .get_param("l10n_br_base.allow_cnpj_multi_ie", default=True)
            )

            if record.parent_id:
                domain += [
                    ("id", "not in", record.parent_id.ids),
                    ("parent_id", "not in", record.parent_id.ids),
                ]

            domain += [("cnpj_cpf", "=", record.cnpj_cpf), ("id", "!=", record.id)]

            # se encontrar CNPJ iguais
            if record.env["res.partner"].search(domain):
                if cnpj_cpf.validar_cnpj(record.cnpj_cpf):
                    if allow_cnpj_multi_ie == "True":
                        for partner in record.env["res.partner"].search(domain):
                            if (
                                partner.inscr_est == record.inscr_est
                                and not record.inscr_est
                            ):
                                raise ValidationError(
                                    _(
                                        "There is already a partner record with this "
                                        "Estadual Inscription !"
                                    )
                                )
                    else:
                        if record.supplier == False:
                            continue
                        raise ValidationError(
                            _("There is already a partner record with this CNPJ !")
                        )
                else:
                    if record.supplier == False:
                        continue
                    raise ValidationError(
                        _("There is already a partner record with this CPF/RG!")
                    )
