# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    DOCUMENT_ISSUER_COMPANY,
    MODELO_FISCAL_NFCE,
    MODELO_FISCAL_NFE,
    PROCESSADOR_OCA,
)


def filter_nfe(record):
    if (
        record.processador_edoc == PROCESSADOR_OCA
        and record.document_type_id.code
        in [
            MODELO_FISCAL_NFE,
            MODELO_FISCAL_NFCE,
        ]
        and record.issuer == DOCUMENT_ISSUER_COMPANY
    ):
        return True
    return False


class DocumentWorkflow(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.workflow"

    def action_document_confirm(self):
        for record in self.filtered(filter_nfe):
            record.nfe40_vol = [(5,)]
            if record.volume_ids:
                volumes = record.env["nfe.40.vol"]
                for vol in record.volume_ids:
                    lacres = record.env["nfe.40.lacres"]
                    for lacre in vol.lacres_ids:
                        lacres += lacres.create(
                            {
                                "nfe40_nLacre": lacre.numero_lacre,
                            }
                        )
                    volumes += volumes.create(
                        {
                            "nfe40_qVol": vol.quantidade,
                            "nfe40_esp": vol.especie,
                            "nfe40_marca": vol.marca,
                            "nfe40_nVol": vol.numero_volume,
                            "nfe40_pesoL": vol.peso_liquido,
                            "nfe40_pesoB": vol.peso_bruto,
                            "nfe40_lacres": [(6, 0, lacres.ids)]
                        }
                    )
                record.nfe40_vol = [(6, 0, volumes.ids)]
            if record.modFrete:
                record.nfe40_modFrete = record.modFrete
            if record.transporter_id:
                    record.nfe40_transporta = record.transporter_id

        super().action_document_confirm()
