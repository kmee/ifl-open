# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Document(models.Model):
    _inherit = "l10n_br_fiscal.document"

    nfe40_modFrete = fields.Selection(
        default=None,
    )

    nfe40_transporta = fields.Many2one(
        comodel_name="res.partner",
        string="Dados do transportador",
    )

    volume_ids = fields.One2many(
        comodel_name='kmee_delivery.volumes',
        inverse_name='document_id',
        string='Dados dos Volumes',
        required=False
    )

    @api.model
    def create(self, values):
        if not values.get("nfe40_modFrete"):
            values['nfe40_modFrete'] = "9"
        if values.get("modFrete"):
            values['nfe40_modFrete'] = values.get("modFrete")
        else:
            values['modFrete'] = values.get("nfe40_modFrete")
        if values.get("transporter_id"):
            values['nfe40_transporta'] = values['transporter_id']
        else:
            values['transporter_id'] = values.get("nfe40_transporta", False)
        res = super(Document, self).create(values)
        return res

    @api.multi
    def copy_data(self, default=None):
        # Copy nfe40_vol
        if default is None:
            default = {}
        new_vols = self.env["nfe.40.vol"]
        for vol in self.nfe40_vol:
            new_vol = vol.copy()
            new_lacres = self.env["nfe.40.lacres"]
            for lacre in vol.nfe40_lacres:
                new_lacres += lacre.copy()
            new_vol.nfe40_lacres = [(6, 0, new_lacres.ids)]
            new_vols += new_vol
        default['nfe40_vol'] = [(6, 0, new_vols.ids)]
        # Generate volume_ids
        if self.nfe40_vol:
            volumes = self.env["kmee_delivery.volumes"]
            for vol in self.nfe40_vol:
                lacres = self.env["kmee_delivery.lacres"]
                for lacre in vol.nfe40_lacres:
                    lacres += lacres.create(
                        {
                            "numero_lacre": lacre.nfe40_nLacre,
                        }
                    )
                volumes += volumes.create(
                    {
                        "quantidade": vol.nfe40_qVol,
                        "especie": vol.nfe40_esp,
                        "marca": vol.nfe40_marca,
                        "numero_volume": vol.nfe40_nVol,
                        "peso_liquido": vol.nfe40_pesoL,
                        "peso_bruto": vol.nfe40_pesoB,
                        "lacres_ids": [(6, 0, lacres.ids)]
                    }
                )
            default['volume_ids'] = [(6, 0, volumes.ids)]
        return super(Document, self).copy_data(default)
