from odoo import fields, models


class Volumes(models.Model):
    _name = "kmee_delivery.volumes"
    _description = "Dados dos Volumes"

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Picking',
    )

    document_id = fields.Many2one(
        comodel_name='l10n_br_fiscal.document',
        string='Fiscal Document',
    )

    quantidade = fields.Char(
        string="Quantidade de volumes transportados",
        default="1",
    )

    especie = fields.Char(
        string="Espécie dos volumes transportados",
    )

    marca = fields.Char(
        string="Marca dos volumes transportados",
        default="Trace",
    )

    numero_volume = fields.Char(
        string="Numeração dos volumes transportados",
    )

    peso_liquido = fields.Float(
        digits=(16, 3),
        string="Peso líquido (em kg)",
    )

    peso_bruto = fields.Float(
        digits=(16, 3),
        string="Peso bruto (em kg)",
    )

    lacres_ids = fields.One2many(
        "kmee_delivery.lacres",
        "volume_id",
        string="Lacres"
    )


class Lacres(models.Model):
    _description = 'Lacres'
    _name = 'kmee_delivery.lacres'

    volume_id = fields.Many2one(
        "kmee_delivery.volumes"
    )

    numero_lacre = fields.Char(
        string="Número dos Lacres"
    )
