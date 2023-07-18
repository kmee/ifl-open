# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from erpbrasil.base.fiscal.edoc import ChaveEdoc
from erpbrasil.base.fiscal.edoc import detectar_chave_edoc, CHAVE_REGEX
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.l10n_br_nfe.models.document import parse_xml_nfe


class NfeImport(models.TransientModel):
    """ Importar XML Nota Fiscal Eletrônica """

    _inherit = "l10n_br_nfe.import_xml"

    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        required=False,
        default=False,
    )

    industrialization_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Stock Picking',
        required=False,
        default=False,
    )

    def _parse_xml_import_wizard(self, xml):
        parsed_xml = parse_xml_nfe(xml)

        matcher = CHAVE_REGEX.match(parsed_xml.infNFe.Id[3:])
        if not matcher:
            chave_edoc = ChaveEdoc(
                ano_mes=datetime.fromisoformat(parsed_xml.infNFe.ide.dhEmi).strftime('%y%m'),
                cnpj_emitente=parsed_xml.infNFe.emit.CNPJ,
                codigo_uf=(parsed_xml.infNFe.ide.cUF or ""),
                forma_emissao=1,
                modelo_documento=parsed_xml.infNFe.ide.mod or "",
                numero_documento=parsed_xml.infNFe.ide.nNF or "",
                numero_serie=parsed_xml.infNFe.ide.serie or "",
                validar=False,
            )
            parsed_xml.infNFe.Id = chave_edoc.prefixo + chave_edoc.chave

        document = detectar_chave_edoc(parsed_xml.infNFe.Id[3:])

        return parsed_xml, document

    def import_nfe_xml(self):
        res = super(NfeImport, self).import_nfe_xml()
        edoc = self.env["l10n_br_fiscal.document"].browse(res['res_id'])
        conciliated_obj = None

        if self.purchase_id:
            conciliated_obj = self.purchase_id
            edoc.linked_purchase_id = conciliated_obj
            if len(self.purchase_id.picking_ids) == 1:
                picking = self.purchase_id.picking_ids
            if picking:
                self.set_picking_quantities_done(picking, edoc)

        elif self.industrialization_id:
            conciliated_obj = self.industrialization_id
            edoc.industrialization_id = conciliated_obj
            self.set_picking_quantities_done(conciliated_obj, edoc)

        if conciliated_obj is not None and edoc.partner_id != conciliated_obj.partner_id:
            raise UserError(_("Os parceiros do Documento Fiscal e da Ordem de Compra/Industrialização não podem ser diferentes."))

        return res

    def set_picking_quantities_done(self, picking, edoc):
        for edoc_line in edoc.line_ids:
            flag = False
            for picking_line in picking.move_ids_without_package:
                if edoc_line.product_id == picking_line.product_id:
                    flag = True
                    picking_line.quantity_done = self.env['uom.uom'].browse(
                        edoc_line.uom_id.id)._compute_quantity(edoc_line.quantity,
                                                               picking_line.product_uom)
                    continue
            if not flag:
                raise UserError(_("A nota fiscal possui produtos que não existem na Ordem de Venda/Transferência."))
